import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_get_books_empty(monkeypatch):
    # Kütüphane boşsa boş liste dönmeli
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_post_books_success(monkeypatch):
    # API çağrısı mocklanacak
    from library import Library
    def mock_add_book_by_isbn(self, isbn):
        class DummyBook:
            def __init__(self, isbn):
                self.title = "API Kitap"
                self.author = "API Yazar"
                self.isbn = isbn
        return DummyBook(isbn), None
    monkeypatch.setattr(Library, "add_book_by_isbn", mock_add_book_by_isbn)
    response = client.post("/books", json={"isbn": "1234567890"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API Kitap"
    assert data["author"] == "API Yazar"
    assert data["isbn"] == "1234567890"

def test_post_books_not_found(monkeypatch):
    from library import Library
    def mock_add_book_by_isbn(self, isbn):
        return None, "Kitap bulunamadı."
    monkeypatch.setattr(Library, "add_book_by_isbn", mock_add_book_by_isbn)
    response = client.post("/books", json={"isbn": "notfound"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Kitap bulunamadı."

def test_delete_book(monkeypatch):
    from library import Library
    def mock_remove_book(self, isbn):
        return isbn == "123"
    monkeypatch.setattr(Library, "remove_book", mock_remove_book)
    response = client.delete("/books/123")
    assert response.status_code == 200
    assert response.json()["message"] == "Kitap silindi."
    response = client.delete("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Kitap bulunamadı."

def test_put_books_update(monkeypatch):
    from library import Library
    def mock_update_book(self, isbn, title, author):
        if isbn == "123":
            return True
        return False
    monkeypatch.setattr(Library, "update_book", mock_update_book)
    response = client.put("/books/123", json={"title": "Yeni Başlık", "author": "Yeni Yazar"})
    assert response.status_code == 200
    assert response.json()["message"] == "Kitap güncellendi."
    response = client.put("/books/999", json={"title": "X", "author": "Y"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Kitap bulunamadı."
