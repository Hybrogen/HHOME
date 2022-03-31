#-*- coding:utf-8 -*-

import time

import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

class HRELAY(object):
    def __init__(self, pin: int, trigger: bool = False):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.trigger = trigger
        self.run(not trigger)

    def set_pin(self, pin: int):
        GPIO.cleanup()
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def run(self, state: bool):
        GPIO.output(self.pin, state == self.trigger)

    def check(self) -> bool:
        return GPIO.input(self.pin) == self.trigger

    def __del__(self):
        GPIO.cleanup()

class SteeppingMOTOR(object):
    def __init__(self, pins: list):
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)
        self.phases = [
                [1, 0, 0, 1], # 1
                [1, 0, 0, 0], # 2
                [1, 1, 0, 0], # 3
                [0, 1, 0, 0], # 4
                [0, 1, 1, 0], # 5
                [0, 0, 1, 0], # 6
                [0, 0, 1, 1], # 7
                [0, 0, 0, 1], # 8
                ]

    def run(self, mode: bool, run_duration: int = 3):
        stime = time.time()
        while int(time.time() - stime) < run_duration:
            for phase in (self.phases if mode else self.phases[::-1]):
                for pin, state in zip(self.pins, phase):
                    GPIO.output(pin, state)
                time.sleep(0.001)
        for pin in self.pins: GPIO.output(pin, False)

    def set_pin(self, pins: list):
        GPIO.cleanup()
        self.pins = pins
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def __del__(self):
        GPIO.cleanup()

if __name__ == '__main__':
    '''
    a = HRELAY(4)
    print(a.check())
    a.set_output(True)
    print(a.check())
    a.set_output(False)
    print(a.check())
    '''
    s = SteeppingMOTOR([6, 13, 19, 26])
    s.run(True)
    s.run(False, 10)

