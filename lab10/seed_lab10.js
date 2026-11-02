// Лаб. 10, вариант 16: Новости, коллекция publications. Только синтетические данные.
// Запуск: mongosh --port 27101 --file seed_lab10.js   (подключаться к PRIMARY)
const d = db.getSiblingDB('university_lab10');
d.publications.drop();
d.publications.createIndex({ pubId: 1 }, { unique: true });

const sections = ['Политика', 'Экономика', 'Спорт', 'Технологии', 'Культура', 'Наука'];
const docs = [];
for (let i = 1; i <= 24; i++) {
  docs.push({
    pubId: i,
    title: 'Синтетическая новость №' + i,
    section: sections[i % sections.length],
    author: 'Автор ' + (1 + i % 4),
    status: i % 5 === 0 ? 'draft' : 'published',
    views: 100 + (i * 37) % 900,
    published_at: new Date(Date.UTC(2026, 9, 1 + (i % 28), 8, 0, 0))
  });
}
const res = d.publications.insertMany(docs, { writeConcern: { w: 'majority', wtimeout: 5000 } });
print('inserted:', Object.keys(res.insertedIds).length);
printjson(d.publications.aggregate([{ $group: { _id: null, count: { $sum: 1 }, maxPubId: { $max: '$pubId' }, sumViews: { $sum: '$views' } } }]).toArray());
