import datetime
import pandas as pd
import random as r
import time
from threading import Thread


class Stock:
    def __init__(self):
        self.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        self.data = {}
        self.fill_data()
        self.run()

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


# stock = Stock()
