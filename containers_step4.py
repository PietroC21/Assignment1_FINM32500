"""
Step 4: Containers for Data & Signals (CSV Backtester)
------------------------------------------------------
Drop-in module providing:
- MarketDataPoint (immutable)
- Order (mutable)
- In-memory containers: data_buffer, open_positions, signals, orders
- Helper functions: record_market_data, queue_signal, flush_signals_to_orders, apply_fill
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Literal, DefaultDict
from collections import defaultdict
from data_generator import MarketDataPoint
from models import Order

Action = Literal["BUY", "SELL"]
Signal = Tuple[Action, str, int, float]  # (action, symbol, qty, price)

# --- Step 4 containers ---
data_buffer: List[MarketDataPoint] = []

# Store positions as a dict keyed by symbol
# e.g., { "AAPL": {"quantity": 0, "avg_price": 0.0} }
open_positions: DefaultDict[str, Dict[str, float]] = defaultdict(
    lambda: {"quantity": 0, "avg_price": 0.0}
)

# Signals are collected as tuples before becoming Order objects
signals: List[Signal] = []

# Orders produced from signals (e.g., by a "broker/execution" component)
orders: List[Order] = []


# --- Convenience API ---
def record_market_data(point: MarketDataPoint) -> None:
    """Append a MarketDataPoint to the in-memory buffer."""
    data_buffer.append(point)


def queue_signal(action: Action, symbol: str, qty: int, price: float) -> None:
    """Collect a raw signal as a tuple (action, symbol, qty, price)."""
    signals.append((action, symbol, qty, price))


def flush_signals_to_orders() -> List[Order]:
    """
    Convert all queued signals into Order objects and clear the signal list.
    Returns the list of NEW orders so a caller can hand them to an execution simulator.
    """
    new_orders = [Order(*sig) for sig in signals]
    signals.clear()
    orders.extend(new_orders)
    return new_orders


def apply_fill(order: Order, fill_price: float) -> None:
    """
    Mark an order as FILLED and update open_positions using running average cost.
    Simple rules:
      - BUY increases quantity and recalculates avg_price toward fill_price.
      - SELL decreases quantity; avg_price unchanged while staying on the same side.
      - Crossing through zero resets avg_price to 0.0; if going short, basis becomes the latest fill_price.
    """
    pos = open_positions[order.symbol]
    q = int(pos["quantity"])
    ap = float(pos["avg_price"])

    if order.action == "BUY":
        new_q = q + order.qty
        if q >= 0:
            # same side (or flat) long accumulation
            pos["avg_price"] = (ap * q + fill_price * order.qty) / max(new_q, 1)
        else:
            # buying to cover part or all of a short
            if new_q == 0:
                pos["avg_price"] = 0.0
            elif new_q > 0:
                # crossed from short to long; start new long basis at fill
                pos["avg_price"] = fill_price
        pos["quantity"] = new_q
    else:  # SELL
        new_q = q - order.qty
        if q <= 0:
            # same side (or flat) short accumulation
            if q == 0:
                pos["avg_price"] = fill_price  # start short basis at first sell
            # keep avg_price for ongoing short constant for simplicity
        else:
            # selling out of a long
            if new_q == 0:
                pos["avg_price"] = 0.0
            elif new_q < 0:
                # crossed from long to short; start new short basis at fill
                pos["avg_price"] = fill_price
        pos["quantity"] = new_q

    order.status = "FILLED"


# --- Minimal demo helpers (optional) ---
def _demo_mutability() -> tuple[bool, bool]:
    """Returns (marketdata_immutable_ok, order_mutable_ok)."""
    md = MarketDataPoint(datetime.now(), "AAPL", 100.0)
    order = Order("BUY", "AAPL", 10, 100.0)

    md_immutable = False
    try:
        setattr(md, "price", 101.0)  # should fail (frozen dataclass)
    except Exception:
        md_immutable = True

    order.status = "FILLED"  # should succeed
    order_mutable = order.status == "FILLED"

    return md_immutable, order_mutable


if __name__ == "__main__":
    print(_demo_mutability())
