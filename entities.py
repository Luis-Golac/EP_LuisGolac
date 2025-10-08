from uuid import UUID, uuid4
from datetime import date

class Author:
    def __init__(self, name: str, birth_year: int):
        self.name = name
        self.birth_year = birth_year


class Reader:
    def __init__(
        self,
        name: str,
        email: str,
        active_loans: list[UUID] = None,
        date_blocked: date = None,
        days_blocked: int = 0,
    ):
        self.id = uuid4()
        self.name = name
        self.email = email
        if active_loans is None:
            self.active_loans = []
        else:
            self.active_loans = active_loans
        self.days_blocked = days_blocked

    def __repr__(self):
        return f"Reader(id={self.id}, name={self.name}, email={self.email})"

    def refresh_block_status(self, today: date):
        if self.date_blocked and (today - self.date_blocked).days >= self.days_blocked:
            self.days_blocked = 0
            self.date_blocked = None

class Book:
    def __init__(
        self,
        name: str,
        author: Author,
        year: int,
        edition: str = None,
        language: str = None,
        status: str = "available",
        reader_act: Reader = None,
        date_loan: date = None,
        date_expiration: date = None,
    ):
        self.name = name
        self.author = author
        self.year = year
        self.edition = edition
        self.language = language
        self.reader_act = reader_act
        self.date_loan = date_loan
        self.date_expiration = date_expiration

    def refresh_status(self, today: date):
        if self.status == "on_loan" and self.date_expiration and today > self.date_expiration:
            self.status = "overdue"
            if self.reader_act:
                self.reader_act.days_blocked += (today - self.date_expiration).days

    def __repr__(self):
        return f"Book(name={self.name}, author={self.author.name}, year={self.year})"

class Copy:
    def __init__(
        self,
        book: Book,
        status: str = "available",
        reader_act: Reader = None,
        date_loan: date = None,
        date_expiration: date = None,
    ):
        self.id = uuid4()
        self.book = book
        self.status = status
        self.reader_act = reader_act
        self.date_loan = date_loan
        self.date_expiration = date_expiration

    def refresh_status(self, today: date):
        if self.status == "on_loan" and self.date_expiration and today > self.date_expiration:
            self.status = "overdue"
            if self.reader_act:
                self.reader_act.days_blocked += (today - self.date_expiration).days

    def __repr__(self):
        return f"Copy(id={self.id}, book={self.book.name}, status={self.status})"


class BioAlert:
    def __init__(self, subscribers: dict[Book, UUID]):
        self.subscribers = subscribers

    def suscribe(self, reader_id: UUID, book: Book):
        if reader_id not in self.subscribers:
            self.subscribers[book] = reader_id

    def unsubscribe(self, reader_id: UUID):
        self.subscribers = {
            book: r_id
            for book, r_id in self.subscribers.items()
            if r_id != reader_id
        }

    def next_subscriber(self, book: Book) -> UUID | None:
        act = self.subscribers.get(book, [])
        if act:
            return act.pop(0)

        return None
