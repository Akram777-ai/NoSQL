<?php
declare(strict_types=1);

const MAX_FILE_SIZE = 5 * 1024 * 1024;               // 5 МиБ
const DATA_FILE     = __DIR__ . '/../var/data/submissions.json';
const UPLOAD_DIR    = __DIR__ . '/../var/uploads';

/** allow-list: MIME-тип => серверное расширение */
const ALLOWED_TYPES = ['application/pdf' => 'pdf'];

/**
 * Исключение, текст которого безопасно показывать пользователю.
 * Все остальные исключения считаются внутренними и только пишутся в журнал.
 */
final class UploadException extends RuntimeException
{
    public function __construct(public readonly string $reason, string $message = '')
    {
        parent::__construct($message !== '' ? $message : $reason);
    }
}

function h(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** Проверка поля discipline (вариант 1). */
function cleanDiscipline(mixed $value): string
{
    if (!is_string($value)) {
        throw new UploadException('discipline');
    }
    $value = trim(preg_replace('/\s+/u', ' ', $value) ?? '');
    $len = mb_strlen($value, 'UTF-8');
    if ($len < 2 || $len > 100 || preg_match('/[\p{C}]/u', $value) === 1) {
        throw new UploadException('discipline');
    }
    return $value;
}

/** Очистка исходного имени: только для отображения, в путь не попадает. */
function cleanOriginalName(string $name): string
{
    $name = basename(str_replace('\\', '/', $name));
    $name = preg_replace('/[\p{C}]/u', '', $name) ?? '';
    $name = mb_substr($name, 0, 150, 'UTF-8');
    return $name !== '' ? $name : 'document.pdf';
}

function uploadedFile(string $field): array
{
    // Превышен post_max_size: PHP полностью отбрасывает $_FILES и $_POST.
    if (empty($_FILES) && (int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 0) {
        throw new UploadException('size');
    }

    $file = $_FILES[$field] ?? null;
    if (!is_array($file) || is_array($file['error'] ?? null)) {
        throw new UploadException('field', 'Некорректное поле файла.');
    }

    // 1. Код ошибки проверяется ПЕРВЫМ, до обращения к tmp_name.
    $error = $file['error'] ?? UPLOAD_ERR_NO_FILE;
    switch ($error) {
        case UPLOAD_ERR_OK:
            break;
        case UPLOAD_ERR_NO_FILE:
            throw new UploadException('nofile');
        case UPLOAD_ERR_INI_SIZE:
        case UPLOAD_ERR_FORM_SIZE:
            throw new UploadException('size');
        case UPLOAD_ERR_PARTIAL:
            throw new UploadException('partial');
        default: // NO_TMP_DIR, CANT_WRITE, EXTENSION — служебные ошибки
            throw new RuntimeException('Ошибка загрузки PHP, код: ' . (int) $error);
    }

    // 2. Прикладной лимит размера.
    if (!is_int($file['size']) || $file['size'] < 1) {
        throw new UploadException('nofile');
    }
    if ($file['size'] > MAX_FILE_SIZE) {
        throw new UploadException('size');
    }

    // 3. Файл действительно пришёл по HTTP-загрузке.
    if (!is_string($file['tmp_name']) || !is_uploaded_file($file['tmp_name'])) {
        throw new RuntimeException('Источник не является HTTP-загрузкой.');
    }
    return $file;
}

/**
 * Определяет MIME по содержимому (Fileinfo) и сверяет с allow-list.
 * Возвращает [mime, серверное расширение].
 */
function detectAllowedType(string $path): array
{
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mime = $finfo->file($path);
    if ($mime === false || !array_key_exists($mime, ALLOWED_TYPES)) {
        throw new UploadException('type');
    }
    return [$mime, ALLOWED_TYPES[$mime]];
}

function appendMetadata(array $item): void
{
    $lock = fopen(DATA_FILE . '.lock', 'c');
    if ($lock === false || !flock($lock, LOCK_EX)) {
        throw new RuntimeException('Не удалось заблокировать реестр.');
    }
    try {
        $json = is_file(DATA_FILE) ? file_get_contents(DATA_FILE) : '[]';
        if ($json === false) {
            throw new RuntimeException('Не удалось прочитать реестр.');
        }
        $items = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        if (!is_array($items)) {
            throw new RuntimeException('Неверная структура реестра.');
        }
        $items[] = $item;
        $newJson = json_encode(
            $items,
            JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR
        );

        // Запись во временный файл рядом + атомарная замена.
        $tmp = DATA_FILE . '.' . bin2hex(random_bytes(6)) . '.tmp';
        if (file_put_contents($tmp, $newJson, LOCK_EX) === false
            || !rename($tmp, DATA_FILE)) {
            @unlink($tmp);
            throw new RuntimeException('Не удалось обновить реестр.');
        }
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

function loadMetadata(): array
{
    $json = file_get_contents(DATA_FILE);
    if ($json === false) {
        return [];
    }
    $items = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
    return is_array($items) ? $items : [];
}
