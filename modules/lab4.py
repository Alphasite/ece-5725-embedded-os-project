"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 4, Lab Section 02, 01/11/17
"""

from datetime import datetime

import threading
import time
from typing import List

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("GPIO not available, mocking.")
    from unittest.mock import Mock

    GPIO = Mock()

from entities.external import Servo
from entities.loop import RunLoop
from entities.ui import Label, ModalButton, Button
from entities import red, green


def blink_pwm(settings, **kwargs):

    try:
        # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

        # Create PWM Instances
        p1 = GPIO.PWM(26, 1)  # Frequency of 1Hz
        p2 = GPIO.PWM(19, 2)  # Frequenxy of 2Hz

        # Start PWM
        p1.start(50)  # 50% Duty Cycle
        p2.start(50)  # 50% Duty Cycle

        while True:
            time.sleep(2)
    finally:
        GPIO.cleanup()


def blink_loop(settings, **kwargs):
    led_pin = 19

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW)

        frequency = int(input("Enter the frequency:"))
        period = 1.0 / frequency / 2.0

        while True:
            GPIO.output(led_pin, GPIO.HIGH)
            time.sleep(period)
            GPIO.output(led_pin, GPIO.LOW)
            time.sleep(period)
    finally:
        GPIO.cleanup()


MODULE = {
    "blink_pwm": blink_pwm,
    "blink": blink_loop,
}
