import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from History import TradeHistory
import time


class Trade:
    def __init__(self, name):
        self.name = name
        self.stock = TradeHistory(name=self.name)
        self.data = None
        self.classifier = None
        self.keep_columns = ['Close', 'MACD', 'signal_Line', 'RSI', 'SMA', 'EMA']
        self.accuracy = {'train': 0, 'test': 0}

    def get_data(self, length='4hr'):
        return self.stock.get_data(length=length, increment='1m')

    def set_data(self, length='4hr'):
        self.data = self.get_data(length)

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
        # Add the indicators to the data set
        self.set_data()
        self.MACD(self.data)
        self.RSI(self.data)
        self.data['SMA'] = self.SMA(self.data)
        self.data['EMA'] = self.EMA(self.data)

        # Create the Target column
        self.data['Target'] = np.where(self.data['Close'].shift(-1) > self.data['Close'], 1, 0)

        self.data = self.data.dropna()

        # Split the data set into a feature or independent data set (X) and a Target or dependent data set (Y)
        X = self.data[self.keep_columns].values[:-1]
        Y = self.data['Target'].values[:-1]

        return X, Y

    def get_model(self):
        X, Y = self.data_preparation()
        # Split the data again but this time into 80% training and 20% testing data sets
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

        if not self.classifier:
            # Create and train the decision tree classifier model
            self.classifier = DecisionTreeClassifier().fit(X_train, Y_train)

            # Check how well the model did on the training data set
            self.accuracy['train'] = self.classifier.score(X_train, Y_train)

            # Check how well the model did on the testing data set
            self.accuracy['test'] = self.classifier.score(X_test, Y_test)
        else:
            # Create and train the decision tree classifier model
            tree = DecisionTreeClassifier().fit(X_train, Y_train)

            # Check how well the model did on the training data set
            train = tree.score(X_train, Y_train)

            # Check how well the model did on the testing data set
            test = tree.score(X_test, Y_test)

            if test > self.accuracy['test']:
                self.classifier, self.accuracy['train'], self.accuracy['test'] = tree, train, test

    def predict(self):
        self.get_model()
        last = self.data[self.keep_columns].values[-1]
        return self.classifier.predict([last])[0]


class Table:
    def __init__(self):
        self.last_close = None
        self.last_prediction = None
        self.right = 0
        self.predictions = pd.DataFrame(None, columns=['Datetime', 'Actual', 'Predicted'])

    def set_close_prediction(self, close, prediction):
        self.last_close = close
        self.last_prediction = prediction

    def add_row(self, datetime, close):
        if self.last_close:
            actual = 1 if close > self.last_close else 0
            self.predictions.append({'Datetime': datetime, 'Actual': actual, 'Prediction': self.last_prediction})
            self.right += 1 if actual == self.last_prediction else self.right

    def score(self):
        round((self.right/len(self.predictions))*100, 2)


t_name = 'EUR/USD'
my_trade = Trade(name=t_name)
print(my_trade.predict())








