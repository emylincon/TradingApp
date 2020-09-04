import requests
import json
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas_datareader as web


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


# EURUSD=X
da = TradeHistory('EUR/USD')
da.moving_avg()
print(da.real_time_obj().read())
print(da.real_time_dict())