#!/usr/bin/env python3

from flask import Flask, jsonify
from enum import Enum
from .irrp import IRRemoteControl, IROption
from .bme280i2c import get_weather
from .tsl2572 import get_lux


# use Flask
app = Flask(__name__)


@app.route('/', methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
    })


@app.route('/weather', methods=["GET"])
def weather():
    try:
        weather = get_weather()
        return jsonify(weather)
    except:
        return jsonify({
            "status": "error",
        })


@app.route('/lux', methods=["GET"])
def lux():
    try:
        lux = get_lux()
        return jsonify(lux)
    except:
        return jsonify({
            "status": "error",
        })


@app.route('/command/<string:name>', methods=["POST"])
def command(name):
    # body = request.get_json()
    try:
        option: IROption = IROption(id=Opt.value_of(name),
                                    gpio=13,
                                    file='./codes.json')
        irRemocon = IRRemoteControl(option)
        irRemocon.playbook()
        return jsonify({
            "status": "ok",
        })
    except:
        return jsonify({
            "status": "error",
        })


class Opt(Enum):
    lightOn = 'light::on'
    lightOff = 'light::off'
    lightBright = 'light::bright'
    lightDark = 'light::dark'
    lightWarm = 'light::warm'
    lightWhite = 'light::white'

    @classmethod
    def value_of(cls, target: str):
        for e in Opt:
            if e.name == target:
                return e.value
        raise ValueError('{} は有効な値はありません'.format(target))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
