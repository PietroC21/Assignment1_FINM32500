from abc import ABC, abstractmethod
from data_generator import MarketDataPoint

class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: MarketDataPoint) -> list:
        pass

class MovingAverage(Strategy):
    def generate_signals(self, tick):
        