// Непрерывная запись во время отказа (для оценки RPO и фиксации ошибок).
// Запуск (URI со всеми тремя узлами):
// mongosh 'mongodb://127.0.0.1:27101,127.0.0.1:27102,127.0.0.1:27103/?replicaSet=rsLab10' --file writer_lab10.js
// Запустите, затем остановите PRIMARY. Скрипт работает 90 секунд.
const d = db.getSiblingDB('university_lab10');
const acked = [], failed = [];
const end = Date.now() + 90 * 1000;
let id = 1001;
while (Date.now() < end) {
  const t = new Date().toISOString();
  try {
    d.publications.insertOne(
      { pubId: id, title: 'Поток №' + id, section: 'Технологии', author: 'Writer', status: 'published', views: 0, published_at: new Date() },
      { writeConcern: { w: 'majority', wtimeout: 5000 } });
    acked.push(id);
    print(t, 'ACK ', id);
  } catch (e) {
    failed.push(id);
    print(t, 'FAIL', id, e.codeName || e.name);   // текст ошибки может содержать адреса; в отчёт — только код
  }
  id++;
  sleep(500);
}
print('ACKED:', JSON.stringify(acked));
print('FAILED:', JSON.stringify(failed));
print('MAX_ACKED:', acked.length ? Math.max(...acked) : null);
