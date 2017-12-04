"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

from __future__ import division, print_function

import threading
import time
import os
import serial

from entities.entity import Entity

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = Mock()

if "DEBUG" in os.environ:
    debug = True
else:
    debug = False

debug = False


class Servo(object):
    zero_pulse_width = 1.5
    maximum_pulse_width_range = 0.2

    def __init__(self, servo_pin):
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


class SerialChannel(object):
    def __init__(self, serial_path, pwm_duty_cycle, pwm_period):
        if not debug:
            self.serial = serial.Serial(serial_path, 57600)
        else:
            self.serial = None

        self.pwm_outputs = [PWMOutput(self, i, pwm_period, pwm_duty_cycle) for i in range(4)]
        self.digital_outputs = [DigitalOutput(self, i, False) for i in range(4)]
        self.analog_inputs = [AnalogInput(self, i) for i in range(4)]

        self.lock = threading.RLock()

    def send(self, string):
        with self.lock:
            # print("Request:", string)

            if debug:
                return ""

            string += "\n"
            string = string.encode('ascii')
            self.serial.write(string)

            response = self.serial.readline().decode().strip()

            # print("Response:", response)

            return response


class PWMOutput(object):
    def __init__(self, serial_channel, index, period, duty_cycle):
        self.serial_channel = serial_channel
        self.index = index
        self.period = period
        self.old_period = None
        self.duty_cycle = duty_cycle
        self.old_duty_cycle = None

    def refresh(self):
        if self.period != self.old_period:
            self.old_period = self.period

            self.serial_channel.send("/pwm{pin}/period {period}".format(
                pin=self.index,
                period=self.period,
            ))

        if self.duty_cycle != self.old_duty_cycle:
            self.old_duty_cycle = self.duty_cycle

            self.serial_channel.send("/pwm{pin}/write {duty}".format(
                pin=self.index,
                duty=self.duty_cycle
            ))


class DigitalOutput(object):
    def __init__(self, serial_channel, index, value):
        self.serial_channel = serial_channel
        self.index = index
        self.value = value
        self.old_value = None

    def refresh(self):
        if self.value != self.old_value:
            if self.value:
                pin_value = 1
            else:
                pin_value = 0

            self.serial_channel.send("/digital{pin}/write {value}".format(
                pin=self.index,
                value=pin_value,
            ))

            self.old_value = self.value


class AnalogInput(object):
    def __init__(self, serial_channel, index):
        self.serial_channel = serial_channel
        self.index = index
        self.value = 0.0

    def refresh(self):
        result = ''

        with self.serial_channel.lock:
            while len(result) == 0:
                result = self.serial_channel.send("/analog{0}/read".format(self.index))

        self.value = float(result)


class Actuator(object):
    MAXIMUM_POSITION_ERROR = 0.1
    MAXIMUM_VELOCITY_ERROR = 0.002

    def __init__(self, channel, index, min_value, max_value):
        self.index = index
        self.channel = channel
        self.min_value = min_value
        self.max_value = max_value
        self.previous_position = self.position
        self._target_position = None
        self.target_position = self.position
        self.stopped = True
        self.seconds_frozen = 0
        self.previous_delta = 0.0

    @property
    def target_position(self):
        return self._target_position

    @target_position.setter
    def target_position(self, value):
        if self.target_position != value:
            self.seconds_frozen = 0

        self._target_position = value

    @property
    def position(self):
        width = self.max_value - self.min_value
        value = self.channel.analog_inputs[self.index].value - self.min_value
        return value / width

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
        return self.seconds_frozen > 2

    def update(self, frame_time_s):
        position_delta = self.target_position - self.position

        target_velocity = min((position_delta * 6) ** 2, 1)
        velocity_delta = target_velocity - self.duty_cycle

        target_velocity_delta = velocity_delta

        # Don't bother moving if we're close to the target position
        if abs(position_delta) > Actuator.MAXIMUM_POSITION_ERROR and not self.stopped and not self.stalled:
            # stall detection
            if abs(position_delta - self.previous_delta) < 0.001:
                print(self.seconds_frozen)
                self.seconds_frozen += frame_time_s
            else:
                self.seconds_frozen = 0

            self.previous_delta = position_delta

            # Don't bother adjusting speed if we're close to the target speed
            if abs(target_velocity_delta) > Actuator.MAXIMUM_VELOCITY_ERROR:
                self.duty_cycle += target_velocity_delta * (frame_time_s * 2)
                self.reverse = position_delta < 0

                # print("Target p:", self.target_position)
                # print("Actual p:", self.position)
                # print("Target v:", target_velocity)
                # print("Actual v:", self.duty_cycle)
                # print("Target d:", target_velocity_delta)

        else:
            self.stopped = True
            self.duty_cycle = 0
            self.reverse = False


class ActuatorController(Entity):
    target_framerate = 30

    def __init__(self, serial_path):
        self.channel = SerialChannel(serial_path, 0.5, 1/200)
        self.actuators = [Actuator(self.channel, i, 0.3/3.3, 3.0/3.3) for i in range(4)]

        self.running = True
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=lambda: self.updater_thread())
        self.thread.start()

    def updater_thread(self):
        previous_time = time.time()

        while self.running:
            current_time = time.time()
            frame_time_s = current_time - previous_time
            previous_time = current_time

            # print("Frametime:", frame_time_s)

            for analogin in self.channel.analog_inputs:
                analogin.refresh()

            for actuator in self.actuators:
                actuator.update(frame_time_s)

            for digitalout in self.channel.digital_outputs:
                digitalout.refresh()

            for pwmout in self.channel.pwm_outputs:
                pwmout.refresh()

    def quit(self):
        self.running = False

    def update(self, loop, time_delta):
        for actuator in self.actuators:
            actuator.update(time_delta)
