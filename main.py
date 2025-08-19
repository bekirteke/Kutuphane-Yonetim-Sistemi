from library import Book, Library

def main():
    library = Library()
    while True:
        print("\n--- Kütüphane Uygulaması ---")
        print("1. Kitap Ekle")
        print("2. Kitap Sil")
        print("3. Kitapları Listele")
        print("4. Kitap Ara")
        print("5. Çıkış")
        choice = input("Seçiminiz: ")

        if choice == "1":
            isbn = input("ISBN: ")
            isbn = (isbn or "").replace(" ", "").replace("-", "").strip()
            book, error = library.add_book_by_isbn(isbn)
            if book:
                print(f"Kitap eklendi: {book['title']} by {book['author']} (ISBN: {book['isbn']})")
            else:
                print(error)
        elif choice == "2":
            isbn = input("Silinecek kitabın ISBN'i: ")
            isbn = (isbn or "").replace(" ", "").replace("-", "").strip()
            if library.remove_book(isbn):
                print("Kitap silindi!")
            else:
                print("Kitap bulunamadı.")
        elif choice == "3":
            books = library.list_books()
            if not books:
                print("Kütüphanede hiç kitap yok.")
            else:
                for book in books:
                    print(f"{book.title} by {book.author} (ISBN: {book.isbn})")
        elif choice == "4":
            isbn = input("Aranacak kitabın ISBN'i: ")
            isbn = (isbn or "").replace(" ", "").replace("-", "").strip()
            book = library.find_book(isbn)
            if book:
                print(f"{book.title} by {book.author} (ISBN: {book.isbn})")
            else:
                print("Kitap bulunamadı.")
        elif choice == "5":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()
