from datetime import datetime
from containers_step4 import (
    MarketDataPoint, queue_signal, flush_signals_to_orders,
    record_market_data, apply_fill, open_positions
)

record_market_data(MarketDataPoint(datetime.now(), "AAPL", 187.35))
queue_signal("BUY", "AAPL", 10, 187.30)
orders = flush_signals_to_orders()
for o in orders:
    apply_fill(o, o.price)

print(open_positions)  # {'AAPL': {'quantity': 10, 'avg_price': 187.3}}