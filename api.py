from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from library import Library, Book
from typing import List

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

library = Library()

class BookModel(BaseModel):
    title: str
    author: str
    isbn: str

class ISBNModel(BaseModel):
    isbn: str

class BookUpdateModel(BaseModel):
    title: str
    author: str

@app.get("/", response_class=HTMLResponse)
def root():
    try:
        with open("web.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return RedirectResponse(url="/docs")

@app.get("/books", response_model=List[BookModel])
def get_books():
    return [BookModel(title=b.title, author=b.author, isbn=b.isbn) for b in library.list_books()]

@app.post("/books", response_model=BookModel)
def add_book(isbn_model: ISBNModel):
    book, error = library.add_book_by_isbn(isbn_model.isbn)
    if book:
        return BookModel(**book)
    raise HTTPException(status_code=404, detail=error or "Kitap eklenemedi.")

@app.delete("/books/{isbn}")
def delete_book(isbn: str):
    if library.remove_book(isbn):
        return {"message": "Kitap silindi."}
    raise HTTPException(status_code=404, detail="Kitap bulunamadı.")

@app.put("/books/{isbn}")
def update_book(isbn: str, book_update: BookUpdateModel):
    updated = library.update_book(isbn, book_update.title, book_update.author)
    if updated:
        return {"message": "Kitap güncellendi."}
    raise HTTPException(status_code=404, detail="Kitap bulunamadı.")
