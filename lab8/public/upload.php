<?php
declare(strict_types=1);

require dirname(__DIR__) . '/src/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Allow: POST');
    exit('Method Not Allowed');
}

$storedPath = null;
try {
    $discipline = cleanDiscipline($_POST['discipline'] ?? null);
    $file = uploadedFile('document');
    [$mime, $ext] = detectAllowedType($file['tmp_name']);

    $id = bin2hex(random_bytes(16));
    $storedName = $id . '.' . $ext;
    $storedPath = UPLOAD_DIR . '/' . $storedName;

    if (!move_uploaded_file($file['tmp_name'], $storedPath)) {
        throw new RuntimeException('Не удалось сохранить файл.');
    }

    appendMetadata([
        'id'            => $id,
        'original_name' => cleanOriginalName((string) $file['name']),
        'stored_name'   => $storedName,
        'discipline'    => $discipline,
        'mime'          => $mime,
        'size'          => filesize($storedPath),
        'sha256'        => hash_file('sha256', $storedPath),
        'uploaded_at'   => (new DateTimeImmutable())->format(DATE_ATOM),
    ]);

    header('Location: /index.php?ok=1');
    exit;
} catch (UploadException $e) {
    if ($storedPath !== null && is_file($storedPath)) {
        unlink($storedPath);
    }
    header('Location: /index.php?error=' . rawurlencode($e->reason));
    exit;
} catch (Throwable $e) {
    // Откат файла-«сироты» и запись в журнал; пользователю — общее сообщение.
    if ($storedPath !== null && is_file($storedPath)) {
        unlink($storedPath);
    }
    error_log($e->__toString());
    header('Location: /index.php?error=internal');
    exit;
}
