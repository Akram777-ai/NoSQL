// Проверка данных: на реплике или в базе восстановления.
// mongosh --port 27102 --eval "var DBNAME='university_lab10'" --file verify_lab10.js
// mongosh --port 27101 --eval "var DBNAME='university_restore10'" --file verify_lab10.js
const name = (typeof DBNAME !== 'undefined') ? DBNAME : 'university_lab10';
const d = db.getSiblingDB(name);
d.getMongo().setReadPref('primaryPreferred');
print('DB:', name);
printjson(d.publications.aggregate([
  { $match: { pubId: { $lte: 24 } } },
  { $group: { _id: null, count: { $sum: 1 }, maxPubId: { $max: '$pubId' }, sumViews: { $sum: '$views' } } }
]).toArray());
print('ожидается для исходных данных: count 24, maxPubId 24, sumViews 13500');
print('всего документов:', d.publications.countDocuments());
print('максимальный pubId в потоке (>=1001):', JSON.stringify(d.publications.find({ pubId: { $gte: 1001 } }).sort({ pubId: -1 }).limit(1).toArray().map(x => x.pubId)));
