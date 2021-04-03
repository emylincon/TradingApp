from flask import Flask, render_template, session, url_for, request, jsonify, Response
from Trade import Manager
import requests
app = Flask(__name__)

record = {'EUR/USD': Manager(name='EUR/USD')}


class ManageRecord:
    def __init__(self):
        self.record = record
        self.url = 'https://trade-ticker.herokuapp.com'

    def search_name(self, data, kind='match'):
        payload = {'name': data, 'kind': kind}
        return requests.get(f'{self.url}/ticker', params=payload).json()

    def search_ticker(self, data, kind='match'):
        payload = {'ticker': data, 'kind': kind}
        return requests.get(f'{self.url}/name', params=payload).json()

    def search(self, data, search_type, kind='match'):
        if search_type.lower() == 'name':
            return self.search_name(data=data, kind=kind)
        else:
            return self.search_ticker(data=data, kind=kind)

    def add_stock(self, name, ticker=None):
        self.record[name.upper()] = Manager(name=name, ticker=ticker)
        self.record[name.upper()].trade.predict()

    def get_display(self, name):
        return self.record[name.upper()].get_display_data()


record_manager = ManageRecord()
#
# @app.route('/')
# def home():
#     return render_template('index.html', ticker='EUR/USD')


@app.route('/<path:ticker>')
def dashboard(ticker):
    return render_template('index.html', ticker=ticker)


@app.route('/dashboard', methods=['POST', 'GET'])
def my_dashboard():
    if request.method == 'POST':
        data = dict(request.form)  # {'myname': 'hey', 'myticker': 'hi'}
        return render_template('index.html', ticker=data['myname'], myticker=data['myticker'])
    return render_template('search.html', results=None)


@app.route('/')
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        req_var = dict(request.form)
        results = record_manager.search(data=req_var['search'], search_type=req_var['kind'])
        return render_template('search.html', results=results)
    else:
        return render_template('search.html', results=None)


@app.route('/display', methods=['POST', 'GET'])
def get_display():
    data = request.json
    tik, ticker = data['name'], data['ticker']
    trade_obj = record.get(tik.upper().strip())
    if trade_obj:
        result = trade_obj.get_display_data()
    else:
        record_manager.add_stock(name=tik, ticker=ticker)
        result = record_manager.get_display(name=tik)

    if result:
        return jsonify(result), 200
    else:
        return render_template('error.html', name=tik), 404


if __name__ == '__main__':
    app.run(debug=True)

