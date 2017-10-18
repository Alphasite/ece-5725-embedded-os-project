"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import Mock
    GPIO = Mock()


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
