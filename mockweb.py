import datetime
import pandas as pd
import random as r
import time
from threading import Thread
import numpy as np


class Stock:
    def __init__(self):
        self.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        self.data = {}
        self.keep_columns = ['Close', 'MACD', 'signal_Line', 'RSI', 'SMA', 'EMA']
        self.fill_data()
        # self.run()

    def run(self):
        t1 = Thread(target=self.update_data, daemon=True)
        t1.start()

    def get_data(self):
        df = pd.DataFrame(self.data)
        df.set_index('Datetime', inplace=True)
        return df

    def fill_data(self, amt=240):
        for i in self.columns:
            self.data[i] = [round(r.uniform(1.1, 1.3), 4) for i in range(amt)]
        self.data['Datetime'] = [datetime.datetime.now()-datetime.timedelta(minutes=i) for i in range(amt-1,-1,-1)]

    def update_data(self):
        while True:
            time.sleep(60)
            data = self.data.copy()
            for i in self.columns:
                data[i].append(data[i].pop(0))
            data['Datetime'].pop(0)
            data['Datetime'].append(data['Datetime'][-1]+datetime.timedelta(minutes=1))

    def SMA(self, data, period=30, column='Close'):
        # Create the Simple Moving Average (SMA)
        return data[column].rolling(window=period).mean()

    # Create the Exponential Moving Average (EMA)
    def EMA(self, data, period=20, column='Close'):
        return data[column].ewm(span=period, adjust=False).mean()

    # Create a function to calculate the Moving Average Convergence / Divergence (MACD)
    def MACD(self, data, period_long=26, period_short=12, period_signal=9, column='Close'):
        # Calculate the Short Term EMA
        ShortEMA = self.EMA(data, period=period_short, column=column)
        # Calculate the Long Term EMA
        LongEMA = self.EMA(data, period=period_long, column=column)
        # Calculate and store the MACD into the data frame
        data['MACD'] = ShortEMA - LongEMA

        # Calculate the signal line and store it in a data frame
        data['signal_Line'] = self.EMA(data, period=period_signal, column='MACD')

        return data

    # Create a Function to calculate the Relative Strength Index (RSI)
    def RSI(self, data, period=14, column='Close'):
        delta = data[column].diff(1)
        delta = delta.dropna()
        up = delta.copy()
        down = delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        data['up'] = up
        data['down'] = down
        AVG_Gain = self.SMA(data, period, column='up')
        AVG_Loss = abs(self.SMA(data, period, column='down'))
        RS = AVG_Gain / AVG_Loss
        RSI = 100.0 - (100.0 / (1.0 + RS))

        data['RSI'] = RSI
        return data

    def data_preparation(self):
        my_data = self.get_data()
        # Add the indicators to the data set
        my_data = self.MACD(my_data)
        my_data = self.RSI(my_data)
        my_data['SMA'] = self.SMA(my_data)
        my_data['EMA'] = self.EMA(my_data)

        # Create the Target column
        my_data['Target'] = np.where(my_data['Close'].shift(-1) > my_data['Close'], 1, 0)

        my_data = my_data.dropna()

        # Split the data set into a feature or independent data set (X) and a Target or dependent data set (Y)
        X = my_data[self.keep_columns].values[:-1]
        Y = my_data['Target'].values[:-1]

        return X, Y, my_data


# stock = Stock()
