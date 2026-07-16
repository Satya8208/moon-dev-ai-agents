import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

class RSIReversalStrategy(Strategy):
    rsi_period = 14
    atr_period = 10
    oversold = 30
    overbought = 70
    atr_multiplier = 1.5
    
    def init(self):
        # Calculate indicators using self.I() wrapper
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        # Initialize signals
        self.buy_signal = self.I(lambda: np.zeros_like(self.data.Close), name='buy_signal')
        self.sell_signal = self.I(lambda: np.zeros_like(self.data.Close), name='sell_signal')
        
    def next(self):
        # Skip if we don't have enough data for indicators
        if len(self.rsi) < 2 or len(self.atr) < 1:
            return
        
        current_rsi = self.rsi[-1]
        previous_rsi = self.rsi[-2] if len(self.rsi) >= 2 else current_rsi
        
        # Entry logic: RSI crosses above 30 from below
        if not self.position:
            if previous_rsi < self.oversold and current_rsi > self.oversold:
                # Calculate stop loss using ATR
                stop_price = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Buy with 95% of portfolio
                self.buy(size=0.95, sl=stop_price)
        
        # Exit logic: RSI crosses below 70 from above
        elif self.position:
            if previous_rsi > self.overbought and current_rsi < self.overbought:
                self.sell(size=self.position.size)

if __name__ == "__main__":
    # Load and prepare data
    data = pd.read_csv(r"C:\Users\satya\OneDrive\Documents\AI Projects\moon-dev-ai-agents\sample_BTC_data.csv")
    
    # Clean column names
    data.columns = data.columns.str.strip().str.lower()
    
    # Map to required format with capital first letters
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }
    
    # Rename columns and select only required ones
    data = data.rename(columns=column_mapping)
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    data = data[required_cols]
    
    # Convert to datetime index if not already
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    # Run backtest
    bt = Backtest(data, RSIReversalStrategy, cash=1000000)
    stats = bt.run()
    
    # Print statistics
    print(stats)