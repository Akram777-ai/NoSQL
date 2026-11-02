"""Слой доступа к данным.

Repository НЕ знает про HTTP: он возвращает доменные данные или бросает
доменные исключения. Только этот модуль зависит от драйвера pymongo.
"""
import logging
import re
from functools import wraps
from typing import Optional, Protocol

from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError

log = logging.getLogger("lab9.repository")


# ---------- доменные ошибки ----------
class RepositoryError(Exception):
    """Базовая ошибка хранилища."""


class BookNotFoundError(RepositoryError):
    pass


class DuplicateBookError(RepositoryError):
    pass


class StorageUnavailableError(RepositoryError):
    """БД недоступна (timeout / нет соединения)."""


class StorageError(RepositoryError):
    """Прочая ошибка хранилища."""


# ---------- интерфейс ----------
class BookRepository(Protocol):
    def create(self, book: dict) -> dict: ...
    def get(self, isbn: str) -> dict: ...
    def list(self, author: Optional[str] = None, category: Optional[str] = None,
             skip: int = 0, limit: int = 20) -> list[dict]: ...
    def update(self, isbn: str, changes: dict) -> dict: ...
    def delete(self, isbn: str) -> None: ...
    def ping(self) -> None: ...


# ---------- реализация на MongoDB ----------
def _map_errors(func):
    """Переводит исключения драйвера в доменные (детали драйвера наружу не уходят)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RepositoryError:
            raise
        except DuplicateKeyError as exc:
            raise DuplicateBookError("Book with this ISBN already exists") from exc
        except ConnectionFailure as exc:  # включает ServerSelectionTimeoutError
            log.error("MongoDB unavailable: %s", type(exc).__name__)
            raise StorageUnavailableError("Storage unavailable") from exc
        except PyMongoError as exc:
            log.exception("MongoDB error")
            raise StorageError("Storage error") from exc
    return wrapper


class MongoBookRepository:
    def __init__(self, uri: str, db_name: str, timeout_ms: int = 3000):
        self.client = MongoClient(
            uri,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=timeout_ms,
            socketTimeoutMS=timeout_ms,
        )
        self.col = self.client[db_name]["books"]

    @_map_errors
    def ensure_indexes(self) -> None:
        self.col.create_index("isbn", unique=True)
        self.col.create_index([("author", ASCENDING)])
        self.col.create_index([("category", ASCENDING)])

    @_map_errors
    def ping(self) -> None:
        self.client.admin.command("ping")

    @_map_errors
    def create(self, book: dict) -> dict:
        self.col.insert_one(dict(book))  # копия: insert_one добавляет _id
        return self.get(book["isbn"])

    @_map_errors
    def get(self, isbn: str) -> dict:
        doc = self.col.find_one({"isbn": isbn}, {"_id": 0})
        if doc is None:
            raise BookNotFoundError(isbn)
        return doc

    @_map_errors
    def list(self, author=None, category=None, skip=0, limit=20) -> list[dict]:
        query: dict = {}
        if author:
            # регистронезависимый поиск по подстроке; re.escape защищает от regex-инъекций
            query["author"] = {"$regex": re.escape(author), "$options": "i"}
        if category:
            query["category"] = category
        cursor = (self.col.find(query, {"_id": 0})
                  .sort("title", ASCENDING).skip(skip).limit(limit))
        return list(cursor)

    @_map_errors
    def update(self, isbn: str, changes: dict) -> dict:
        doc = self.col.find_one_and_update(
            {"isbn": isbn}, {"$set": changes},
            projection={"_id": 0}, return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise BookNotFoundError(isbn)
        return doc

    @_map_errors
    def delete(self, isbn: str) -> None:
        if self.col.delete_one({"isbn": isbn}).deleted_count == 0:
            raise BookNotFoundError(isbn)


# ---------- in-memory fake для тестов ----------
class InMemoryBookRepository:
    def __init__(self):
        self._data: dict[str, dict] = {}

    def ping(self) -> None:
        return None

    def create(self, book: dict) -> dict:
        if book["isbn"] in self._data:
            raise DuplicateBookError(book["isbn"])
        self._data[book["isbn"]] = dict(book)
        return dict(book)

    def get(self, isbn: str) -> dict:
        if isbn not in self._data:
            raise BookNotFoundError(isbn)
        return dict(self._data[isbn])

    def list(self, author=None, category=None, skip=0, limit=20) -> list[dict]:
        items = sorted(self._data.values(), key=lambda b: b["title"])
        if author:
            items = [b for b in items if author.lower() in b["author"].lower()]
        if category:
            items = [b for b in items if b["category"] == category]
        return [dict(b) for b in items[skip:skip + limit]]

    def update(self, isbn: str, changes: dict) -> dict:
        if isbn not in self._data:
            raise BookNotFoundError(isbn)
        self._data[isbn].update(changes)
        return dict(self._data[isbn])

    def delete(self, isbn: str) -> None:
        if isbn not in self._data:
            raise BookNotFoundError(isbn)
        del self._data[isbn]
