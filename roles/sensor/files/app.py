#!/usr/bin/env python3

from flask import Flask, jsonify
# from bme280i2c import get_weather
# from tsl2572 import get_lux

# use Flask
app = Flask(__name__)


@app.route('/', methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
    })


# @app.route('/weather', methods=["GET"])
# def weather():
#     return get_weather()


# @app.route('/lux', methods=["GET"])
# def lux():
#     return get_lux()


@app.route('/command',  methods=["POST"])
def command():
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
