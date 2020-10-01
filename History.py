import requests
import json
import pandas as pd
import yfinance as yf
from drawnow import *
import matplotlib.pyplot as plt
import pandas_datareader as web
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import time


class TradeHistory:
    def __init__(self, name):
        self.ticker_api = 'https://trade-ticker.herokuapp.com/'
        self.name = name
        self.ticker = self.get_ticker_symbol()

    def get_ticker_symbol(self):
        payload = {'name': self.name, 'kind': 'match'}
        r = requests.get(self.ticker_api+'ticker', params=payload)
        return json.loads(r.content)[0]['Ticker']

    def get_data(self, length='30m', increment='1m'):
        # https://www.youtube.com/watch?v=bMElPqhGdUA&list=PLaYT64KWZAEOOf3FnrYZKrm0GW7--go_a&index=4
        stock = yf.Ticker(self.ticker)
        return stock.history(length, increment)

    def moving_avg(self):
        # Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        d = [['30m', '1m'], ['60m', '2m'], ['15m', '1m']]
        for i in d:
            data = self.get_data(i[0], i[1])
            data['avg'] = data.Close.rolling(5).mean()
            data['high'] = data.Close.rolling(5).max()
            data['low'] = data.Close.rolling(5).min()
            data['%ofH'] = round(data['Close'] / data['high'], 2)
            print(f'{i} -> \n', data)
            self.plot(lines=['Close', 'avg', 'high', 'low'], data=data)

    def plot(self, lines, data):
        data[lines].plot()
        plt.show()

    def real_time_obj(self):
        return web.av.forex.AVForexReader(symbols=self.name, retry_count=3, pause=0.1, session=None)

    def real_time_dict(self):
        return web.data.get_quote_yahoo(self.ticker).to_dict('records')

    @staticmethod
    def max_value(data):
        return data.max().to_dict('records')


class PredictFlow:
    """:key
    Predicts the direction of flow of the stock
    it predicts if the stock would go up or down
    returns down, up or stable as results
    """
    def __init__(self, name):
        self.name = name
        self.model = None
        self.stock = TradeHistory(name=self.name)
        self.increment = 3

    def get_data(self):
        return self.stock.get_data(length='4hr', increment='1m')

    def get_price_trend(self):
        df = self.get_data()
        df['Price_trend'] = np.where(df['Close'].shift(-1) > df['Close'], 1, -1)
        df['Price_trend'] = np.where(df['Close'].shift(-1) == df['Close'], 0, df['Price_trend'])
        return df.iloc[:, df.shape[1] - 1].values

    def data_prep(self):
        # split data into feature and target
        price_trend = self.get_price_trend()
        x_train = []
        y_train = []
        for i in range(self.increment, len(price_trend)):
            x_train.append(price_trend[i - self.increment:i])
            y_train.append(price_trend[i])

        # Split the data again but this time into 80% training and 20% testing data sets
        return train_test_split(x_train, y_train, test_size=0.2)

    def get_model(self):
        X_train, X_test, Y_train, Y_test = self.data_prep()
        # Create and train the model (DecisionTreeClassifier)
        self.model = DecisionTreeClassifier().fit(X_train, Y_train)

        # Show how well the model did on the test data set
        print("Prediction Score ->", self.model.score(X_test, Y_test))

    def predict_next(self):
        keys = {1: 'up', -1: 'down', 0: 'stable'}
        data = self.get_price_trend()
        if not self.model:
            self.get_model()
        result = self.model.predict([data[-self.increment:]])
        return keys[result[0]]


