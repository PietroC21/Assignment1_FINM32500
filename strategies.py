from abc import ABC, abstractmethod
from collections import deque
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
        self._quantity = 10
        self.__last_signal = None       #BUY or SELL signal or None

    def __moving_average(self, prices, window):
        if len(prices)<window:
            return None
        return sum(list(prices)[-window:])/window
    
    def generate_signals(self, tick: MarketDataPoint)-> list:
        signals = []
        self.__prices.append(tick.price)

        short_ma = self.__moving_average(self.__prices, self.__short_window)
        long_ma = self.__moving_average(self.__prices, self.__long_window)

        if short_ma and long_ma:
            if short_ma>long_ma and self.__last_signal!='BUY':
                signals.append((("BUY", tick.symbol,self._quantity, tick.price )))
                self.__last_signal = "BUY"
            elif short_ma<long_ma and self.__last_signal!="SELL":
                 signals.append((("SELL", tick.symbol,self._quantity, tick.price )))
                 self.__last_signal = "SELL"
        return signals
        

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
        
        
        