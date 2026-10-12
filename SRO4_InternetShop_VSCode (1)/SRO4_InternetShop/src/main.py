"""CLI: python -m src.main demo | query | create | update | delete | get."""
import argparse, json
from datetime import datetime, timezone
from .db import connect, ensure_indexes
from .repository import add_order, get_order, change_status, remove_order
from . import queries as q

def pretty(value):
    print(json.dumps(value,ensure_ascii=False,indent=2,default=str))

def main():
    ap=argparse.ArgumentParser(description="SRO4 MongoDB shop project")
    ap.add_argument("action",choices=["demo","query","create","get","update","delete"])
    ap.add_argument("--id",default="DEMO-1000")
    ap.add_argument("--status",default="paid")
    ap.add_argument("--number",type=int,choices=range(1,9),default=6)
    args=ap.parse_args()
    client,db=connect()
    try:
        ensure_indexes(db)
        if args.action=="demo":
            print("Count:",db.orders.count_documents({}))
            for title, result in [
                ("Q1 Customer orders",q.q1_customer_orders(db,"C001")),
                ("Q2 Order details",q.q2_order_details(db,"ORD-001")),
                ("Q3 Status orders",q.q3_status_orders(db,"paid")),
                ("Q4 Date period",q.q4_date_range(db,datetime(2026,10,1,tzinfo=timezone.utc),datetime(2026,11,1,tzinfo=timezone.utc))),
                ("Q5 Customer spend",q.q5_customer_paid_total(db,"C001")),
                ("Q6 Revenue by category",q.q6_revenue_by_category(db)),
                ("Q7 Top products",q.q7_top_products(db)),
                ("Q8 Daily revenue",q.q8_daily_revenue(db))]:
                print("\n"+title);pretty(result[:5] if isinstance(result,list) else result)
        elif args.action=="query":
            runners={1:lambda:q.q1_customer_orders(db,"C001"),2:lambda:q.q2_order_details(db,"ORD-001"),3:lambda:q.q3_status_orders(db,"paid"),4:lambda:q.q4_date_range(db,datetime(2026,10,1,tzinfo=timezone.utc),datetime(2026,11,1,tzinfo=timezone.utc)),5:lambda:q.q5_customer_paid_total(db,"C001"),6:lambda:q.q6_revenue_by_category(db),7:lambda:q.q7_top_products(db),8:lambda:q.q8_daily_revenue(db)}
            pretty(runners[args.number]())
        elif args.action=="create":
            products=[{"product_id":"PR01","name":"Наушники","category":"Электроника","price_kzt":12990,"quantity":2}]
            pretty(add_order(db,args.id,"C001",products))
        elif args.action=="get": pretty(get_order(db,args.id))
        elif args.action=="update": pretty({"updated":change_status(db,args.id,args.status)})
        elif args.action=="delete": pretty({"deleted":remove_order(db,args.id)})
    finally: client.close()
if __name__=="__main__": main()
