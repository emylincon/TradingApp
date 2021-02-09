import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report


class Trade:
    def __init__(self):
        pass
df = pd.read_csv('test.csv')
# https://www.youtube.com/watch?v=UsPIDNmiSDM&ab_channel=ComputerScience
#Createl functions to calculate the Simple Moving Average (SMA) & the Exponential Moving Average (EMA)
#Typical time periods for moving averages are 15, 20, & 30
#Create the Simple Moving Average (SMA)

def SMA(data, period=30, column='Close'):
    return data[column].rolling(window=period).mean()

#Create the Exponential Moving Average (EMA)
def EMA(data, period=20, column='Close'):
    return data[column].ewm(span=period, adjust=False).mean()


#Create a function to calculate the Moving Average Convergence / Divergence (MACD)
def MACD(data, period_long=26, period_short=12, period_signal=9, column='Close'):
    #Calculate the Short Term EMA
    ShortEMA = EMA(data, period=period_short, column=column)
    # Calculate the Long Term EMA
    LongEMA = EMA(data, period=period_long, column=column)
    # Calculate and store the MACD into the data frame
    data['MACD'] = ShortEMA - LongEMA

    # Calculate the signal line and store it in a data frame
    data['signal_Line'] = EMA(data, period=period_signal, column='MACD')

    return data


# Create a Function to calculate the Relative Strength Index (RSI)
def RSI(data, period=14, column='Close'):
    delta = data[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    data['up'] = up
    data['down'] = down
    AVG_Gain = SMA(data, period, column='up')
    AVG_Loss = abs(SMA(data, period, column='down'))
    RS = AVG_Gain / AVG_Loss
    RSI = 100.0 - (100.0 / (1.0 + RS))

    data['RSI'] = RSI
    return data


#Add the indicators to the data set
MACD(df)
RSI(df)
df['SMA'] = SMA(df)
df['EMA'] = EMA(df)

#Create the Target column
df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
# df = df[:29]
df = df.dropna()

#Split the data set into a feature or independent data set (X) and a Target or dependent data set (Y)
keep_columns = ['Close', 'MACD', 'signal_Line', 'RSI', 'SMA', 'EMA']
X = df[keep_columns].values
Y = df['Target'].values

#Split the data again but this time into 80% training and 20% testing data sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

#Create and train the decision tree classifier model
tree = DecisionTreeClassifier().fit(X_train, Y_train)

#Check how well the model did on the training data set
print(tree.score(X_train, Y_train))


#Check how well the model did on the testing data set
print(tree.score(X_test, Y_test))


#Show the model tree predicitons
tree_predictions = tree.predict(X_test)
print(tree_predictions)

#Show the actual values from the test data
print(Y_test)

#Get the models metrics
print(classification_report(Y_test, tree_predictions))