class TradingSignal:
    """
    # Money flow index helps to determine when to buy or sell stock
    # money flow index over 80 is considered over bought which is an indication to sell
    # and a money flow index below 20 is considered over sold which is an indication to buy
    # money flow index of 90 and 10 are used as thresholds
    # this program determines when to buy or sell
    """
    def __init__(self, name):
        self.name = name
        self.stock = TradeHistory(name=self.name)
        self.period = 60
        self.data = self.get_data()
        self.high = 85
        self.low = 25

    def get_data(self, length='4hr'):
        return self.stock.get_data(length=length, increment='1m')

    def money_flow(self):
        self.data = self.get_data()
        return (self.data['Close'] + self.data['High'] + self.data['Low']) / 3

    def money_flow_index(self):
        money_flow = self.money_flow()

        positive_flow = []
        negative_flow = []

        # Loop through the typical price
        for i in range(1, len(money_flow)):
            if money_flow[i] > money_flow[i - 1]:
                positive_flow.append(money_flow[i - 1])
                negative_flow.append(0)
            elif money_flow[i] < money_flow[i - 1]:
                negative_flow.append(money_flow[i - 1])
                positive_flow.append(0)
            else:
                positive_flow.append(0)
                negative_flow.append(0)

        # Get all of the positive and negative money flows within the time period
        positive_mf = []
        negative_mf = []

        for i in range(self.period - 1, len(positive_flow)):
            positive_mf.append(sum(positive_flow[i + 1 - self.period: i + 1]))

        for i in range(self.period - 1, len(negative_flow)):
            negative_mf.append(sum(negative_flow[i + 1 - self.period: i + 1]))

        # Calculate the money flow index
        mfi = 100 * (np.array(positive_mf) / (np.array(positive_mf) + np.array(negative_mf)))

        new_df = self.data[self.period:]
        new_df['MFI'] = mfi
        return new_df

    def get_signal(self):
        buy_signal = []
        sell_signal = []
        data = self.money_flow_index()
        for i in range(len(data['MFI'])):

            if data['MFI'][i] > self.high:
                buy_signal.append(0)
                sell_signal.append(data['Close'][i])

            elif data['MFI'][i] < self.low:
                buy_signal.append(data['Close'][i])
                sell_signal.append(0)
            else:
                sell_signal.append(0)
                buy_signal.append(0)
        return buy_signal, sell_signal, data

    def determine_signal(self):
        buy, sell, my_data = self.get_signal()
        result = {'buy': buy[-1], 'sell': sell[-1]}
        if buy[-1] != np.nan:
            print('type ->', type(buy[-1]), buy[-1])
            return 'buy', result
        elif sell[-1] != np.nan:
            return 'sell', result
        else:
            return 'wait', result

    def plot(self):
        plt.figure(figsize=(12.2, 4.5))
        buy, sell, new_df = self.get_signal()
        print(len(buy), len(sell), len(new_df))
        new_df.index = pd.to_datetime(new_df.index.astype(str).str.slice(0, 19), format='%Y-%m-%d %H:%M:%S')

        my_df = pd.DataFrame({'date': new_df.index, 'buy': buy, 'sell': sell})

        my_df.set_index('date')
        my_buy = my_df.loc[my_df.buy != 0, :]
        my_sell = my_df.loc[my_df.sell != 0, :]
        print(my_buy)
        print(my_sell)

        plt.plot(new_df['Close'], label='Close Price', alpha=0.5)

        plt.scatter(my_buy.index, my_buy.buy, color='green', label='Buy Signal', marker='^', alpha=1)
        plt.scatter(my_sell.index, my_sell.buy, color='red', label='Sell Signal', marker='v', alpha=1)
        #plt.scatter(new_df.index, sell, color='red', label='Sell Signal', marker='v', alpha=1)
        plt.title(f'{self.name} Close Price')
        plt.xlabel('Date')
        plt.ylabel('Close Price')
        plt.legend()
        # plt.show()

        # EURUSD=X
t_name = 'EUR/USD'
# da = TradeHistory('EUR/USD')
# df = da.get_data(length='4hr', increment='1m')
# df.to_csv('test.csv')
# da.moving_avg()
# print(da.real_time_obj().read())
# print(da.real_time_dict())

#print(PredictFlow('EUR/USD').predict_next())

ts = TradingSignal(t_name)
print(ts.determine_signal())
#
while True:
    drawnow(ts.plot)
    time.sleep(2)
# ts.plot()
