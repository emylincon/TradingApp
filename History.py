import requests
import json
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_datareader as web
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import numpy as np


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


class Predict:
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



        # EURUSD=X
# da = TradeHistory('EUR/USD')
# da.moving_avg()
# print(da.real_time_obj().read())
# print(da.real_time_dict())

print(Predict('EUR/USD').predict_next())