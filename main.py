import csv  
from typing import List, Dict, Any
from data_generator import market_data_generator  
from models import load_market_data  
from collections import defaultdict
from strategies import MovingAverageStrategy, MomentumStrategy  
from engine import Engine  
import matplotlib.pyplot as plt
from reporting import save_report
def generate_merged_market_csv(symbols: List[str],  
                               start_price:  List[float],  
                               ticks_per_symbol: int,  
                               volatilities: float,  
                               out_filename: str):  
    """  
    Generate merged market_data.csv by round-robin polling per-symbol generators.  
    Writes CSV with header: timestamp, symbol, price  
    """  
    gens = {sym: market_data_generator(sym, start_price, volatility=volatility, interval=0.0)  
            for sym,volatility in zip(symbols,volatilities)}  
  
    ticks = []  
    for _ in range(ticks_per_symbol):  
        for sym in symbols:  
            tick = next(gens[sym])  
            ticks.append(tick)  
  
    # Optionally shuffle ticks here to create more randomness; we keep round-robin order.  
    # Write to CSV  
    with open(out_filename, "w", newline="") as f:  
        writer = csv.writer(f)  
        writer.writerow(['timestamp', 'symbol', 'price'])  
        for t in ticks:  
            writer.writerow([t.timestamp.isoformat(), t.symbol, f"{t.price:.2f}"])  
    print(f"Generated {len(ticks)} ticks across {len(symbols)} symbols to {out_filename}")  
  
def build_strategies_for_symbols(symbols: List[str]):  
    """  
    Create a list of strategy instances, one MA and one Momentum per symbol.  
    Strategies are stateful and tied to the symbol passed in.  
    """  
    strategies:Dict[str,Any ] = defaultdict(list)
    for s in symbols:  
        strategies[s].append(MovingAverageStrategy(symbol=s))
        strategies[s].append(MomentumStrategy(symbol=s)) 
    return strategies  
  

def try_plot_equity(equity_curve, outpath="equity_curve.png"):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None

    if not equity_curve:
        return None

    plt.figure(figsize=(10, 4))

    # Handle the new structure where equity_curve is a dict by symbol
    if isinstance(equity_curve, dict):
        for symbol, curve in equity_curve.items():
            if not curve:
                continue
            # unzip (datetime, value) pairs
            times, values = zip(*curve)
            plt.plot(times, values, label=f"Equity {symbol}")
    else:
        # Fallback for old structure (list of curves)
        for i, curve in enumerate(equity_curve):
            if not curve:
                continue
            # unzip (datetime, value) pairs
            times, values = zip(*curve)
            plt.plot(times, values, label=f"Equity {i}")

    if not plt.gca().has_data():
        return None

    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.title("Equity Curves by Symbol")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    return outpath


def main():  

    
    ticks_per_symbol = 500
    symbols = ['AAPL', 'MSFT', 'NVDA', 'META', 'AMC']
    #symbols = ['AAPL', 'MSFT']
    start_price = 150
    volatilities = [0.02, 0.2, .2, 1, 0.3]
    out_file = 'market_data.csv'
    
    
    generate_merged_market_csv(symbols, start_price, ticks_per_symbol, volatilities, out_file)  

  
    # Load ticks from CSV into MarketDataPoint instances  
    ticks = load_market_data(out_file)  
    print(f"Loaded {len(ticks)} ticks from {out_file}")  
  
    
    # create strategy instances for each symbol and run them all on the merged time series  
    strategies = build_strategies_for_symbols(symbols) 
     
    engine = Engine()  
    results = engine.run(ticks, strategies) 
    metrics = engine.performance_metrics()  
    equity_curve = results.get("equity_curve", {})  
    #print([j for i,j in equity_curve])
    image = try_plot_equity(equity_curve, outpath="equity_curve.png")  
    save_report("performance.md", metrics, equity_curve, image_path=image)  
    print("Backtest complete (time mode). Report written to performance.md")  

if __name__ == "__main__":  
     main()  