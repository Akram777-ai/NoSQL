"""CRUD operations over the orders collection."""
from .domain import create_order, VALID_STATUSES

def add_order(db, order_id, customer_id, products):
    order = create_order(order_id, customer_id, products)
    db.orders.insert_one(order)
    return order

def get_order(db, order_id):
    return db.orders.find_one({"_id": str(order_id)})

def change_status(db, order_id, status):
    if status not in VALID_STATUSES:
        raise ValueError("Invalid order status")
    result = db.orders.update_one({"_id": str(order_id)}, {"$set": {"status": status}})
    return result.matched_count == 1

def remove_order(db, order_id):
    return db.orders.delete_one({"_id": str(order_id)}).deleted_count == 1
