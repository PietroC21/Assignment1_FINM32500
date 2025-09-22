from abc import ABC, abstractmethod
from collections import deque
from typing import Optional
from data_generator import MarketDataPoint

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass

class MovingAverageStrategy(Strategy):
    """
    Buy when short moving average crosses above long moving average
    Sell when short moving average crosses below long moving average
    """
    def __init__(self, symbol):
        self.__short_window = 5
        self.__symbol = symbol
        self.__long_window = 10
        self.__prices =  deque(maxlen=self.__long_window)
        self.__quantity = 10
        self.__position = 0
        self.__last_signal = None       
        self.__prev_short_ma: Optional[float] = None
        self.__prev_long_ma:Optional[float] = None

    def generate_signals(self, tick: MarketDataPoint)-> list:
        signals = []
        if tick.symbol!=self.__symbol:
            return signals
        
        self.__prices.append(tick.price)
        short_ma = self.__moving_average(self.__short_window)
        long_ma = self.__moving_average(self.__long_window)

        if short_ma is None or long_ma is None:
            self.__prev_short_ma = short_ma
            self.__prev_long_ma = long_ma
            return signals
        
        #detect signals
        if self.__prev_long_ma and self.__prev_short_ma:
            if self.__prev_short_ma<= self.__prev_long_ma and short_ma>=long_ma:
                qty = self.__quantity
                signals.append((("BUY", tick.symbol,self.__quantity, tick.price )))
                self.__position+=qty
                self.__last_signal='BUY'
            elif self.__prev_short_ma >= self.__prev_long_ma and short_ma < long_ma:
                signals.append((("SELL", tick.symbol,-self.__position, tick.price )))
                self.__position = -self.__position
                self.__last_signal='SELL'

        self.__prev_long_ma = long_ma
        self.__prev_short_ma = short_ma
        print(f'{self.__last_signal} for {tick.symbol} with a position of {self.__position} @ {tick.price}')
        return signals
    def display(self):
        print(f'')
    def __moving_average(self, window):
        if len(self.__prices)<window:
            return None
        return sum(list(self.__prices)[-window:])/window
    

class MomentumStrategy(Strategy):
    """ If the last N prices are increasing, BUY
        If the last N prices are decreasing SELL """
    def __init__(self, symbol):
        self.__lookback = 5
        self.__quantity = 10
        self.__symbol = symbol
        self.__prices = deque(maxlen=self.__lookback)

    def generate_signals(self, tick : MarketDataPoint):
        signals = []
        self.__prices.append(tick.price)

        if len(self.__prices) == self.__lookback:

            increasing = all(self.__prices[i]<=self.__prices[i+1] for i in range(len(self.__prices)-1))
            decreasing = all(self.__prices[i]>=self.__prices[i+1] for i in range(len(self.__prices)-1))

            if increasing:
                signals.append((("BUY", tick.symbol,self.__quantity, tick.price )))
            elif decreasing:
                signals.append((("SELL", tick.symbol,self.__quantity, tick.price )))
        return signals
        
        
        