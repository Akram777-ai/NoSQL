# Строит график распределения нагрузки (chart_load.png) по тем же данным, что simulation.py
# Требуется: pip install matplotlib
import random, hashlib
from collections import Counter
import matplotlib.pyplot as plt

random.seed(42)
N, Q, SHARDS = 12000, 30000, 3
rows = [dict(deviceId=i % 2500, deviceType=i % 5, readingId=i) for i in range(N)]

def stable_hash(v):
    return int.from_bytes(hashlib.sha256(str(v).encode()).digest()[:8], 'big')

keys = {'deviceType': lambda r: r['deviceType'] % SHARDS,
        'hashed_device': lambda r: stable_hash(r['deviceId']) % SHARDS,
        'range_reading': lambda r: min(r['readingId'] // (N // SHARDS), SHARDS - 1)}

uniform = random.choices(rows, k=Q)
hot_rows = [r for r in rows if r['deviceType'] == 0]
hot = [random.choice(hot_rows) if random.random() < 0.6 else random.choice(rows) for _ in range(Q)]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
for ax, (title, reqs) in zip(axes, [('uniform', uniform), ('hot (60% к одной категории)', hot)]):
    w = 0.26
    for k, (name, fn) in enumerate(keys.items()):
        c = Counter(fn(r) for r in reqs)
        pct = [c[i] / Q * 100 for i in range(SHARDS)]
        ax.bar([i + (k - 1) * w for i in range(SHARDS)], pct, w, label=name)
    ax.axhline(100 / SHARDS, color='gray', ls='--')
    ax.set_xticks(range(SHARDS)); ax.set_xticklabels(['Shard A', 'Shard B', 'Shard C'])
    ax.set_ylabel('Доля запросов, %'); ax.set_title(title)
axes[0].legend()
plt.tight_layout(); plt.savefig('chart_load.png', dpi=150)
print('Сохранено: chart_load.png')
