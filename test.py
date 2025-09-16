import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('market_data.csv')

plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['price'])
plt.show()