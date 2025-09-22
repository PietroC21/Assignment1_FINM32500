from typing import Dict  
import os  
  
def ascii_sparkline(values):  
    if not values:  
        return ""  
    bars = "▁▂▃▄▅▆▇█"  
    mn, mx = min(values), max(values)  
    if mx == mn:  
        return bars[0] * len(values)  
    out = ""  
    for v in values:  
        idx = int((v - mn) / (mx - mn) * (len(bars) - 1))  
        out += bars[idx]  
    return out  
  
def save_report(filepath: str, metrics: Dict, equity_curve, image_path=None):  
    lines = []  
    lines.append("# Backtest Performance Report\n")  
    lines.append("## Key Metrics\n")  
    lines.append("| Metric | Value |")  
    lines.append("|---|---:|")  
    lines.append(f"| Initial equity | {metrics.get('initial_equity'):.2f} |")  
    lines.append(f"| Final equity | {metrics.get('final_equity'):.2f} |")  
    lines.append(f"| Total return | {metrics.get('total_return'):.2%} |")  
    sharpe = metrics.get('sharpe')  
    lines.append(f"| Sharpe (ann.) | {sharpe:.3f} |" if sharpe == sharpe else "| Sharpe (ann.) | N/A |")  
    lines.append(f"| Max drawdown | {metrics.get('max_drawdown'):.2%} |")  
  
    lines.append("\n## Equity Curve\n")  
    if image_path and os.path.exists(image_path):  
        lines.append(f"![Equity Curve]({os.path.basename(image_path)})\n")  
    else:  
        # Handle new structure where equity_curve is a dict by symbol
        if isinstance(equity_curve, dict):
            for symbol, curve in equity_curve.items():
                eq_values = [v for (_, v) in curve]  
                lines.append(f"ASCII Sparkline for {symbol}:\n\n")  
                lines.append("```\n" + ascii_sparkline(eq_values) + "\n```\n")
        else:
            # Fallback for old structure
            eq_values = [v for (_, v) in equity_curve]  
            lines.append("ASCII Sparkline:\n\n")  
            lines.append("```\n" + ascii_sparkline(eq_values) + "\n```\n")  
  
    lines.append("\n## Short interpretation\n")  
    lines.append("This report shows the basic metrics computed from the backtest. "  
                 "Sharpe ratio is a simple mean/std annualized assuming 252 periods/year. "  
                 "Max drawdown is the largest peak-to-trough decline observed.\n")  
  
    with open(filepath, "w") as f:  
        f.write("\n".join(lines))  