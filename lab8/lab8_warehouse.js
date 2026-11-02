// Лабораторная работа 8, вариант 8: Склад (MongoDB 8). Запуск: mongosh --file lab8_warehouse.js
// Только синтетические данные, только учебная БД lab8_warehouse.
const wdb = db.getSiblingDB('lab8_warehouse');
wdb.dropDatabase();  // только учебная БД!
// ---- индексы ----
wdb.stock.createIndex({sku:1});
wdb.stock.createIndex({wh:1});
wdb.movements.createIndex({sku:1, wh:1, ts:-1});
wdb.movements.createIndex({type:1, ts:-1});
wdb.movements.createIndex({doc_no:1});
// ---- данные ----
wdb.warehouses.insertMany([{"_id": "WH-ALA", "name": "Склад Алматы", "city": "Алматы"}, {"_id": "WH-AST", "name": "Склад Астана", "city": "Астана"}, {"_id": "WH-SHY", "name": "Склад Шымкент", "city": "Шымкент"}]);
wdb.products.insertMany([{"_id": "SKU-1001", "name": "Ноутбук Lite 15", "category": "Электроника", "unit": "шт", "price": 420000, "active": true}, {"_id": "SKU-1002", "name": "Смартфон S5", "category": "Электроника", "unit": "шт", "price": 250000, "active": true}, {"_id": "SKU-1003", "name": "Наушники Air", "category": "Электроника", "unit": "шт", "price": 35000, "active": true}, {"_id": "SKU-2001", "name": "Офисный стул Комфорт", "category": "Мебель", "unit": "шт", "price": 45000, "active": true}, {"_id": "SKU-2002", "name": "Стол письменный", "category": "Мебель", "unit": "шт", "price": 60000, "active": true}, {"_id": "SKU-3001", "name": "Бумага А4 (пачка)", "category": "Канцелярия", "unit": "пач", "price": 2500, "active": true}, {"_id": "SKU-3002", "name": "Ручка шариковая (уп. 50)", "category": "Канцелярия", "unit": "уп", "price": 1800, "active": true}, {"_id": "SKU-4001", "name": "Принтер LaserJet", "category": "Оргтехника", "unit": "шт", "price": 130000, "active": true}]);
wdb.stock.insertMany([{"_id": "SKU-1001@WH-ALA", "sku": "SKU-1001", "wh": "WH-ALA", "qty": 20, "reserved": 0, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-1001@WH-AST", "sku": "SKU-1001", "wh": "WH-AST", "qty": 23, "reserved": 0, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-1002@WH-ALA", "sku": "SKU-1002", "wh": "WH-ALA", "qty": 35, "reserved": 5, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-1002@WH-AST", "sku": "SKU-1002", "wh": "WH-AST", "qty": 25, "reserved": 0, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-1003@WH-ALA", "sku": "SKU-1003", "wh": "WH-ALA", "qty": 20, "reserved": 10, "min_qty": 20, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-2001@WH-ALA", "sku": "SKU-2001", "wh": "WH-ALA", "qty": 40, "reserved": 0, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-2001@WH-AST", "sku": "SKU-2001", "wh": "WH-AST", "qty": 35, "reserved": 0, "min_qty": 10, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-2002@WH-AST", "sku": "SKU-2002", "wh": "WH-AST", "qty": 21, "reserved": 0, "min_qty": 5, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-3001@WH-ALA", "sku": "SKU-3001", "wh": "WH-ALA", "qty": 110, "reserved": 0, "min_qty": 100, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-3001@WH-SHY", "sku": "SKU-3001", "wh": "WH-SHY", "qty": 320, "reserved": 0, "min_qty": 100, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-3002@WH-ALA", "sku": "SKU-3002", "wh": "WH-ALA", "qty": 60, "reserved": 0, "min_qty": 100, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-3002@WH-SHY", "sku": "SKU-3002", "wh": "WH-SHY", "qty": 200, "reserved": 0, "min_qty": 100, "updated_at": new Date("2026-10-07T09:00:00Z")}, {"_id": "SKU-4001@WH-ALA", "sku": "SKU-4001", "wh": "WH-ALA", "qty": 17, "reserved": 0, "min_qty": 5, "updated_at": new Date("2026-10-07T09:00:00Z")}]);
wdb.movements.insertMany([
  {sku:"SKU-1001", wh:"WH-ALA", type:"receipt", qty:40, doc_no:"RC-001", ts:ISODate("2026-09-01T09:00:00Z")},
  {sku:"SKU-1002", wh:"WH-ALA", type:"receipt", qty:60, doc_no:"RC-002", ts:ISODate("2026-09-01T09:00:00Z")},
  {sku:"SKU-1003", wh:"WH-ALA", type:"receipt", qty:120, doc_no:"RC-003", ts:ISODate("2026-09-02T09:00:00Z")},
  {sku:"SKU-2001", wh:"WH-AST", type:"receipt", qty:50, doc_no:"RC-004", ts:ISODate("2026-09-02T09:00:00Z")},
  {sku:"SKU-2002", wh:"WH-AST", type:"receipt", qty:30, doc_no:"RC-005", ts:ISODate("2026-09-03T09:00:00Z")},
  {sku:"SKU-3001", wh:"WH-SHY", type:"receipt", qty:500, doc_no:"RC-006", ts:ISODate("2026-09-03T09:00:00Z")},
  {sku:"SKU-3002", wh:"WH-SHY", type:"receipt", qty:300, doc_no:"RC-007", ts:ISODate("2026-09-04T09:00:00Z")},
  {sku:"SKU-4001", wh:"WH-ALA", type:"receipt", qty:25, doc_no:"RC-008", ts:ISODate("2026-09-04T09:00:00Z")},
  {sku:"SKU-1001", wh:"WH-AST", type:"receipt", qty:20, doc_no:"RC-009", ts:ISODate("2026-09-05T09:00:00Z")},
  {sku:"SKU-1002", wh:"WH-AST", type:"receipt", qty:35, doc_no:"RC-010", ts:ISODate("2026-09-05T09:00:00Z")},
  {sku:"SKU-3001", wh:"WH-ALA", type:"receipt", qty:200, doc_no:"RC-011", ts:ISODate("2026-09-06T09:00:00Z")},
  {sku:"SKU-2001", wh:"WH-ALA", type:"receipt", qty:40, doc_no:"RC-012", ts:ISODate("2026-09-06T09:00:00Z")},
  {sku:"SKU-1001", wh:"WH-ALA", type:"shipment", qty:12, doc_no:"SH-001", ts:ISODate("2026-09-10T09:00:00Z")},
  {sku:"SKU-1002", wh:"WH-ALA", type:"shipment", qty:25, doc_no:"SH-002", ts:ISODate("2026-09-11T09:00:00Z")},
  {sku:"SKU-1003", wh:"WH-ALA", type:"shipment", qty:70, doc_no:"SH-003", ts:ISODate("2026-09-12T09:00:00Z")},
  {sku:"SKU-3001", wh:"WH-SHY", type:"shipment", qty:180, doc_no:"SH-004", ts:ISODate("2026-09-12T09:00:00Z")},
  {sku:"SKU-2001", wh:"WH-AST", type:"shipment", qty:15, doc_no:"SH-005", ts:ISODate("2026-09-15T09:00:00Z")},
  {sku:"SKU-4001", wh:"WH-ALA", type:"shipment", qty:8, doc_no:"SH-006", ts:ISODate("2026-09-16T09:00:00Z")},
  {sku:"SKU-1002", wh:"WH-AST", type:"shipment", qty:10, doc_no:"SH-007", ts:ISODate("2026-09-18T09:00:00Z")},
  {sku:"SKU-3001", wh:"WH-ALA", type:"shipment", qty:90, doc_no:"SH-008", ts:ISODate("2026-09-20T09:00:00Z")},
  {sku:"SKU-1001", wh:"WH-ALA", type:"transfer_out", qty:8, doc_no:"TR-01", ts:ISODate("2026-09-22T09:00:00Z")},
  {sku:"SKU-1001", wh:"WH-AST", type:"transfer_in", qty:8, doc_no:"TR-01", ts:ISODate("2026-09-22T09:00:00Z")},
  {sku:"SKU-3002", wh:"WH-SHY", type:"transfer_out", qty:100, doc_no:"TR-02", ts:ISODate("2026-09-25T09:00:00Z")},
  {sku:"SKU-3002", wh:"WH-ALA", type:"transfer_in", qty:100, doc_no:"TR-02", ts:ISODate("2026-09-25T09:00:00Z")},
  {sku:"SKU-1003", wh:"WH-ALA", type:"shipment", qty:30, doc_no:"SH-009", ts:ISODate("2026-10-01T09:00:00Z")},
  {sku:"SKU-2002", wh:"WH-AST", type:"shipment", qty:9, doc_no:"SH-010", ts:ISODate("2026-10-03T09:00:00Z")},
  {sku:"SKU-3002", wh:"WH-ALA", type:"shipment", qty:40, doc_no:"SH-011", ts:ISODate("2026-10-05T09:00:00Z")},
  {sku:"SKU-1001", wh:"WH-AST", type:"shipment", qty:5, doc_no:"SH-012", ts:ISODate("2026-10-07T09:00:00Z")}
]);
print('products:',wdb.products.countDocuments(),'warehouses:',wdb.warehouses.countDocuments(),'stock:',wdb.stock.countDocuments(),'movements:',wdb.movements.countDocuments());

print('--- Q1 карточка товара');
printjson(wdb.products.findOne({_id:'SKU-1001'}));

print('--- Q2 остатки товара по складам и итог');
printjson(wdb.stock.find({sku:'SKU-1001'},{_id:0,wh:1,qty:1,reserved:1}).sort({wh:1}).toArray());
printjson(wdb.stock.aggregate([{$match:{sku:'SKU-1001'}},
  {$group:{_id:'$sku', total_qty:{$sum:'$qty'}, total_available:{$sum:{$subtract:['$qty','$reserved']}}}}]).toArray());

print('--- Q3 последние движения по товару на складе');
printjson(wdb.movements.find({sku:'SKU-1001',wh:'WH-ALA'},{_id:0,type:1,qty:1,doc_no:1,ts:1}).sort({ts:-1}).limit(5).toArray());

print('--- Q4 списание 5 шт SKU-1002 со склада WH-ALA (условное атомарное изменение)');
let r = wdb.stock.updateOne(
  {_id:'SKU-1002@WH-ALA', $expr:{$gte:[{$subtract:['$qty','$reserved']}, 5]}},
  {$inc:{qty:-5}, $set:{updated_at:new Date()}});
if (r.modifiedCount === 1) {
  wdb.movements.insertOne({sku:'SKU-1002', wh:'WH-ALA', type:'shipment', qty:5, doc_no:'SH-013', ts:new Date()});
}
printjson({modified:r.modifiedCount});
printjson(wdb.stock.findOne({_id:'SKU-1002@WH-ALA'}));
// негативный тест: остатка недостаточно -> modifiedCount 0, движение не пишется
printjson({modified: wdb.stock.updateOne(
  {_id:'SKU-1002@WH-ALA', $expr:{$gte:[{$subtract:['$qty','$reserved']}, 9999]}},
  {$inc:{qty:-9999}}).modifiedCount});

print('--- Q5 статистика: топ отгрузок за период (сентябрь–октябрь 2026)');
printjson(wdb.movements.aggregate([
  {$match:{type:'shipment', ts:{$gte:ISODate('2026-09-01T00:00:00Z'), $lt:ISODate('2026-11-01T00:00:00Z')}}},
  {$group:{_id:'$sku', shipped:{$sum:'$qty'}, ops:{$sum:1}}},
  {$sort:{shipped:-1}}, {$limit:5},
  {$lookup:{from:'products', localField:'_id', foreignField:'_id', as:'p'}},
  {$project:{_id:0, sku:'$_id', name:{$first:'$p.name'}, shipped:1, ops:1}}]).toArray());

print('--- Q6 аналитика: стоимость запасов по складам');
printjson(wdb.stock.aggregate([
  {$lookup:{from:'products', localField:'sku', foreignField:'_id', as:'p'}}, {$unwind:'$p'},
  {$group:{_id:'$wh', value:{$sum:{$multiply:['$qty','$p.price']}}, items:{$sum:1}}},
  {$sort:{_id:1}}]).toArray());

print('--- Q7 товары ниже порога (доступно < min_qty)');
printjson(wdb.stock.find({$expr:{$lt:[{$subtract:['$qty','$reserved']},'$min_qty']}},
  {_id:1,qty:1,reserved:1,min_qty:1}).sort({_id:1}).toArray());

print('--- Q8 безопасное инвалидирование: снять товар с продажи (soft delete)');
printjson(wdb.products.find({_id:'SKU-4001'}).toArray());              // контрольная выборка
printjson({modified: wdb.products.updateOne({_id:'SKU-4001', active:true}, {$set:{active:false}}).modifiedCount});

print('--- Сверка: остаток в stock = сумма движений (ожидается пустой список)');
printjson(wdb.movements.aggregate([
  {$group:{_id:{sku:'$sku',wh:'$wh'}, net:{$sum:{$cond:[{$in:['$type',['receipt','transfer_in']]},'$qty',{$multiply:['$qty',-1]}]}}}},
  {$lookup:{from:'stock', localField:'_id.sku', foreignField:'sku', as:'st'}}, {$unwind:'$st'},
  {$match:{$expr:{$eq:['$st.wh','$_id.wh']}}},
  {$match:{$expr:{$ne:['$net','$st.qty']}}},
  {$project:{_id:0, sku:'$_id.sku', wh:'$_id.wh', net:1, stock_qty:'$st.qty'}}]).toArray());

print('--- EXPLAIN Q3');
printjson(wdb.movements.find({sku:'SKU-1001',wh:'WH-ALA'}).sort({ts:-1}).limit(5).explain('executionStats').executionStats);

print('--- Альтернативный способ Q2: остаток считается по журналу движений (без таблицы stock)');
printjson(wdb.movements.aggregate([
  {$match:{sku:'SKU-1001', wh:'WH-ALA'}},
  {$group:{_id:null, qty:{$sum:{$cond:[{$in:['$type',['receipt','transfer_in']]},'$qty',{$multiply:['$qty',-1]}]}}, scanned:{$sum:1}}}]).toArray());
print('--- EXPLAIN основного способа: чтение по _id в stock');
printjson(wdb.stock.find({_id:'SKU-1001@WH-ALA'}).explain('executionStats').executionStats);
print('--- EXPLAIN альтернативы');
printjson(wdb.movements.explain('executionStats').aggregate([{$match:{sku:'SKU-1001', wh:'WH-ALA'}},{$group:{_id:null, n:{$sum:1}}}]));
