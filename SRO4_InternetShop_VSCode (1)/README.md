# СРО №4 — Заказы интернет-магазина (MongoDB + Python)

**Вариант 4:** заказы со встроенными позициями, snapshot цены и аналитика выручки по категориям.

## Запуск в VS Code (Windows, PowerShell)
1. Убедитесь, что локальный MongoDB Server запущен (`mongodb://localhost:27017/`). MongoDB Compass — GUI-клиент и сам по себе не запускает сервер.
2. Откройте папку `SRO4_InternetShop` через File → Open Folder в VS Code.
3. В терминале VS Code выполните:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m scripts.seed
python -m src.main demo
python -m unittest discover -s tests -v
```

Если PowerShell запрещает Activate.ps1, запускайте `.\.venv\Scripts\python.exe` вместо `python` в командах (без активации). Для использования `.env` значения перенесите в переменные окружения PowerShell: `$env:MONGODB_URI="mongodb://localhost:27017/"`; `$env:MONGODB_DB="sro4_shop"`. Файл `.env` здесь является образцом конфигурации, автоматически не загружается.

## CRUD
```powershell
python -m src.main create --id DEMO-1000
python -m src.main get --id DEMO-1000
python -m src.main update --id DEMO-1000 --status delivered
python -m src.main get --id DEMO-1000
python -m src.main delete --id DEMO-1000
```

## Восемь запросов
```powershell
python -m src.main query --number 1
python -m src.main query --number 2
python -m src.main query --number 3
python -m src.main query --number 4
python -m src.main query --number 5
python -m src.main query --number 6
python -m src.main query --number 7
python -m src.main query --number 8
```

Q1 заказы клиента; Q2 детали заказа; Q3 заказы по статусу; Q4 заказы за период; Q5 сумма оплаченных заказов клиента; Q6 выручка по категориям (aggregation `$unwind/$group`); Q7 самые продаваемые товары; Q8 выручка по дням.

**Правило выручки:** заказы со статусом `paid`, `shipped`, `delivered` учитываются; `new` и `cancelled` не учитываются. Все суммы представлены целыми тенге (KZT), цены товаров фиксируются в `items` на момент оформления.

## Состав
- `src/` — бизнес-логика, MongoDB, запросы, консольное управление
- `scripts/seed.py` — 36 синтетических заказов; повторный запуск обновляет эти же 36 ID
- `tests/` — 7 автономных unit-тестов; для запуска тестов сервер MongoDB не нужен
- `docs/ADR.md` — выбор технологии, ограничения, архитектура
- `docs/architecture.svg` — диаграмма архитектуры
- `docs/report.pdf` — отчёт для дополнения скриншотами реального запуска

## Проверка в MongoDB Compass
Подключение `mongodb://localhost:27017` → база `sro4_shop` → коллекция `orders`. После запуска seed в пустой базе должно быть 36 документов. Чтобы увидеть аналитический запрос, в Compass можно выбрать Aggregations, но основная демонстрация делается через Python CLI.

## Проверка перед защитой
Приложите реальные скриншоты `seed`, `demo`, CRUD, 7 unit-тестов и MongoDB Compass. На GitHub залейте все файлы кроме `.env`, `.venv` и `__pycache__`. Презентация готовится отдельно.
