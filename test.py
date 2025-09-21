import unittest
from data_generator import MarketDataPoint
from models import Order
import datetime
from dataclasses import FrozenInstanceError


class TestMutability(unittest.TestCase):
    def test_order_status_is_mutable(self):
        o = Order("AAPL", 10, 100.0, "bid")
        o.status = "ask"
        self.assertEqual(o.status, "bid")

    def test_market_data_point_is_immutable(self):
        tick = MarketDataPoint(datetime(2025, 1, 1, 9, 30), "AAPL", 100.0)
        with self.assertRaises(FrozenInstanceError):
            tick.price = 0  # modifying a frozen dataclass field should raise

if __name__ == "__main__":
    unittest.main()