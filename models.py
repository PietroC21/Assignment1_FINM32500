from data_generator import MarketDataPoint
import datetime
import csv

class Order:
    def __init__(self, symbol, quantity, price, status):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.status = status
    def display(self):
        return f"return f'{self.status} {self.quantity} shares of {self.symbol} at ${self.price:,} each"
    
    def validate(self):  
        if self.quantity <= 0:  
            raise OrderError("Order quantity must be positive.")  
        if self.status not in ("BUY", "SELL"):  
            raise OrderError("Order action must be 'BUY' or 'SELL'.")  
  
    
class OrderError(Exception): 
    def __init__(self, message):
        self.__message = message
        super().__init__(self.__message)

class ExecutionError(Exception): 
    def __init__(self, message):
        self.__message = message
        super().__init__(self.__message)

def load_market_data(path):
    l = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        for row, value in enumerate(reader):
            if row == 0:  # first row it's the column names
                continue

            timestamp = value[0]
            timestamp = datetime.datetime.fromisoformat(timestamp)
            symbol = value[1] 
            price = float(value[2])
            temp = MarketDataPoint(timestamp, symbol, price)
            l.append(temp)
    return l

