#!/usr/bin/env python3

from flask import Flask, jsonify
from flask_cors import CORS
from enum import Enum
from send import InfraredSender, IROption
from bme280i2c import get_weather
from tsl2572 import get_lux

app = Flask(__name__)
CORS(app)


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
    except RuntimeError as e:
        return internal_server_error(e)


@app.route('/lux', methods=["GET"])
def lux():
    try:
        lux = get_lux()
        return jsonify(lux)
    except RuntimeError as e:
        return internal_server_error(e)

@app.route('/command/list', methods=["GET"])
def get_all_commands():
    res = {
        "commands": Opt.all_name()
    }
    return res, 200

@app.route('/command/<string:name>', methods=["POST"])
def command(name):
    # body = request.get_json()
    try:
        option: IROption = IROption(
            id=Opt.value_of(name),
            gpio=13,
            file='./codes.json')

        sender = InfraredSender(option)
        sender.run()
        return jsonify({
            "status": "ok",
        })

    except RuntimeError as e:
        return internal_server_error(e)

    except ValueError as e:
        return bad_request(e)


def internal_server_error(error: RuntimeError):
    res = jsonify({
        "error": {
            "name": "RuntimeError",
            "description": error.args[0]
        }
    })
    return res, 500


def bad_request(error: ValueError):
    res = jsonify({
        "error": {
            "name": "ValueError",
            "description": error.args[0]
        }
    })
    return res, 400


class Opt(Enum):
    lightOn = 'light::on'
    lightOff = 'light::off'
    lightBright = 'light::bright'
    lightDark = 'light::dark'
    lightWarm = 'light::warm'
    lightWhite = 'light::white'
    airDehumidifying = 'air::Dehumidifying'
    airCooling = 'air::cooling'
    airHeating = 'air::heating'
    airOff = 'air::off'
    circulatorPower = 'circulator::power'
    circulatorSpin = 'circulator::spin'
    circulatorUp = 'circulator::up'
    circulatorDown = 'circulator::down'

    @classmethod
    def value_of(cls, target: str):
        for e in Opt:
            if e.name == target:
                return e.value
        raise ValueError(f'{target} is not an available command')

    @classmethod
    def all_name(cls):
        return [e.name for e in Opt]

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
