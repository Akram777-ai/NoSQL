<?php
declare(strict_types=1);

require dirname(__DIR__) . '/src/functions.php';

try {
    $items = loadMetadata();
} catch (Throwable $e) {
    error_log($e->__toString());
    $items = [];
}

// Вариант 1: сортировка по дате загрузки (новые сверху)
usort($items, static fn(array $a, array $b): int =>
    strcmp((string) ($b['uploaded_at'] ?? ''), (string) ($a['uploaded_at'] ?? '')));

$messages = [
    'nofile'     => 'Файл не выбран.',
    'size'       => 'Файл превышает допустимый размер (5 МиБ) или пуст.',
    'type'       => 'Разрешены только файлы PDF.',
    'partial'    => 'Файл получен не полностью. Повторите загрузку.',
    'discipline' => 'Укажите дисциплину (от 2 до 100 символов).',
    'field'      => 'Некорректный запрос.',
    'internal'   => 'Внутренняя ошибка. Попробуйте позже.',
];
$errorKey = isset($_GET['error']) && is_string($_GET['error']) ? $_GET['error'] : null;
?>
<!doctype html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Реестр лабораторных работ</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem}
 table{border-collapse:collapse;width:100%;margin-top:1.5rem}
 th,td{border:1px solid #ccc;padding:.4rem .6rem;text-align:left}
 .ok{color:#0a6b2d}.err{color:#b00020}
 form>*{margin-right:.5rem}
</style>
</head>
<body>
<h1>Лабораторные работы</h1>

<?php if (isset($_GET['ok'])): ?><p class="ok">Файл сохранён.</p><?php endif; ?>
<?php if ($errorKey !== null): ?>
  <p class="err">Загрузка отклонена: <?= h($messages[$errorKey] ?? $messages['internal']) ?></p>
<?php endif; ?>

<form method="post" action="/upload.php" enctype="multipart/form-data">
  <input type="hidden" name="MAX_FILE_SIZE" value="<?= MAX_FILE_SIZE ?>">
  <label>Дисциплина
    <input type="text" name="discipline" minlength="2" maxlength="100" required>
  </label>
  <label>PDF до 5 МиБ
    <input type="file" name="document" accept="application/pdf,.pdf" required>
  </label>
  <button type="submit">Загрузить</button>
</form>

<table>
  <tr><th>Имя</th><th>Дисциплина</th><th>Тип</th><th>Размер, байт</th><th>Дата</th><th></th></tr>
<?php foreach ($items as $item): ?>
  <tr>
    <td><?= h((string) ($item['original_name'] ?? '')) ?></td>
    <td><?= h((string) ($item['discipline'] ?? '')) ?></td>
    <td><?= h((string) ($item['mime'] ?? '')) ?></td>
    <td><?= h((string) ($item['size'] ?? '')) ?></td>
    <td><?= h((string) ($item['uploaded_at'] ?? '')) ?></td>
    <td><a href="/download.php?id=<?= h(rawurlencode((string) ($item['id'] ?? ''))) ?>">Скачать</a></td>
  </tr>
<?php endforeach; ?>
</table>
</body>
</html>
