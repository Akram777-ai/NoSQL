#!/usr/bin/env bash
# Автотесты T1–T12 через curl. Запуск: сервер уже работает на localhost:8000
#   php -S localhost:8000 -t public     (в корне lab8)
#   bash tests/run_tests.sh
BASE=${BASE:-http://localhost:8000}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0

# --- тестовые файлы ---
mkpdf() { # mkpdf <файл> <размер_в_байтах>
  printf '%%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n' > "$1"
  local cur; cur=$(stat -c%s "$1")
  head -c $(( $2 - cur - 6 )) /dev/zero | tr '\0' ' ' >> "$1"
  printf '\n%%%%EOF' >> "$1"
}
mkpdf "$T/ok.pdf" 2000
mkpdf "$T/limit.pdf" $((5*1024*1024))
mkpdf "$T/big.pdf" $((5*1024*1024+1))
echo "Просто текст, не PDF" > "$T/fake.pdf"

up() { # up <поле-файл|-> <имя_файла> <дисциплина>  -> печатает Location
  local args=(-s -o /dev/null -D - -F "discipline=$3")
  [ "$1" != "-" ] && args+=(-F "document=@$1;filename=$2;type=application/pdf")
  curl "${args[@]}" "$BASE/upload.php" | tr -d '\r' | awk 'tolower($1)=="location:"{print $2}'
}
count() { grep -c '"id"' "$ROOT/var/data/submissions.json"; }
files() { find "$ROOT/var/uploads" -type f ! -name .gitkeep | wc -l; }
check() { # check <код> <описание> <условие 0/1>
  if [ "$3" = 1 ]; then echo "PASS $1 $2"; pass=$((pass+1)); else echo "FAIL $1 $2"; fail=$((fail+1)); fi
}

n0=$(count); f0=$(files)
loc=$(up "$T/ok.pdf" "lab1.pdf" "PHP")
check T1 "корректный PDF" $([[ "$loc" == *ok=1* && $(count) -eq $((n0+1)) && $(files) -eq $((f0+1)) ]] && echo 1 || echo 0)

loc=$(up - - "PHP"); check T2 "файл не выбран" $([[ "$loc" == *error=nofile* ]] && echo 1 || echo 0)

loc=$(up "$T/limit.pdf" "limit.pdf" "PHP"); check T3 "ровно 5 МиБ принимается" $([[ "$loc" == *ok=1* ]] && echo 1 || echo 0)
loc=$(up "$T/big.pdf" "big.pdf" "PHP");     check T4 "5 МиБ + 1 байт отклоняется" $([[ "$loc" == *error=size* ]] && echo 1 || echo 0)
loc=$(up "$T/fake.pdf" "fake.pdf" "PHP");   check T5 "TXT под видом PDF" $([[ "$loc" == *error=type* ]] && echo 1 || echo 0)

n1=$(count); loc=$(up "$T/ok.pdf" "report.php.pdf" "PHP")
last=$(grep stored_name "$ROOT/var/data/submissions.json" | tail -1)
check T6 "report.php.pdf -> случайное имя .pdf" $([[ "$loc" == *ok=1* && "$last" =~ \"[a-f0-9]{32}\.pdf\" ]] && echo 1 || echo 0)

loc=$(up "$T/ok.pdf" "../../x\"'<b>.pdf" "<script>alert(1)</script>")
body=$(curl -s "$BASE/index.php")
check T7 "../, кавычки и HTML экранированы" $([[ "$loc" == *ok=1* && "$body" != *"<script>alert(1)"* && ! -e "$ROOT/x" ]] && echo 1 || echo 0)

# T8 повреждённый JSON
cp "$ROOT/var/data/submissions.json" "$T/backup.json"; f8=$(files)
echo '{broken' > "$ROOT/var/data/submissions.json"
loc=$(up "$T/ok.pdf" "a.pdf" "PHP")
check T8 "битый JSON: ошибка, без сирот" $([[ "$loc" == *error=internal* && $(files) -eq $f8 ]] && echo 1 || echo 0)
cp "$T/backup.json" "$ROOT/var/data/submissions.json"

# T9 нет прав на uploads
chmod a-w "$ROOT/var/uploads"; n9=$(count)
loc=$(up "$T/ok.pdf" "a.pdf" "PHP")
chmod u+w "$ROOT/var/uploads"
check T9 "нет прав на uploads (если не root)" $([[ ( "$loc" == *error=internal* && $(count) -eq $n9 ) || $(id -u) -eq 0 ]] && echo 1 || echo 0)

# T10 параллельные запросы
n10=$(count)
for i in 1 2 3 4 5; do up "$T/ok.pdf" "p$i.pdf" "PHP" >/dev/null & done; wait
check T10 "5 параллельных запросов — 5 записей" $([[ $(count) -eq $((n10+5)) ]] && echo 1 || echo 0)
php -r 'json_decode(file_get_contents($argv[1]), true, 512, JSON_THROW_ON_ERROR);' "$ROOT/var/data/submissions.json" 2>/dev/null \
  && echo "     JSON валиден" || echo "     (php CLI недоступен или JSON невалиден)"

code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/download.php?id=../../etc/passwd")
code2=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/download.php?id=$(printf 'a%.0s' {1..32})")
check T11 "неверный id -> 400/404" $([[ "$code" == 400 && "$code2" == 404 ]] && echo 1 || echo 0)

id=$(grep '"id"' "$ROOT/var/data/submissions.json" | tail -1 | sed 's/.*: "\(.*\)".*/\1/')
mv "$ROOT/var/uploads/$id.pdf" "$T/moved.pdf"
code=$(curl -s -o "$T/body" -w '%{http_code}' "$BASE/download.php?id=$id")
mv "$T/moved.pdf" "$ROOT/var/uploads/$id.pdf"
check T12 "удалён файл -> 404 без путей" $([[ "$code" == 404 && ! $(cat "$T/body") == *"/"* ]] && echo 1 || echo 0)

echo "Итого: PASS=$pass FAIL=$fail"
