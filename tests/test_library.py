import os
import pytest
from library import Book, Library

def test_add_and_find_book(tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    book = Book("Test Kitap", "Test Yazar", "1234567890")
    lib.add_book(book)
    found = lib.find_book("1234567890")
    assert found is not None
    assert found.title == "Test Kitap"
    assert found.author == "Test Yazar"
    assert found.isbn == "1234567890"

def test_remove_book(tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    book = Book("Test Kitap", "Test Yazar", "1234567890")
    lib.add_book(book)
    assert lib.remove_book("1234567890")
    assert lib.find_book("1234567890") is None

def test_list_books(tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    book1 = Book("Kitap1", "Yazar1", "111")
    book2 = Book("Kitap2", "Yazar2", "222")
    lib.add_book(book1)
    lib.add_book(book2)
    books = lib.list_books()
    assert len(books) == 2
    assert books[0].isbn == "111"
    assert books[1].isbn == "222"

def test_duplicate_isbn(tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    book = Book("Kitap", "Yazar", "999")
    lib.add_book(book)
    with pytest.raises(ValueError):
        lib.add_book(Book("Başka Kitap", "Başka Yazar", "999"))

def test_add_book_by_isbn_success(monkeypatch, tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    # Mock httpx.get
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json = json_data
            self.status_code = status_code
        def json(self):
            return self._json
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP error")
    def mock_get(url, timeout=10):
        if url.startswith("https://openlibrary.org/isbn/"):
            return MockResponse({"title": "Mock Kitap", "authors": [{"key": "/authors/OL123A"}]})
        elif url.startswith("https://openlibrary.org/authors/OL123A.json"):
            return MockResponse({"name": "Mock Yazar"})
        return MockResponse({}, 404)
    monkeypatch.setattr("httpx.get", mock_get)
    book, error = lib.add_book_by_isbn("0000000000")
    assert error is None
    assert book is not None
    assert book.title == "Mock Kitap"
    assert book.author == "Mock Yazar"
    assert book.isbn == "0000000000"

def test_add_book_by_isbn_not_found(monkeypatch, tmp_path):
    test_file = tmp_path / "test_library.json"
    lib = Library(str(test_file))
    class MockResponse:
        def __init__(self, status_code=404):
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP error")
        def json(self):
            return {}
    def mock_get(url, timeout=10):
        return MockResponse(404)
    monkeypatch.setattr("httpx.get", mock_get)
    book, error = lib.add_book_by_isbn("notfound")
    assert book is None
    assert error == "Kitap bulunamadı."
