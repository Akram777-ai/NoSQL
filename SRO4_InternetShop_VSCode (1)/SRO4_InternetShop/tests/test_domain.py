import unittest
from datetime import datetime,timezone
from src.domain import create_order,calculate_total,snapshot_item
from scripts.seed import generate_orders

class ShopTest(unittest.TestCase):
    def test_snapshot_preserves_original_price(self):
        p={"product_id":"P","name":"Item","category":"Test","price_kzt":100,"quantity":2}
        order=create_order("1","C",[p]);p["price_kzt"]=300
        self.assertEqual(order["items"][0]["unit_price_kzt_snapshot"],100)
        self.assertEqual(order["total_kzt"],200)
    def test_line_totals_and_order_total(self):
        order=create_order("2","C",[{"product_id":"P","name":"A","category":"X","price_kzt":500,"quantity":3}])
        self.assertEqual(order["total_kzt"],1500)
        self.assertEqual(calculate_total(order["items"]),1500)
    def test_validation(self):
        with self.assertRaises(ValueError):create_order("3","C",[])
        with self.assertRaises(ValueError):snapshot_item({"product_id":"P","name":"X","category":"X","price_kzt":10,"quantity":0})
    def test_seed_is_synthetic_and_has_36_unique_orders(self):
        o=generate_orders()
        self.assertEqual(len(o),36)
        self.assertEqual(len({v["_id"] for v in o}),36)
        self.assertTrue(all(v["total_kzt"]==calculate_total(v["items"]) for v in o))
if __name__=="__main__":unittest.main()
