"""Idempotently seed 36 synthetic orders without deleting other records."""
from datetime import datetime, timezone, timedelta
from src.domain import create_order

CATALOG = [
    ("PR01","Наушники","Электроника",12990),
    ("PR02","Клавиатура","Электроника",15990),
    ("PR03","Футболка","Одежда",6900),
    ("PR04","Кроссовки","Одежда",24990),
    ("PR05","Книга Python","Книги",8900),
    ("PR06","Блокнот","Канцелярия",1900),
    ("PR07","Мышь","Электроника",8990),
    ("PR08","Рюкзак","Аксессуары",13990),
]

def generate_orders():
    statuses=["paid","delivered","shipped","new","cancelled","paid"]
    orders=[]
    for i in range(36):
        products=[]
        for k in range(1+i%3):
            pid,name,cat,price=CATALOG[(i*3+k)%len(CATALOG)]
            products.append({"product_id":pid,"name":name,"category":cat,"price_kzt":price,"quantity":1+(i+k)%3})
        date=datetime(2026,10,1,tzinfo=timezone.utc)+timedelta(days=i%12,hours=8+(i%9))
        orders.append(create_order(f"ORD-{i+1:03d}",f"C{(i%8)+1:03d}",products,statuses[i%len(statuses)],date))
    return orders

def main():
    from src.db import connect, ensure_indexes
    client,db=connect()
    try:
        ensure_indexes(db)
        for o in generate_orders():
            db.orders.replace_one({"_id":o["_id"]},o,upsert=True)
        print("Seeded 36 orders. Total documents:",db.orders.count_documents({}))
    finally: client.close()
if __name__=="__main__":main()
