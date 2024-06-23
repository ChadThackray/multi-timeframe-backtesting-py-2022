import numpy as np
import pandas as pd

import pandas_ta as ta

from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply

data = pd.read_csv("BTCUSDT-1m-2022-08.csv",
        usecols = [0,1,2,3,4],
        names = ["Date","Open","High","Low","Close"])
data["Date"] = pd.to_datetime(data["Date"], unit = "ms")
data.set_index("Date", inplace=True)

print(data)

# If you plot too many bars it aggregates to 5 mins which can make 
# it difficult to see your entries and exits. 
data = data.iloc[1000:3000]

# datetime offset codes
# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects

print(data)

def momentum(arr, n=1):
    ind = (np.diff(arr, n=n)/arr[:-n]) * 100
    ind = np.concatenate((np.zeros(n), ind))
    return ind

class RsiOscillator(Strategy):

    # Defining as a class variable lets it be optimized
    short_threshold = 0.1
    long_threshold = 1
    momentum_bars = 2

    # All initial calculations
    def init(self):
        self.short_momentum = self.I(ta.ao, high=self.data.High.s,
                                    low=self.data.Low.s, fast = 10)

        # This magical function does all the resampling
        # relying on pandas
        self.long_momentum = resample_apply(
            '10T', ta.rsi, self.data.Close.s, 21)

        self.longer_momentum = resample_apply(
            '1H', ta.rsi, self.data.Close.s, 21)
    # Step through bars one by one
    def next(self):

        if self.position:
            if self.position.is_long:
                if self.long_momentum[-1] < 0:
                    self.position.close()
            elif self.position.is_short:
                if self.long_momentum[-1] > 0:
                    self.position.close()

        else:
            if self.long_momentum[-1] > self.long_threshold and \
                    self.short_momentum[-1] > self.short_threshold:
                self.buy()
            elif self.long_momentum[-1] < -1 * self.long_threshold and \
                    self.short_momentum[-1] < -1 * self.short_threshold:
                self.sell()

bt = Backtest(data, RsiOscillator, cash=10_000_000, commission=.002)
stats = bt.run()

print(stats)
bt.plot()


