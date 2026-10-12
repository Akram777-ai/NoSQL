"""Eight read access patterns, including 3 aggregation pipelines."""
from datetime import datetime,timezone

def q1_customer_orders(db,customer_id):
    return list(db.orders.find({"customer_id":customer_id}).sort("created_at",-1))

def q2_order_details(db,order_id):
    return db.orders.find_one({"_id":order_id})

def q3_status_orders(db,status):
    return list(db.orders.find({"status":status}).sort("created_at",-1))

def q4_date_range(db,start,end):
    return list(db.orders.find({"created_at":{"$gte":start,"$lt":end}}).sort("created_at",-1))

def q5_customer_paid_total(db,customer_id):
    return list(db.orders.aggregate([
        {"$match":{"customer_id":customer_id,"status":{"$in":["paid","shipped","delivered"]}}},
        {"$group":{"_id":"$customer_id","revenue_kzt":{"$sum":"$total_kzt"},"orders":{"$sum":1}}}
    ]))

def q6_revenue_by_category(db):
    return list(db.orders.aggregate([
        {"$match":{"status":{"$in":["paid","shipped","delivered"]}}},
        {"$unwind":"$items"},
        {"$group":{"_id":"$items.category_snapshot", "revenue_kzt":{"$sum":"$items.line_total_kzt"},"units":{"$sum":"$items.quantity"}}},
        {"$sort":{"revenue_kzt":-1}}
    ]))

def q7_top_products(db,limit=5):
    return list(db.orders.aggregate([
        {"$match":{"status":{"$in":["paid","shipped","delivered"]}}},
        {"$unwind":"$items"},
        {"$group":{"_id":{"id":"$items.product_id","name":"$items.name_snapshot"},"units":{"$sum":"$items.quantity"},"revenue_kzt":{"$sum":"$items.line_total_kzt"}}},
        {"$sort":{"units":-1,"_id.id":1}}, {"$limit":limit}
    ]))

def q8_daily_revenue(db):
    return list(db.orders.aggregate([
        {"$match":{"status":{"$in":["paid","shipped","delivered"]}}},
        {"$group":{"_id":{"$dateToString":{"format":"%Y-%m-%d","date":"$created_at","timezone":"UTC"}},"revenue_kzt":{"$sum":"$total_kzt"},"orders":{"$sum":1}}},
        {"$sort":{"_id":1}}
    ]))
