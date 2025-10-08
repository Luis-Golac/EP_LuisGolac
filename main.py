from library import Library
from entities import Book, Author

from datetime import date

name = "Software Engineering"

somerville = Author("Sommerville", date(1951, 2, 23))
se10_es = Book(
    name, somerville, 2025, edition="10th", language="ES"
)
se9_en = Book(
    name, somerville, 2023, edition="9th", language="EN"
)
se9_es = Book(
    name, somerville, 2022, edition="9th", language="ES"
)
se8_en = Book(
    name, somerville, 2020, edition="8th", language="EN"
)

library = Library()
library.add_book(se10_es)
library.add_book(se9_en)
library.add_book(se9_es)
library.add_book(se8_en)
library.add_copy(se9_en)
library.add_copy(se9_en)
library.add_copy(se9_en)
library.add_copy(se9_es)
library.add_copy(se9_es)
library.add_copy(se9_es)
library.add_copy(se9_es)
library.add_copy(se8_en)
library.add_copy(se8_en)
library.add_copy(se8_en)
library.add_copy(se8_en)

print(library.count_books_by_author("Sommerville"))
