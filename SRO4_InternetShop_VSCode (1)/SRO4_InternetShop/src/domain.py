"""Pure helpers for shop orders. Monetary values use integer KZT."""
from datetime import datetime, timezone

VALID_STATUSES = {"new", "paid", "shipped", "delivered", "cancelled"}

def snapshot_item(product):
    """Freeze product price/category/name at time of checkout."""
    quantity = int(product["quantity"])
    unit_price = int(product["price_kzt"])
    if quantity <= 0 or unit_price < 0:
        raise ValueError("Quantity must be positive and price nonnegative")
    return {
        "product_id": str(product["product_id"]),
        "name_snapshot": str(product["name"]),
        "category_snapshot": str(product["category"]),
        "unit_price_kzt_snapshot": unit_price,
        "quantity": quantity,
        "line_total_kzt": unit_price * quantity,
    }

def create_order(order_id, customer_id, products, status="new", created_at=None):
    if status not in VALID_STATUSES:
        raise ValueError("Unknown status")
    if not products:
        raise ValueError("Order must contain at least one item")
    items = [snapshot_item(x) for x in products]
    return {
        "_id": str(order_id), "customer_id": str(customer_id),
        "created_at": created_at or datetime.now(timezone.utc),
        "status": status, "items": items,
        "total_kzt": sum(x["line_total_kzt"] for x in items),
    }

def calculate_total(items):
    return sum(int(item["unit_price_kzt_snapshot"]) * int(item["quantity"]) for item in items)
