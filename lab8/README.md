# Лабораторная работа 8 — Реестр лабораторных работ (вариант 1)

Требования: PHP 8.4+, расширение Fileinfo (`php -m | grep -i fileinfo`).

```
php -S localhost:8000 -t public
bash tests/run_tests.sh      # автотесты T1–T12 (при запущенном сервере)
```

Каталог `var/` должен быть доступен PHP на запись и не должен отдаваться веб-сервером
(при `php -S -t public` это выполняется автоматически, т.к. корень — `public/`).
Для теста лимитов проверьте `php -i | grep -E "upload_max_filesize|post_max_size"` (≥ 6M).
Запуск сервера с нужными лимитами:
`php -d upload_max_filesize=6M -d post_max_size=8M -S localhost:8000 -t public`
