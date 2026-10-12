import unittest
from unittest.mock import MagicMock
from src.repository import add_order,get_order,change_status,remove_order

class RepositoryTest(unittest.TestCase):
    def setUp(self):self.db=MagicMock()
    def test_create_and_read(self):
        record=add_order(self.db,"A","C",[{"product_id":"P","name":"Book","category":"Books","price_kzt":200,"quantity":1}])
        self.db.orders.insert_one.assert_called_once()
        self.assertEqual(record["total_kzt"],200)
        self.db.orders.find_one.return_value=record
        self.assertEqual(get_order(self.db,"A")["_id"],"A")
    def test_update(self):
        self.db.orders.update_one.return_value.matched_count=1
        self.assertTrue(change_status(self.db,"A","paid"))
        self.db.orders.update_one.assert_called_once_with({"_id":"A"},{"$set":{"status":"paid"}})
    def test_delete(self):
        self.db.orders.delete_one.return_value.deleted_count=1
        self.assertTrue(remove_order(self.db,"A"))
        self.db.orders.delete_one.assert_called_once_with({"_id":"A"})
if __name__=="__main__":unittest.main()
