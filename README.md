# Assignment1_FINM32500
Design and implement a modular Python backtester that reads pre-generated market data from a CSV file, applies trading strategies, executes simulated orders, and produces a performance report.
## Features
* **CSV Data Input**: Load historical market data directly from CSV files
* **Signal Generation**: Generate signals according to mean-reversion and momentum strategies
* **Order Execution**: Execute orders according to signal generation
* **Position Tracking**: Track orders in a dictionary by symbol, quantity, price, side, and time
* **Performance Metrics**: Calculate P&L, drawdown, Sharpe ratio, and other key statistics
* **Visualization**: Plot equity curves, trade signals, and other analytics using Matplotlib

## Project Structure
* **data_generator.py**: Simulates a live market feed for a given symbol through a Gaussian random walk and then converts it to a CSV
* **engine.py**: Takes the signals and executes trades, while tracking portfolio performance metrics
* **main.py**: Runs the entire notebook by inputting symbols, using the data generator, running the strategies, executing orders, and tracking performance
* **models.py**: Defines the order class with personalized exceptions and loads the CSV data
* **reporting.py**: Generates a report file for our portfolio by using the performance metrics
* **strategies.py**: Defines the signal generation for our two strategies: mean-reversion and momentum
* **test.py**: Proves through a unit test that we can update Order.status but not MarketDataPoint.price

## Running the Notebook
### main.py
The script runs a full backtest using your chosen data and strategy. To run it, simply use `python main.py` or provide optional arguments with
`python main.py --data data/market_csv --strategy MovingAverageCrossover`
where
* `--data`: Path to the CSV file containing historical data
* `--strategy`: Name of the strategy class to run
The script will:
* Load data from the CSV file
* Execute the selected trading strategy
* Print performance metrics
* Save trade logs and plots (if enabled)

### test.py
The script ensures the integrity of key components (data loading, signal generation, backtesting engine). To run it, simply use `python test.py`. 
This will:
* Discover and execute all tests inside the `tests/` dictionary
* Print a summary of passed/failed tests
Use this command regularly to confirm changes do not break existing functionality