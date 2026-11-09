# Шаг 4: перекос 80% в одной категории + альтернативный ключ deviceId + dayBucket
# + доп. эксперимент "горячее устройство"
import random, hashlib
from collections import Counter
random.seed(42)
N, Q, SHARDS = 12000, 30000, 3

def stable_hash(value):
    digest = hashlib.sha256(str(value).encode()).digest()
    return int.from_bytes(digest[:8], 'big')

# 80% записей относятся к deviceType = 0
rows = []
for i in range(N):
    t = 0 if random.random() < 0.8 else random.randint(1, 4)
    rows.append(dict(deviceId=i % 2500, deviceType=t,
                     readingId=i, dayBucket=i // 2500))

def low_card(r):      return r['deviceType'] % SHARDS
def hashed_device(r): return stable_hash(r['deviceId']) % SHARDS
def range_reading(r): return min(r['readingId'] // (N // SHARDS), SHARDS - 1)
def hashed_dev_day(r):
    return stable_hash((r['deviceId'], r['dayBucket'])) % SHARDS

def describe(name, assign, requests):
    docs = Counter(assign(r) for r in rows)
    load = Counter(assign(r) for r in requests)
    d = [docs[i] for i in range(SHARDS)]
    q = [load[i] for i in range(SHARDS)]
    print(f'{name:34s} docs={d} queries={q} '
          f'doc_max_mean={max(d)/(sum(d)/SHARDS):.2f} '
          f'query_max_mean={max(q)/(sum(q)/SHARDS):.2f}')

share0 = sum(r['deviceType'] == 0 for r in rows) / N
print('доля deviceType=0:', round(share0 * 100, 1), '%')

uniform = random.choices(rows, k=Q)
hot_rows = [r for r in rows if r['deviceType'] == 0]
hot_cat = [random.choice(hot_rows) if random.random() < 0.6
           else random.choice(rows) for _ in range(Q)]
# горячее устройство: 60% запросов к deviceId = 7
dev_rows = [r for r in rows if r['deviceId'] == 7]
hot_dev = [random.choice(dev_rows) if random.random() < 0.6
           else random.choice(rows) for _ in range(Q)]

keys = [('deviceType', low_card), ('hashed_device', hashed_device),
        ('range_reading', range_reading),
        ('hashed(device+day)', hashed_dev_day)]
print('--- набор данных 80% ---')
for name, fn in keys:
    describe(name + '/uniform', fn, uniform)
    describe(name + '/hot-category', fn, hot_cat)
print('--- горячее устройство (60% к deviceId=7) ---')
for name, fn in keys:
    describe(name + '/hot-device', fn, hot_dev)

print('--- кардинальность ---')
print('deviceType      :', len({r['deviceType'] for r in rows}))
print('deviceId        :', len({r['deviceId'] for r in rows}))
print('readingId       :', len({r['readingId'] for r in rows}))
print('device+dayBucket:', len({(r['deviceId'], r['dayBucket']) for r in rows}))

# AP-04: загрузка нового потока (3000 новых показаний, новый день dayBucket=5)
print('--- загрузка нового потока: 3000 записей (куда попадут вставки) ---')
new = [dict(deviceId=random.randrange(2500),
            deviceType=0 if random.random() < 0.8 else random.randint(1, 4),
            readingId=N + j, dayBucket=5) for j in range(3000)]
def range_new(r):  # границы диапазонов зафиксированы при начальной загрузке
    return min(r['readingId'] // (N // SHARDS), SHARDS - 1)
for name, fn in [('deviceType', low_card), ('hashed_device', hashed_device),
                 ('range_reading', range_new), ('hashed(device+day)', hashed_dev_day)]:
    c = Counter(fn(r) for r in new)
    print(f'{name:22s} inserts={[c[i] for i in range(SHARDS)]}')
