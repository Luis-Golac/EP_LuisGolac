from entities import (
    Book,
    Author,
    Reader,
    Copy,
    BioAlert,
)

from datetime import date

class Library:
    def __init__(self):
        self.books: list[Book] = []
        self.copies: dict[str, Copy] = {}
        self.readers: dict[str, Reader] = {}
        self.bioalert: BioAlert = BioAlert(subscribers=[])

    def add_book(
        self,
        book: Book,
    ):
        self.books.append(book)

    def add_copy(
        self,
        book: Book,
    ):
        copy: Copy = Copy(
            book=book,
            status="available",
        )
        self.copies[copy.id] = copy

    def add_reader(
        self,
        reader: Reader,
    ):
        self.readers[reader.id] = reader

    def find_books_by_name(
        self,
        name: str,
    ) -> list[Book | Copy]:
        found_books: list[Book | Copy] = []

        for book in self.books:
            if book.name.lower() == name.lower():
                found_books.append(book)

        for copy in self.copies.values():
            if copy.book.name.lower() == name.lower():
                found_books.append(copy)

        return found_books

    def count_books_by_name(
        self,
        name: str,
    ) -> int:
        return len(self.find_books_by_name(name))

    def count_copies_by_name(
        self,
        name: str,
        year: int = None,
        edition: str = None,
        language: str = None,
    ) -> int:
        count: int = 0

        for copy in self.copies.values():
            if copy.book.name.lower() == name.lower():
                if year is not None and copy.book.year != year:
                    continue
                if edition is not None and copy.book.edition != edition:
                    continue
                if language is not None and copy.book.language != language:
                    continue
                count += 1

        return count

    def count_available_copies_by_name(
        self,
        name: str,
        year: int = None,
        edition: str = None,
        language: str = None,
    ) -> int:
        count: int = 0

        for copy in self.copies.values():
            if copy.book.name.lower() == name.lower() and copy.status == "available":
                if year is not None and copy.book.year != year:
                    continue
                if edition is not None and copy.book.edition != edition:
                    continue
                if language is not None and copy.book.language != language:
                    continue
                count += 1

        return count

    def find_books_by_author(
        self,
        name: str,
    ) -> list[Book | Copy]:
        found_books: list[Book | Copy] = []

        for book in self.books:
            if book.author.name.lower() == name.lower():
                found_books.append(book)

        for copy in self.copies.values():
            if copy.book.author.name.lower() == name.lower():
                found_books.append(copy)

        return found_books

    def count_books_by_author(
        self,
        name: str,
    ) -> int:
        return len(self.find_books_by_author(name))

    def get_available_copy(
        self,
        book: Book,
    ) -> Copy | None:
        result: dict[str, str | Copy] = {}
        reason: str = ""
        for copy in self.copies.values():
            if copy.book == book and copy.status == "available":
                result["copy"] = copy

        if "copy" not in result:
            if self.count_copies_by_name(
                book.name,
                book.year,
                book.edition,
                book.language,
            ) == 0:
                reason = "El libro es nuevo, no existen copias en la biblioteca."
            else:
                reason = "No hay copias disponibles en este momento."

            result["reason"] = reason

        return result

    def lend_book(
        self,
        book: Book,
        reader: Reader,
    ) -> dict[str, str | Copy]:
        result: dict[str, Copy | str] = {}
        reason: str = ""

        if reader.days_blocked > 0:
            reason = f"El lector tiene {reader.days_blocked} días de bloqueo."
            result["reason"] = reason
            return result

        available_copy = self.get_available_copy(book)

        if "reason" in available_copy:
            result["reason"] = available_copy["reason"]
            return result

        copy: Copy = available_copy["copy"]
        copy.status = "on_loan"
        copy.reader_act = reader
        reader.active_loans.append(copy.id)

        result["copy"] = copy
        return result

    def validate_copies_on_loan(
        self,
        current_date: date,
    ) -> list[Reader]:
        blocked_readers: list[Reader] = []

        for copy in self.copies.values():
            copy: Copy
            copy.refresh_status(current_date)

            if copy.status == "overdue":
                reader: Reader = copy.reader_act
                blocked_readers.append(reader)

        return blocked_readers

    def refresh_readers_blocked_status(
        self,
        current_date: date,
    ) -> None:
        for reader in self.readers.values():
            reader: Reader
            reader.refresh_block_status(current_date)

    def return_book(
        self,
        copy: Copy,
    ) -> None:
        reader: Reader = copy.reader_act
        reader.active_loans.remove(copy.id)

        copy.status = "available"
        copy.reader_act = None
        copy.date_loan = None
        copy.date_expiration = None

    def subscribe_bioalert(
        self,
        reader: Reader,
        book: Book,
    ) -> None:
        self.bioalert.suscribe(reader.id, book)

    def unsubscribe_bioalert(
        self,
        reader: Reader,
    ) -> None:
        self.bioalert.unsuscribe(reader.id)
