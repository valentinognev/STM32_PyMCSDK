#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 18:06:21 2022

@author: valentin
"""

import evdev
import logging
from select import select

controller_name = "Nintendo Switch Pro Controller"
#controller_name = "GamePadPlus V3 Consumer Control"


class struct:
    pass


def main():
    controller = ControllerInput(controller_name, NintendoPadIDs())
    while True:
        controller.events_get()


def NintendoPadIDs():
    buttons = {
        'LEFTx': [0, 3, 0],   # 'LEFT-X'
        'LEFTy': [1, 3, 1],   # 'LEFT-Y'
        'RIGHTy': [4, 3, 2],   # 'L2'
        'RIGHTx': [3, 3, 3],   # 'RIGHT-X'
        'CrossX': [16, 3, 4],   # 'DPAD-LEFT'
        'CrossY': [17, 3, 5],   # 'DPAD-DOWN'
        'cross': [304, 1, 0],  # 'CROSS', 'B'
        'B': [304, 1, 0],  # 'CROSS', 'B'
        'circle': [305, 1, 1],  # 'CIRCLE', 'A'
        'A': [305, 1, 1],  # 'CIRCLE', 'A'
        'triangle': [307, 1, 2],  # 'TRIANGLE', 'X'
        'X': [307, 1, 2],  # 'TRIANGLE', 'X'
        'square': [308, 1, 3],  # 'SQUARE', 'Y'
        'Y': [308, 1, 3],  # 'SQUARE', 'Y'
        'R': [311, 1, 4],  # 'R', RB', 'R1'
        'RB': [311, 1, 4],  # 'R', RB', 'R1'
        'L': [310, 1, 5],  # 'L1', LB
        'LB': [310, 1, 5],  # 'L1', LB
        'home': [316, 1, 6],  # 'home'
        'plus': [315, 1, 7],  # 'plus', 'start'
        'start': [-1,  1, 7],  # 'plus', 'start'
        'select': [314, 1, 8],  # 'SELECT', 'minus'
        'minus': [314, 1, 8],  # 'SELECT', 'Minus'
        'startT': [315, 1, 9],  # 'START', 'o'
        'o': [315, 1, 9],  # 'START', 'o'
        'LJ': [317, 1, 10],  # 'LJ', 'PS'
        'RJ': [318, 1, 11],  # 'RJ', 'L3'
        'ZL': [312, 1, 11],  # 'LT', 'ZL', R2'
        'LT': [312, 1, 11],  # 'LT', 'ZL', R2'
        'ZR': [313, 1, 12],  # 'ZR', 'RT', 'L2'
        'RT': [313, 1, 12]}  # 'ZR', 'RT', 'L2'

    return buttons


class ControllerInput():
    def __init__(self, controller_name, buttons):
        self.buttons = buttons
        self.pad = struct
        self.pad.button = [False, False, False, False, False, False, False,
                           False, False, False, False, False, False, False, False, False, False]
        self.pad.axis = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        logging.debug("Found devices: " + str(len(devices)))

        dev_location = None
        for dev in devices:
            if dev.name == controller_name:
                dev_location = dev.fn
                logging.debug("Found desired device: " +
                              dev.name + " at: " + dev.fn)
                break
        if dev_location is None:
            raise "Device not found!"

        self.dev_obj = evdev.InputDevice(dev_location)
        # self.dev_obj = evdev.InputDevice('/dev/input/event257')

    def events_get(self):
        for event in self.dev_obj.read_loop():
            if event.type != 0:
                # print(event)
                self.update(event)
                return

    def checkEvens(self):
        event = self.dev_obj.read_one()
        if event != None:
            if event.type != 0:
                self.update(event)

    def update(self, event):
        for button in self.buttons:
            if event.code == self.buttons[button][0] and event.type == 1:
                self.pad.button[self.buttons[button][2]] = event.value == 1
            if event.code == self.buttons[button][0] and event.type == 3:
                self.pad.axis[self.buttons[button][2]] = event.value
        return self.pad


if __name__ == "__main__":
    main()
