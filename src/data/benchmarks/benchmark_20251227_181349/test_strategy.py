import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy

class BBSqueezeStrategy(Strategy):
    def init(self):
        close = self.data.Close
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.upper = self.I(upper)
        self.middle = self.I(middle)
        self.lower = self.I(lower)
        self.bandwidth = self.I((self.upper - self.lower) / self.middle)

    def next(self):
        if len(self.bandwidth) >= 2:
            prev_bw = self.bandwidth[-2]
            current_upper = self.upper[-1]
            current_close = self.data.Close[-1]
            if prev_bw < 0.05 and current_close > current_upper:
                self.buy(size=0.95)
        if self.position:
            if self.data.Close[-1] < self.middle[-1]:
                self.sell()

if __name__ == "__main__":
    df = pd.read_csv(r'C:\Users\satya\OneDrive\Documents\AI Projects\moon-dev-ai-agents\sample_BTC_data.csv')
    df.columns = df.columns.str.strip().str.lower()
    df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    bt = Backtest(df, BBSqueezeStrategy, cash=1_000_000)
    stats = bt.run()
    print(stats)