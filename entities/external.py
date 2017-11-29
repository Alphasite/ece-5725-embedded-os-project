"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""
import threading
from queue import Queue

from math import sqrt

import os
from pygame.time import Clock

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import Mock
    GPIO = Mock()

import serial

# if "DEBUG" in os.environ:
#     debug = True
# else:
#     debug = False
debug = False

class Servo:
    zero_pulse_width = 1.5
    maximum_pulse_width_range = 0.2

    def __init__(self, servo_pin) -> None:
        self.pulse_width = Servo.zero_pulse_width

        GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(servo_pin, self.frequency)
        self.start()

    def set_pwm(self):
        self.pwm.ChangeFrequency(self.frequency)
        self.pwm.ChangeDutyCycle(self.duty_cycle)

    def stop(self):
        self.pwm.stop()

    def start(self):
        self.pwm.start(self.duty_cycle)

    @property
    def speed(self):
        return (self.pulse_width - Servo.zero_pulse_width) / Servo.maximum_pulse_width_range

    @speed.setter
    def speed(self, value):
        self.pulse_width = value * Servo.maximum_pulse_width_range + Servo.zero_pulse_width
        self.set_pwm()

    @property
    def period(self):
        """The millisecond period of the pwm signal"""
        return 20 + self.pulse_width

    @property
    def frequency(self):
        return 1 / (self.period / 1000)

    @property
    def duty_cycle(self):
        return (self.pulse_width / self.period) * 100


class SerialChannel:
    def __init__(self, serial_path: str, pwm_duty_cycle: float, pwm_period: float) -> None:
        if not debug:
            self.serial = serial.Serial(serial_path, 9600, timeout=1)
        else:
            self.serial = None

        self.pwm_outputs = [PWMOutput(self, i, pwm_period, pwm_duty_cycle) for i in range(4)]
        self.digital_outputs = [DigitalOutput(self, i, False) for i in range(4)]
        self.analog_inputs = [AnalogInput(self, i) for i in range(4)]

        self.lock = threading.RLock()

        self.inputs = Queue()

    def send(self, string: str) -> str:
        with self.lock:
            print("Request:", string)

            if debug:
                return

            string += "\n"
            string = string.encode('ascii')
            self.serial.write(string)

            serial.time.sleep(0.002)

            response = self.serial.readline().decode().strip()

            print("Response:", response)

            return response


class PWMOutput:
    def __init__(self, serial_channel: SerialChannel, index: int, period: float, duty_cycle: float) -> None:
        self.serial_channel = serial_channel
        self.index = index
        self._period = period
        self._duty_cycle = duty_cycle

    def _update(self):
        self.serial_channel.send("/pwm{pin}/{period}".format(
            pin=self.index,
            period=self._period,
        ))

        self.serial_channel.send("/pwm{pin}/{duty}".format(
            pin=self.index,
            duty=self._duty_cycle
        ))

    @property
    def duty_cycle(self) -> float:
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, value: float):
        self._duty_cycle = value
        self._update()

    @property
    def period(self) -> float:
        return self._period

    @period.setter
    def period(self, value: float):
        self._period = value
        self._update()


class DigitalOutput:
    def __init__(self, serial_channel: SerialChannel, index: int, value: bool) -> None:
        self.serial_channel = serial_channel
        self.index = index
        self._value = value

    def _update(self):
        if self._value:
            pin_value = 1
        else:
            pin_value = 0

        self.serial_channel.send("/digital{pin}/write {value}".format(
            pin=self.index,
            value=pin_value,
        ))

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, value: bool):
        self._value = value
        self._update()


class AnalogInput:
    def __init__(self, serial_channel: SerialChannel, index: int) -> None:
        self.serial_channel = serial_channel
        self.index = index

    @property
    def value(self) -> float:
        result = ''

        with self.serial_channel.lock:
            while len(result) == 0:
                result = self.serial_channel.send("/analog{0}/read".format(self.index))

        return float(result)


class Actuator:
    MAXIMUM_POSITION_ERROR = 0.001
    MAXIMUM_VELOCITY_ERROR = 0.001

    def __init__(self, channel: SerialChannel, index: int, min_value: float, max_value: float):
        self.index = index
        self.channel = channel
        self.min_value = min_value
        self.max_value = max_value
        self.previous_position = self.position
        self.target_position = self.position

    @property
    def position(self) -> float:
        width = self.max_value - self.min_value
        value = self.channel.analog_inputs[self.index].value - self.min_value
        return value / width

    @position.setter
    def position(self, value: float):
        self.target_position = value

    @property
    def reverse(self):
        return self.channel.digital_outputs[self.index].value

    @reverse.setter
    def reverse(self, value):
        self.channel.digital_outputs[self.index].value = value

    @property
    def duty_cycle(self):
        return self.channel.pwm_outputs[self.index].duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, value):
        self.channel.pwm_outputs[self.index].duty_cycle = value

    @property
    def stalled(self):
        return False

    def update(self, frame_time_s: float):
        position_delta = self.target_position - self.position

        # Don't bother moving if we're close to the target position
        if abs(position_delta) > Actuator.MAXIMUM_POSITION_ERROR:
            target_velocity = sqrt(1 + abs(position_delta)) - 1
            velocity_delta = target_velocity - self.duty_cycle

            target_velocity_delta = sqrt(1 + abs(velocity_delta)) - 1

            # Don't bother adjusting speed if we're close to the target speed
            if abs(target_velocity_delta) > Actuator.MAXIMUM_VELOCITY_ERROR:
                self.duty_cycle += target_velocity_delta * frame_time_s
                self.reverse = position_delta >= 0
        else:
            self.duty_cycle = 0
            self.reverse = False


class ActuatorController:
    target_framerate = 60

    def __init__(self, serial_path: str) -> None:
        self.channel = SerialChannel(serial_path, 0.5, 1/10000)
        self.actuators = [Actuator(self.channel, i, 0, 1) for i in range(4)]

        self.running = True
        self.thread = threading.Thread(target=lambda: self.updater_thread())
        self.thread.start()

    def updater_thread(self):
        clock = Clock()

        while self.running:
            frame_time_ms = clock.tick(ActuatorController.target_framerate)
            frame_time_s = frame_time_ms / 1000

            for actuator in self.actuators:
                actuator.update(frame_time_s)

    def quit(self):
        self.running = False
