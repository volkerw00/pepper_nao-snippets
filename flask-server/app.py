#!python/Scripts/python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'data': 'Hello, World!'})

@app.route('/hello/<string:word>', methods=['GET'])
def hello_data(word):
    return jsonify({'data': 'Hello, ' + word + '!'})

if __name__ == '__main__':
    app.run(debug=True)
