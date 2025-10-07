import pytest
from datetime import date, timedelta
from entities import Author, Book, Reader, Copy
from library import Library

@pytest.fixture
def author():
    return Author("Sommerville", 1951)

@pytest.fixture
def books(author):
    se10_es = Book("Software Engineering", author, 2025, edition="10th", language="ES")
    se9_en = Book("Software Engineering", author, 2023, edition="9th", language="EN")
    se9_es = Book("Software Engineering", author, 2022, edition="9th", language="ES")
    se8_en = Book("Software Engineering", author, 2020, edition="8th", language="EN")
    return se10_es, se9_en, se9_es, se8_en

@pytest.fixture
def library_populated(books):
    se10_es, se9_en, se9_es, se8_en = books
    lib = Library()
    lib.add_book(se10_es)
    lib.add_book(se9_en)
    lib.add_book(se9_es)
    lib.add_book(se8_en)
    lib.add_copy(se9_en)
    lib.add_copy(se9_en)
    lib.add_copy(se9_en)
    lib.add_copy(se9_es)
    lib.add_copy(se9_es)
    lib.add_copy(se9_es)
    lib.add_copy(se9_es)
    lib.add_copy(se8_en)
    lib.add_copy(se8_en)
    lib.add_copy(se8_en)
    lib.add_copy(se8_en)
    return lib


def test_count_and_find_by_name(library_populated):
    lib = library_populated
    assert lib.count_books_by_name("Software Engineering") == len(lib.find_books_by_name("Software Engineering"))
    assert lib.count_books_by_name("Software Engineering") == 15
    assert lib.count_copies_by_name("Software Engineering") == 11

def test_count_available_with_filters(library_populated, books):
    se10_es, se9_en, se9_es, se8_en = books
    lib = library_populated
    assert lib.count_available_copies_by_name("Software Engineering") == 11
    assert lib.count_available_copies_by_name("Software Engineering", year=2023) == 3
    assert lib.count_available_copies_by_name("Software Engineering", edition="9th") == 7
    assert lib.count_available_copies_by_name("Software Engineering", language="ES") == 4

def test_find_by_author_includes_books_and_copies(library_populated):
    lib = library_populated
    found = lib.find_books_by_author("Sommerville")
    assert len(found) == 15
    assert any(repr(x).startswith("Book(") for x in found)
    assert any(repr(x).startswith("Copy(") for x in found)


def test_get_available_copy_when_there_is_one(library_populated, books):
    lib = library_populated
    _, se9_en, _, _ = books
    result = lib.get_available_copy(se9_en)
    assert "copy" in result and result["copy"].status == "available"

def test_get_available_copy_when_new_book_has_no_copies(library_populated, books):
    lib = library_populated
    se10_es, _, _, _ = books
    result = lib.get_available_copy(se10_es)
    assert "reason" in result
    assert "nuevo" in result["reason"].lower()


def test_lend_book_success(library_populated, books):
    lib = library_populated
    reader = Reader("Ana", "ana@uni.edu")
    lib.add_reader(reader)

    _, se9_en, _, _ = books
    out = lib.lend_book(se9_en, reader)

    assert "copy" in out
    cpy = out["copy"]
    assert cpy.status == "on_loan"
    assert cpy.reader_act == reader
    assert cpy.id in reader.active_loans

def test_lend_book_reader_blocked(library_populated, books):
    lib = library_populated
    reader = Reader("Bob", "bob@uni.edu", days_blocked=2)
    lib.add_reader(reader)
    _, se9_en, _, _ = books

    out = lib.lend_book(se9_en, reader)
    assert "reason" in out
    assert "bloqueo" in out["reason"].lower()

def test_lend_book_no_copies_available(library_populated, books):
    lib = library_populated
    reader = Reader("Carla", "carla@uni.edu")
    lib.add_reader(reader)
    se10_es, _, _, _ = books

    out = lib.lend_book(se10_es, reader)
    assert "reason" in out
    assert "no existen copias" in out["reason"].lower() or "no hay copias" in out["reason"].lower()

def test_validate_copies_on_loan_marks_overdue_and_blocks_reader(library_populated, books):
    lib = library_populated
    reader = Reader("Diego", "diego@uni.edu")
    lib.add_reader(reader)
    _, se9_en, _, _ = books

    cpy = lib.get_available_copy(se9_en)["copy"]
    cpy.status = "on_loan"
    cpy.reader_act = reader
    cpy.date_loan = date.today() - timedelta(days=40)
    cpy.date_expiration = date.today() - timedelta(days=10)

    blocked = lib.validate_copies_on_loan(date.today())
    assert cpy.status == "overdue"
    assert reader in blocked
    assert reader.days_blocked >= 10

def test_return_book_clears_fields(library_populated, books):
    lib = library_populated
    reader = Reader("Eva", "eva@uni.edu")
    lib.add_reader(reader)
    _, se9_en, _, _ = books

    cpy = lib.get_available_copy(se9_en)["copy"]
    cpy.status = "on_loan"
    cpy.reader_act = reader
    reader.active_loans.append(cpy.id)

    lib.return_book(cpy)
    assert cpy.status == "available"
    assert cpy.reader_act is None
    assert cpy.date_loan is None and cpy.date_expiration is None
    assert cpy.id not in reader.active_loans


def test_refresh_readers_blocked_status_unblocks_when_due():
    lib = Library()
    reader = Reader("Frank", "frank@uni.edu", days_blocked=2)
    reader.date_blocked = date.today() - timedelta(days=2)
    lib.add_reader(reader)

    lib.refresh_readers_blocked_status(date.today())
    assert reader.days_blocked == 0
    assert getattr(reader, "date_blocked", None) is None
