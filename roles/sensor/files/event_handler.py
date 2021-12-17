#!/usr/bin/env python3

import pigpio
import os
import time


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
    def click_on_red_switch(self, func1, func2):
        self.pi.set_mode(self.SWITCH_RED, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SWITCH_RED, pigpio.PUD_UP)
        try:
            while True:
                switch_state = self.pi.read(self.SWITCH_BLACK)
                if 0 == switch_state:
                    func1()
                    print("click on switch...")
                else:
                    func2()
                time.sleep(0.20)
                print('===========')
        except KeyboardInterrupt:
            print("stop")

    @check_connection
    def click_on_black_switch(self, func1, func2):
        self.pi.set_mode(self.SWITCH_BLACK, pigpio.INPUT)
        self.pi.set_pull_up_down(self.SWITCH_BLACK, pigpio.PUD_UP)
        try:
            while True:
                switch_state = self.pi.read(self.SWITCH_BLACK)
                if 0 == switch_state:
                    func1()
                    print("click on switch...")
                else:
                    func2()
                time.sleep(0.20)
                print('===========')
        except KeyboardInterrupt:
            print("stop")


def event1():
    p = PigpioFactory()
    p.click_on_black_switch(p.on_white, p.off_white)


if __name__ == '__main__':
    event1()
