"""HTTP/API-слой: маршруты, валидация, маппинг ошибок в коды. Запросов к БД здесь нет."""
import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Optional

from fastapi import Depends, FastAPI, Path, Query, Request, Response, status
from fastapi.responses import JSONResponse

from config import get_settings
from models import ISBN_PATTERN, Book, BookCreate, BookUpdate
from repository import (BookNotFoundError, BookRepository, DuplicateBookError,
                        MongoBookRepository, RepositoryError, StorageUnavailableError)
from service import BookService

settings = get_settings()
logging.basicConfig(level=settings.log_level,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("lab9.api")


@lru_cache
def get_repository() -> BookRepository:
    return MongoBookRepository(settings.mongodb_uri, settings.db_name, settings.timeout_ms)


def get_service(repo: BookRepository = Depends(get_repository)) -> BookService:
    return BookService(repo)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Недоступная БД при старте не должна ронять сервис
    try:
        repo = get_repository()
        if hasattr(repo, "ensure_indexes"):
            repo.ensure_indexes()
    except RepositoryError:
        log.warning("Storage not available at startup; will retry on requests")
    yield


app = FastAPI(title="Library API (Lab 9, variant 9)", lifespan=lifespan)

IsbnPath = Path(pattern=ISBN_PATTERN, description="ISBN-13 с дефисами, напр. 978-5-17-100001-1")


# ---------- маппинг доменных ошибок -> HTTP ----------
def _err(code: int, msg: str) -> JSONResponse:
    return JSONResponse(status_code=code, content={"detail": msg})


@app.exception_handler(BookNotFoundError)
async def _not_found(_: Request, __: BookNotFoundError):
    return _err(404, "Book not found")


@app.exception_handler(DuplicateBookError)
async def _duplicate(_: Request, __: DuplicateBookError):
    return _err(409, "Book with this ISBN already exists")


@app.exception_handler(StorageUnavailableError)
async def _unavailable(_: Request, __: StorageUnavailableError):
    return _err(503, "Storage temporarily unavailable")


@app.exception_handler(RepositoryError)
async def _storage(_: Request, __: RepositoryError):
    return _err(500, "Internal server error")


@app.exception_handler(Exception)
async def _unexpected(_: Request, exc: Exception):
    log.exception("Unhandled error")  # детали только в серверный лог
    return _err(500, "Internal server error")


# ---------- endpoints ----------
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, svc: BookService = Depends(get_service)):
    return svc.add_book(data)


@app.get("/books/{isbn}", response_model=Book)
def get_book(isbn: str = IsbnPath, svc: BookService = Depends(get_service)):
    return svc.get_book(isbn)


@app.get("/books", response_model=list[Book])
def search_books(
    author: Optional[str] = Query(None, min_length=1, max_length=100, description="Подстрока имени автора"),
    category: Optional[str] = Query(None, min_length=1, max_length=50),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    svc: BookService = Depends(get_service),
):
    return svc.search_books(author, category, skip, limit)


@app.patch("/books/{isbn}", response_model=Book)
def update_book(data: BookUpdate, isbn: str = IsbnPath, svc: BookService = Depends(get_service)):
    return svc.update_book(isbn, data)


@app.delete("/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(isbn: str = IsbnPath, svc: BookService = Depends(get_service)):
    svc.remove_book(isbn)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health")
def health(repo: BookRepository = Depends(get_repository)):
    repo.ping()  # при недоступной БД -> 503 через handler
    return {"status": "ok"}
