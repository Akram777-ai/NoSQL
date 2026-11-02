"""Тонкий service-слой: оркестрирует repository, не знает ни HTTP, ни драйвера."""
from typing import Optional

from models import BookCreate, BookUpdate
from repository import BookRepository


class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def add_book(self, data: BookCreate) -> dict:
        return self.repo.create(data.model_dump())

    def get_book(self, isbn: str) -> dict:
        return self.repo.get(isbn)

    def search_books(self, author: Optional[str], category: Optional[str],
                     skip: int, limit: int) -> list[dict]:
        return self.repo.list(author=author, category=category, skip=skip, limit=limit)

    def update_book(self, isbn: str, data: BookUpdate) -> dict:
        return self.repo.update(isbn, data.model_dump(exclude_unset=True))

    def remove_book(self, isbn: str) -> None:
        self.repo.delete(isbn)
