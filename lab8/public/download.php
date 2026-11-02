<?php
declare(strict_types=1);

require dirname(__DIR__) . '/src/functions.php';

$id = $_GET['id'] ?? '';
if (!is_string($id) || !preg_match('/\A[a-f0-9]{32}\z/', $id)) {
    http_response_code(400);
    exit('Bad Request');
}

try {
    $items = loadMetadata();
} catch (Throwable $e) {
    error_log($e->__toString());
    http_response_code(500);
    exit('Internal Server Error');
}

$item = null;
foreach ($items as $candidate) {
    if (is_array($candidate) && ($candidate['id'] ?? null) === $id) {
        $item = $candidate;
        break;
    }
}
if ($item === null) {
    http_response_code(404);
    exit('Not Found');
}

// Путь строит сервер: каталог + basename серверного имени из реестра.
$path = UPLOAD_DIR . '/' . basename((string) ($item['stored_name'] ?? ''));
if (!is_file($path)) {
    http_response_code(404);
    exit('Not Found');
}

$downloadName = cleanOriginalName((string) ($item['original_name'] ?? 'document.pdf'));

header('Content-Type: application/pdf');
header('Content-Length: ' . filesize($path));
header('Content-Disposition: attachment; filename="document.pdf"; '
     . "filename*=UTF-8''" . rawurlencode($downloadName));
header('X-Content-Type-Options: nosniff');
readfile($path);
