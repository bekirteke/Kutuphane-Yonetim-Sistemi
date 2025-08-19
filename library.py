import json
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List, Optional

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

    def to_dict(self):
        return {"title": self.title, "author": self.author, "isbn": self.isbn}

    @staticmethod
    def from_dict(data):
        return Book(isbn=data["isbn"], title=data["title"], author=data["author"])

class Library:
    def __init__(self, db_url: str = "sqlite:///library.db"):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_book(self, book: Book):
        with self.Session() as session:
            if session.get(Book, book.isbn):
                raise ValueError("Bu ISBN ile bir kitap zaten var.")
            session.add(book)
            session.commit()

    def remove_book(self, isbn: str):
        with self.Session() as session:
            book = session.get(Book, isbn)
            if book:
                session.delete(book)
                session.commit()
                return True
            return False

    def list_books(self) -> List[Book]:
        with self.Session() as session:
            return session.query(Book).all()

    def find_book(self, isbn: str) -> Optional[Book]:
        with self.Session() as session:
            return session.get(Book, isbn)

    def update_book(self, isbn: str, title: str, author: str):
        with self.Session() as session:
            book = session.get(Book, isbn)
            if book:
                book.title = title
                book.author = author
                session.commit()
                return True
            return False

    # Open Library API ile kitap ekleme fonksiyonu (değişmedi)
    def add_book_by_isbn(self, isbn: str):
        import httpx
        # Normalize ISBN: remove spaces and hyphens
        isbn = (isbn or "").replace(" ", "").replace("-", "").strip()
        url = f"https://openlibrary.org/isbn/{isbn}.json"
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            if response.status_code == 404:
                return None, "Kitap bulunamadı."
            response.raise_for_status()
            data = response.json()
            title = data.get("title", "Bilinmiyor")
            authors = data.get("authors", [])
            author_names = []
            for author in authors:
                key = author.get("key")
                if key:
                    author_url = f"https://openlibrary.org{key}.json"
                    try:
                        author_resp = httpx.get(author_url, timeout=10, follow_redirects=True)
                        if author_resp.status_code == 200:
                            author_data = author_resp.json()
                            author_names.append(author_data.get("name", "Bilinmiyor"))
                        else:
                            author_names.append("Bilinmiyor")
                    except Exception:
                        author_names.append("Bilinmiyor")
                else:
                    author_names.append("Bilinmiyor")
            author_str = ", ".join(author_names) if author_names else "Bilinmiyor"
            book = Book(isbn=isbn, title=title, author=author_str)
            self.add_book(book)
            # Dönmeden önce verileri kopyala!
            return {"isbn": isbn, "title": title, "author": author_str}, None
        except httpx.RequestError:
            return None, "İnternet bağlantısı yok veya API'ye ulaşılamıyor."
        except Exception as e:
            return None, f"Beklenmeyen hata: {e}"
