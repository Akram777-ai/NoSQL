# Лабораторная работа №11, вариант 09 (IoT-датчики)
# candidate: deviceId, alternative low-cardinality key: deviceType
import random, hashlib
from collections import Counter
random.seed(42)
N, Q, SHARDS = 12000, 30000, 3
rows = [dict(deviceId=i % 2500,
             deviceType=i % 5,
             readingId=i) for i in range(N)]

def stable_hash(value):
    digest = hashlib.sha256(str(value).encode()).digest()
    return int.from_bytes(digest[:8], 'big')

def low_card(row):
    return row['deviceType'] % SHARDS

def hashed_device(row):
    return stable_hash(row['deviceId']) % SHARDS

def range_reading(row):
    return min(row['readingId'] // (N // SHARDS), SHARDS - 1)

def describe(name, assign, requests):
    docs = Counter(assign(r) for r in rows)
    load = Counter(assign(r) for r in requests)
    d = [docs[i] for i in range(SHARDS)]
    q = [load[i] for i in range(SHARDS)]
    print(name, 'docs=', d, 'queries=', q,
          'doc_max_mean=', round(max(d)/(sum(d)/SHARDS), 2),
          'query_max_mean=', round(max(q)/(sum(q)/SHARDS), 2))

uniform = random.choices(rows, k=Q)
hot_rows = [r for r in rows if r['deviceType'] == 0]
hot = [random.choice(hot_rows)
       if random.random() < 0.6 else random.choice(rows)
       for _ in range(Q)]

for name, fn in [('deviceType', low_card),
                 ('hashed_device', hashed_device),
                 ('range_reading', range_reading)]:
    describe(name + '/uniform', fn, uniform)
    describe(name + '/hot', fn, hot)
