"""Тесты HTTP-слоя БЕЗ запущенной СУБД: репозиторий подменяется fake через DI."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import app, get_repository
from repository import InMemoryBookRepository, StorageUnavailableError

BOOK = {"isbn": "978-5-17-100001-1", "title": "Основы баз данных",
        "author": "Иван Петров", "category": "Информатика", "year": 2019, "copies": 5}


class BrokenRepository(InMemoryBookRepository):
    """Имитация остановленной СУБД."""
    def _fail(self, *a, **k):
        raise StorageUnavailableError("down")
    create = get = list = update = delete = ping = _fail


@pytest.fixture
def client():
    repo = InMemoryBookRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_and_get(client):
    assert client.post("/books", json=BOOK).status_code == 201
    r = client.get(f"/books/{BOOK['isbn']}")
    assert r.status_code == 200 and r.json()["title"] == BOOK["title"]


def test_not_found_404(client):
    assert client.get("/books/978-5-17-999999-9").status_code == 404


def test_duplicate_409(client):
    client.post("/books", json=BOOK)
    assert client.post("/books", json=BOOK).status_code == 409


def test_validation_422(client):
    bad = {**BOOK, "year": 1200}
    assert client.post("/books", json=bad).status_code == 422
    assert client.post("/books", json={"title": "x"}).status_code == 422
    assert client.get("/books/abc").status_code == 422          # плохой ISBN
    assert client.patch(f"/books/{BOOK['isbn']}", json={}).status_code == 422


def test_search_by_author_and_category(client):
    client.post("/books", json=BOOK)
    client.post("/books", json={**BOOK, "isbn": "978-5-17-100006-6", "title": "Тихая гавань",
                                "author": "Ольга Ветрова", "category": "Роман"})
    assert len(client.get("/books", params={"author": "петров"}).json()) == 1
    assert len(client.get("/books", params={"category": "Роман"}).json()) == 1
    assert len(client.get("/books").json()) == 2


def test_patch_and_delete(client):
    client.post("/books", json=BOOK)
    r = client.patch(f"/books/{BOOK['isbn']}", json={"copies": 2})
    assert r.status_code == 200 and r.json()["copies"] == 2
    assert client.delete(f"/books/{BOOK['isbn']}").status_code == 204
    assert client.delete(f"/books/{BOOK['isbn']}").status_code == 404


def test_storage_down_503_without_secrets():
    app.dependency_overrides[get_repository] = lambda: BrokenRepository()
    c = TestClient(app)
    r = c.get(f"/books/{BOOK['isbn']}")
    app.dependency_overrides.clear()
    assert r.status_code == 503
    assert "mongodb" not in r.text.lower() and "down" not in r.text
