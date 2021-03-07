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

    def add_stock(self, name):
        self.record[name.upper()] = Manager(name=name)
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

@app.route('/')
@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        req_var = dict(request.form)
        results = record_manager.search(data=req_var['search'], search_type=req_var['kind'])
        return render_template('search.html', results=results)
    else:
        return render_template('search.html', results=None)


@app.route('/display/<path:tik>')
def get_display(tik):
    trade_obj = record.get(tik.upper().strip())
    if trade_obj:
        return jsonify(trade_obj.get_display_data()),200
    else:
        record_manager.add_stock(name=tik)
        return jsonify(record_manager.get_display(name=tik)),200


if __name__ == '__main__':
    app.run(debug=True)

