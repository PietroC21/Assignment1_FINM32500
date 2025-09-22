from models import *
import logging
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
import random

logger = logging.getLogger("Engine")  

class Engine:
    def __init__(self):
        # self.portfolio = {}
        self.cash = 100_000
        self.last_price: Dict[str, float] = {}
        self.positions: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'quantity': 0, 'avg_price': 0.0})  
        self.equity_curve = []
        self.equity_by_symbol = {}  # Store equity curves by symbol
        self.trades: List[Dict[str, Any]] = []  
    
    def run(self, ticks, strategies):
        intial_cash = self.cash
        ticks_by_symbol: Dict[str, List[MarketDataPoint]] = defaultdict(list)        
        for t in ticks:
            ticks_by_symbol[t.symbol].append(t)
        
        results:Dict[str, Any]= {}
        for symbol, sym_ticks in ticks_by_symbol.items():
            sym_ticks.sort(key= lambda x: x.timestamp)

            #run each strategy 
            res = self.__run(sym_ticks, strategies[symbol])
            results[symbol] = res
        return  {  
            "initial_cash": intial_cash,  
            "final_cash": self.cash,  
            "positions": self.positions,  
            "equity_curve": self.equity_by_symbol,  
        }  
    
    def __run(self, ticks:List[MarketDataPoint], strat_list: List[Any]):
        ticks = sorted(ticks, key= lambda t: t.timestamp)
        if not ticks:
            raise ExecutionError("No ticks were provided ")
        
        # Reset equity curve for this symbol
        self.equity_curve = []
        
        for tick in ticks:
            #update the last price
            self.last_price[tick.symbol] = tick.price

            #collect signals from strategies 
            signals = []
            
            for strat in strat_list:
                try:
                    sigs = strat.generate_signals(tick)
                    if sigs:
                        signals.extend(sigs)
                except Exception as e:
                    logger.exception(f"Strategy {type(strat).__name__} error on tick {tick}: {e}")  
                    continue
            # convert signals to Orders and execute them
            for sig in signals:
                try:
                    action, symbol, qty, price = sig  
                    order = Order(symbol, qty, price, action)
                    
                    order.validate()
                except OrderError as eE:
                    logger.error(f"Order validation failed for signal {sig}: {eE}")
                    continue
                except Exception as e:
                      logger.exception(f"Error creating order from signal {sig}: {e}")  
                      continue

                #execute the order (each order handled independently)
                try: 
                    self.execute_orders(order, tick.timestamp)
                except ExecutionError as e:
                    logger.error(f"Execution failed for order {order}: {e}")  
                    continue  
                except Exception as e:  
                    logger.exception(f"Unexpected error executing order : {e}")  
                    continue  
        
            # record equity after processing this tick (regardless of whether there were signals)
            equity = self._compute_equity()  
            self.equity_curve.append((tick.timestamp, equity))
        
        # Store the equity curve for this symbol
        if self.equity_curve:
            symbol = ticks[0].symbol if ticks else "unknown"
            self.equity_by_symbol[symbol] = self.equity_curve.copy()
    def execute_orders(self, order: Order, timestamp)->None:
        
        #Simulate occasional execution failure with 5% chance
        if random.random() < 0.01:
            raise ExecutionError('Simulating Execution Failure!')
        
        symbol = order.symbol
        qty = int(order.quantity)
        if qty<=0:
            raise OrderError('Order quantity must be greater than zero!')
        
        fill_price = self.last_price.get(symbol,float(order.price))
        pos = self.positions[symbol]
        old_qty = int(pos.get('quantity', 0))
        old_avg = float(pos.get('avg_price', 0.0))  

        action = order.status.upper()
        if action == 'BUY':
            cost = fill_price*qty
            if cost > self.cash:
                raise ExecutionError(f"Insufficient cash for BUY {qty} {symbol} @ {fill_price:.2f}: need {cost:.2f}, have {self.cash:.2f}")  

            new_qty = old_qty + qty

            # average price calculations:
            if old_qty>0 and new_qty>0:
                #add to existing position
                new_avg = ((old_qty*old_avg) +(qty*fill_price))/new_qty
            elif old_qty<0 and new_qty>=0:
                if new_qty == 0:
                    new_avg = 0.0
                else:
                    new_avg = fill_price
            else:
                new_avg = old_avg
            
            pos['quantity'] = new_qty
            pos['avg_price'] = float(new_avg)
            self.cash -= cost
            order.status = 'FILLED'
            self.trades.append({
                'timestamp': timestamp,
                'action': 'BUY',
                'quantity': qty,  
                'price': fill_price,  
                'cash_after': self.cash  
                })
            logger.info(f"FILLED BUY {qty} {symbol} @ {fill_price:.2f}. Cash: {self.cash:.2f}")
            
        elif action == "SELL":
            # Check if we have enough shares to sell
            if old_qty < qty:
                raise ExecutionError(f"Insufficient shares for SELL {qty} {symbol}: have {old_qty}, need {qty}")
            
            new_qty = old_qty - qty
            proceeds = fill_price * qty

            # Update position
            pos['quantity'] = new_qty
            # Update average price to zero if position is closed
            if new_qty == 0:
                pos['avg_price'] = 0.0

            self.cash += proceeds  
            order.status = "FILLED"  
            self.trades.append({  
                'timestamp': timestamp,  
                'action': 'SELL',  
                'symbol': symbol,  
                'quantity': qty,  
                'price': fill_price,  
                'cash_after': self.cash  
            })  
            logger.info(f"FILLED SELL {qty} {symbol} @ {fill_price:.2f}. Cash: {self.cash:.2f}")  
        else:
            raise ExecutionError(f"Unknown order action: {order.action}")  

    def _compute_equity(self):
        '''Compute equity = cash + sum(position_qty * last_price) for all symbols.'''
        equity = self.cash
        for sym, pos in self.positions.items():
            qty = pos.get('quantity', 0)
            if qty == 0:
                continue
            price = self.last_price.get(sym, pos.get('avg_price',0.0))
            equity += price*qty
        return float(equity)

    def performance_metrics(self):
        if not self.equity_curve:
            return {}
        eq_val = [v for (_,v) in self.equity_curve]
        intial_eq = eq_val[0]
        final_eq = eq_val[-1]
        total_return = (final_eq/intial_eq -1.0) if intial_eq!=0 else 0

        period_returns = []
        for i in range(1, len(eq_val)):
            prev = eq_val[i-1]
            curr = eq_val[i]
            if prev == 0:
                period_returns.append(0.0)
            else:
                period_returns.append(curr/prev-1.0)
        avg_ret = sum(period_returns)/len(period_returns) if period_returns else 0.0
        std_ret = np.std(period_returns) if len(period_returns) >=2 else 0.0
        sharpe = (avg_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0.0

        #max drawdown
        peak = eq_val[0]
        max_dd = 0.0
        for v in eq_val:
            if v> peak:
                peak = v
            dd = (peak-v)/ peak if peak>0 else 0.0
            if dd > max_dd:
                max_dd = dd
        return {
            'initial_equity': intial_eq,
            'final_equity': final_eq,
            'total_return': total_return,  
            'period_returns': period_returns,  
            'sharpe': sharpe,  
            'max_drawdown': max_dd  
        }