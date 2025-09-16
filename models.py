from data_generator import MarketDataPoint
import datetime
import csv

class Order:
    def __init__(self, symbol, quantity, price, status):
        self.__symbol = symbol
        self.__quantity = quantity
        self.__price = price
        self.__status = status
    
    def display(self):
        return f"return f'{self.__status} {self.__quantity} shares of {self.__symbol} at ${self.__price:,} each"
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, new_status):
        if new_status!='ask' and new_status!='bid':
            raise OrderError('Status must be a \'bid\' or \'ask\'')
        self.__status = new_status
    
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

if __name__ == '__main__':
    list = load_market_data('Assignment1_FINM32500/market_data.csv')
    

