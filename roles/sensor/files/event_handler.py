#!/usr/bin/env python3

import argparse
import pigpio
import os
import time
from datetime import datetime


class PigpioFactory:
    LED_GREEN = 17
    LED_YELLOW = 18
    LED_BLUE = 22
    LED_WHITE = 27
    SWITCH_RED = 5
    SWITCH_BLACK = 6

    def __init__(self):
        self.pi = pigpio.pi()
        # self.pi.set_mode(self.LED_GREEN, pigpio.OUTPUT)
        # self.pi.set_mode(self.LED_YELLOW, pigpio.OUTPUT)
        # self.pi.set_mode(self.LED_BLUE, pigpio.OUTPUT)
        # self.pi.set_mode(self.LED_WHITE, pigpio.OUTPUT)

    def __del__(self):
        self.pi.stop()

    # decorator
    def check_connection(func):
        def wrapper(*args, **kwargs):
            _self = args[0]
            if not _self.pi.connected:
                raise RuntimeError('Pigpio Connection Failed')
            func(*args, **kwargs)
        return wrapper

    @check_connection
    def on_green(self):
        self.pi.write(self.LED_GREEN, 1)

    @check_connection
    def off_green(self):
        self.pi.write(self.LED_GREEN, 0)

    @check_connection
    def on_yellow(self):
        self.pi.write(self.LED_YELLOW, 1)

    @check_connection
    def off_yellow(self):
        self.pi.write(self.LED_YELLOW, 0)

    @check_connection
    def on_blue(self):
        self.pi.write(self.LED_BLUE, 1)

    @check_connection
    def off_blue(self):

        self.pi.write(self.LED_BLUE, 0)

    @check_connection
    def on_white(self):
        self.pi.write(self.LED_WHITE, 1)

    @check_connection
    def off_white(self):
        self.pi.write(self.LED_WHITE, 0)

    @check_connection
    def click_on_red_switch(self, func):
        self.__loop(self.SWITCH_RED, func)

    @check_connection
    def click_on_black_switch(self, func):
        self.__loop(self.SWITCH_BLACK, func)

    def __loop(self, switch: str, func):
        self.pi.set_mode(switch, pigpio.INPUT)
        self.pi.set_pull_up_down(switch, pigpio.PUD_UP)
        try:
            while True:
                switch_state = self.pi.read(switch)
                if 0 == switch_state:
                    print(f'{datetime.now()} event fired.')
                    func()
                else:
                    pass
                time.sleep(0.20)
        except KeyboardInterrupt:
            print(f'{datetime.now()} loop stopped.')


def reboot():
    p = PigpioFactory()

    def event_handler():
        p.on_yellow()
        os.system("sudo shutdown -r 1")
        time.sleep(3)
        p.off_yellow()

    p.click_on_red_switch(event_handler)


def health_check():
    p = PigpioFactory()

    def event_handler():
        p.on_green()
        time.sleep(3)
        p.off_green()

    p.click_on_black_switch(event_handler)


### Use python command, call a function directly ####
# python -c "import event_handler; event_handler.health_check()"
# However, it seems that xxx.py must be in the current directory...


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('function_name',
                        type=str,
                        help='set fuction name in this file')
    args = parser.parse_args()

    # get functions in this file.
    func_dict = {k: v for k, v in locals().items() if callable(v)}
    # run function
    func_dict[args.function_name]()
