from flask import Flask, render_template, session, url_for, request, jsonify, Response

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

