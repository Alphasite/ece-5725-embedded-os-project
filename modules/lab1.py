"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

import sys
import time

from modules.fifo import passthrough


def gpio_handler_1_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            time.sleep(0.2)
            if not GPIO.input(23):
                print("Button 23: has been pressed!")
    finally:
        GPIO.cleanup()


def gpio_handler_4_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            if not GPIO.input(17):
                print("Button 17: has been pressed!")

            if not GPIO.input(22):
                print("Button 22: has been pressed!")

            if not GPIO.input(23):
                print("Button 23: has been pressed!")

            if not GPIO.input(27):
                print("Button 27: has been pressed!")

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


def gpio_handler(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(27, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        while True:
            if not GPIO.input(17):
                passthrough(settings, command="pause")
                print("Pause Button Pressed.")

            if not GPIO.input(22):
                passthrough(settings, command="seek 1 0")
                print("Fwd x10 Button Pressed.")

            if not GPIO.input(23):
                passthrough(settings, command="seek -1 0")
                print("Rew x10 Button Pressed.")

            if not GPIO.input(27):
                passthrough(settings, command="quit")
                print("Quit Button Pressed.")
                sys.exit()

            time.sleep(0.2)
    finally:
        GPIO.cleanup()


MODULE = {
    "buttons": gpio_handler,
    "one_button": gpio_handler_1_button,
    "four_button": gpio_handler_4_button,
}
