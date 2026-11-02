# Лабораторная работа № 9. Вариант 9 — Библиотека (MongoDB + FastAPI)

Хранилище: MongoDB, драйвер `pymongo`. Repository: `BookRepository`.
Сценарий: CRUD книги + поиск по автору/категории.

## Схема слоёв
```
HTTP -> main.py (API, валидация, коды) -> service.py -> repository.py -> pymongo -> MongoDB
HTTP <- маппинг ошибок <- доменный результат / доменные исключения <-
```
| Слой | Ответственность | Не делает |
|---|---|---|
| main.py | HTTP, валидация пути/query, коды, маппинг ошибок | запросы к БД |
| models.py | схемы Pydantic (422 при неверных данных) | — |
| service.py | оркестрация сценариев | знает про HTTP и драйвер |
| repository.py | запросы, индексы, перевод ошибок драйвера в доменные | знает про HTTP |
| config.py | URI, имя БД, timeout из env | хранит секреты в коде |

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # при необходимости поправьте значения
docker run -d --name mongo9 -p 127.0.0.1:27017:27017 mongo:7   # порт только на localhost
python seed.py                                       # 18 синтетических книг
uvicorn main:app --reload                            # Swagger: http://127.0.0.1:8000/docs
pytest -q                                            # тесты без БД (fake repository)
```

## Контракт API
| Операция | Метод и путь | Успех | Ошибки |
|---|---|---|---|
| Создать | POST /books | 201 | 422 валидация, 409 дубликат ISBN, 503 |
| Получить | GET /books/{isbn} | 200 | 404, 422 (формат ISBN), 503 |
| Список/поиск | GET /books?author=&category=&skip=&limit= | 200 | 422, 503 |
| Изменить | PATCH /books/{isbn} | 200 | 404, 422 (в т.ч. пустое тело), 503 |
| Удалить | DELETE /books/{isbn} | 204 | 404, 422, 503 |
| Проверка | GET /health | 200 | 503 |

Любая непредвиденная ошибка → 500 `Internal server error`; подробности только в логе.

## Примеры curl
```bash
curl -i -X POST localhost:8000/books -H "Content-Type: application/json" \
  -d '{"isbn":"978-5-17-200001-1","title":"Новая книга","author":"Иван Петров","category":"Информатика","year":2024,"copies":3}'
curl -i localhost:8000/books/978-5-17-100001-1
curl -i "localhost:8000/books?author=петров"
curl -i "localhost:8000/books?category=Детектив&limit=5"
curl -i -X PATCH localhost:8000/books/978-5-17-100001-1 -H "Content-Type: application/json" -d '{"copies":10}'
curl -i -X DELETE localhost:8000/books/978-5-17-100001-1
curl -i localhost:8000/books/978-5-17-999999-9        # 404
curl -i localhost:8000/books/abc                      # 422
docker stop mongo9 && curl -i localhost:8000/books    # 503, сервис не падает
```

## Что скрывает repository
URI и клиент MongoClient, таймауты, имя коллекции, проекцию `{_id: 0}`, синтаксис `$regex/$set`
и `re.escape`, уникальный индекс по `isbn`, типы исключений pymongo (переводятся в
`BookNotFoundError`, `DuplicateBookError`, `StorageUnavailableError`, `StorageError`).

## Что заменить при смене хранилища
Только `MongoBookRepository` (и `config.py`). API, service и модели не меняются, пока соблюдён
протокол `BookRepository`.

## Безопасность
`.env` в `.gitignore`; в `.env.example` только имена и локальные значения; клиент не видит stack trace
и URI; данные синтетические; порт MongoDB привязан к 127.0.0.1.

## Ответы на контрольные вопросы (кратко)
1. Драйвер — библиотека, устанавливающая соединение и выполняющая операции СУБД (pymongo).
2. Repository изолирует детали хранения: проще тестировать, менять БД, обрабатывать ошибки.
3. URI содержит логин/пароль: репозиторий Git читают многие, история хранит секрет навсегда.
4. Валидация HTTP — в API-слое (Pydantic, Path/Query).
5. 404 — ресурса нет (штатный случай); 503 — сервис/хранилище временно недоступно.
6. HTTP — забота API; иначе repository нельзя использовать вне веба и тестировать отдельно.
7. Задать `serverSelectionTimeoutMS` / `connectTimeoutMS` / `socketTimeoutMS`, ловить `ConnectionFailure` → `StorageUnavailableError` → 503.
8. `$regex`-поиск по автору, `$set`-обновление, уникальный индекс, проекция, сортировка/пагинация.
9. Новая реализация протокола `BookRepository` и конфигурация; плюс перевод ошибок нового драйвера.
10. Ошибки драйвера, stack trace, детали подключения, неожиданные исключения (500).

## Шаблон отчёта (что вставить)
1. Тема и вариант (9, Библиотека, MongoDB).  2. Схема слоёв (выше).  3. Драйвер pymongo.
4. Структура проекта.  5. Repository (протокол + Mongo + fake).  6. Контракт API (таблица).
7. Скриншоты успешных запросов (POST/GET/PATCH/DELETE/поиск).  8. Скриншоты 404 и 422.
9. Скриншот 503 при остановленной БД + лог сервиса.  10. Конфигурация без секретов (.env.example).
11. Анализ ошибок и вывод.
