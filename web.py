from flask import Flask, render_template, session, url_for, request, jsonify, Response
from Trade import Manager
app = Flask(__name__)

record = {'EUR/USD': Manager(name='EUR/USD')}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/display/<path:tik>')
def get_display(tik):
    trade_obj = record.get(tik.upper().strip())
    if trade_obj:
        return jsonify(trade_obj.get_display_data()),200
    else:
        return jsonify({'result': 'Not found'}),404


if __name__ == '__main__':
    app.run(debug=True)

