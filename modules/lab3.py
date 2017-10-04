import random
import sys
import os
import threading
import time
from typing import Tuple, Optional, List

import pygame
from pygame.time import Clock

from modules.fifo import passthrough
import RPi.GPIO as GPIO

timestamp = time.time()

running_on_pi = True if os.getenv("DEBUG") is None else False

black = 0, 0, 0
WHITE = 255, 255, 255

screen_size = 320, 240
target_framerate = 30

point = Tuple[int, int]
colour = Tuple[int, int, int]

red = (165, 0, 0)
green = (0, 165, 0)

class Button:
    def __init__(self, center: point, text: str, action: callable, background_colour: Optional[colour] = None):
        self.action = action
        self.label = Label(center, text, background_colour)

    def update(self, screen, time_delta: float):
        self.label.update(screen, time_delta)

    def interact(self, interact_point: point):
        if self.label.rect.collidepoint(interact_point):
            self.action()


class Label:
    def __init__(self, center: point, text: str, background_colour: Optional[colour] = None):
        self.font = my_font = pygame.font.Font(None, 25)
        self.center = center
        self.text = center
        self.surface = my_font.render(text, True, WHITE)
        self.rect = self.surface.get_rect(center=center)
        self.background_colour = background_colour

    def update(self, screen, time_delta: float):
        if self.background_colour is not None:
            pygame.draw.rect(screen, self.background_colour, self.rect)

        screen.blit(self.surface, self.rect)


class ModalButton:
    def __init__(self, center: point, text_1: str, text_2: str, action_1: callable, action_2: callable):
        self.active_action = action_1
        self.disabled_action = action_2

        def swap_button():
            temp_button = self.active_button
            self.active_button = self.disabled_button
            self.disabled_button = temp_button

            temp_action = self.active_button
            self.active_button = self.disabled_button
            self.disabled_button = temp_action

            self.active_action()

        self.active_button = Button(center, text_1, swap_button, red)
        self.disabled_button = Button(center, text_2, swap_button, green)

    def update(self, screen, time_delta: float):
        self.active_button.update(screen, time_delta)

    def interact(self, interact_point: point):
        self.active_button.interact(interact_point)


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


def setup_for_pi():
    os.putenv('SDL_VIDEODRIVER', 'fbcon')  # Display on piTFT
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    # pygame.mouse.set_visible(False)

#################################

def blink(settings, **kwargs):

    #Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

    #Create PWM Instances
    p1 = GPIO.PWM(26, 1) #Frequency of 1Hz
    p2 = GPIO.PWM(19, 2) #Frequenxy of 2Hz

    #Start PWM
    p1.start(50) #50% Duty Cycle
    p2.start(50) #50% Duty Cycle

    while True:
        time.sleep(2)

    return True

def pwm_calibrate(settings, **kwargs):
    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

    # Create PWM Instances
    p1 = GPIO.PWM(26, 46.5)  # 0.020ms between pulses
    p2 = GPIO.PWM(19, 46.5)  # 0.020ms between pulses

    # Start PWM
    p1.start(7)  # 7% Duty Cycle [1.5mS signal]
    p2.start(7)  # 7% Duty Cycle [1.5mS signal]

    while True:
        time.sleep(0.2)

    return True


def servo_control(settings,**kwargs):
    GPIO.setmode(GPIO.BCM)

    #Initialize Servos
    servo1 = Servo(19)
    servo2 = Servo(26)
    servo1.speed = 0
    servo2.speed = 0

    #Begin Sequence
    print("Servo Speed Sequence Initialized.")
    time.sleep(2)

    for i in range(0,-11, -1):
        servo1.speed = i/10
        servo2.speed = i/10
        print("Servo Speed Set to:", i/10)
        time.sleep(3)

    for i in range(0, 11, 1):
        servo1.speed = i/10
        servo2.speed = i/10
        print("Servo Speed Set to:", i/10)
        time.sleep(3)

    servo1.speed = 0
    servo2.speed = 0
    print("Sequence complete. Servos stopped.")
    return True

def servo_control_beta(settings, **kwargs):

    done_semaphore = threading.Semaphore(0)

    #Default Frequency/PWM Settings
    SpeedS1 = 0
    SpeedS2 = 0
    #p1_freq = 46.5
    #p2_freq = 46.5
    #p1_pwm = 7
    #p2_pwm = 7

    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #Create Servos using Servo Class
    servo1 = Servo(26)
    servo2 = Servo(19)

    #Initialize Speed
    servo1.speed = SpeedS1
    servo2.speed = SpeedS2

    #Adjustment Code
    def quit(channel):
        GPIO.cleanup()
        print("Quit Button Pressed.")
        done_semaphore.release()

    def stop(channel):
        servo1.speed = 0
        servo2.speed = 0

    def adjust_freq_p1(channel):
        nonlocal SpeedS1

        time.sleep(0.5)
        if GPIO.input(23):
            SpeedS1 = SpeedS1 + 0.1  # add 1Hz to the signal
        else:
            SpeedS1 = SpeedS1 - 0.1  # subtract 1Hz from the signal

        servo1.speed = SpeedS1
        print("Servo 1 Speed [-1.0 to 1.0]: ", SpeedS1)

    def adjust_freq_p2(channel):
        nonlocal SpeedS2

        time.sleep(0.5)
        if GPIO.input(27):
            SpeedS2 = SpeedS2 + 0.1 #add 1Hz to the signal
        else:
            SpeedS2 = SpeedS2 - 0.1 #subtract 1Hz from the signal

        servo2.speed = SpeedS2
        print("Servo 2 Speed [-1.0 to 1.0]: ", SpeedS2)

    GPIO.add_event_detect(17, GPIO.FALLING, callback=quit, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=stop, bouncetime=300)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=adjust_freq_p1, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=adjust_freq_p2, bouncetime=300)

    done_semaphore.acquire()

    return True


def two_wheel(settings, **kwargs):
    done_semaphore = threading.Semaphore(0)

    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #Create Servos using Servo Class
    servo1 = Servo(26)
    servo2 = Servo(19)

    def quit(channel):
        GPIO.cleanup()
        print("Quit Button Pressed.")
        done_semaphore.release()

    def stop(channel):
        time.sleep(1)
        if GPIO.input(22):
            servo1.speed = 0
            print("Servo 1: Stopped")
        else:
            servo2.speed = 0
            print("Servo 2: Stopped")

    def servo_1_increment(channel):
        time.sleep(1)
        if GPIO.input(23):
            SpeedS1 = 1.0  # add 1Hz to the signal
            print("Servo 1: Counter-Clockwise Rotation")
        else:
            SpeedS1 = -1.0  # subtract 1Hz from the signal
            print("Servo 1: Clockwise Rotation")
        servo1.speed = SpeedS1

    def servo_2_increment(channel):
        time.sleep(1)
        if GPIO.input(27):
            SpeedS2 = 1.0 # add 1Hz to the signal
            print("Servo 2: Counter-Clockwise Rotation")
        else:
            SpeedS2 = -1.0  # subtract 1Hz from the signal
            print("Servo 2: Clockwise Rotation")
        servo2.speed = SpeedS2

    GPIO.add_event_detect(17, GPIO.FALLING, callback=quit, bouncetime=600)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=stop, bouncetime=600)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=servo_1_increment, bouncetime=600)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=servo_2_increment, bouncetime=600)

    done_semaphore.acquire()

    return True


def rolling_control(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    GPIO.setmode(GPIO.BCM)
    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    done = False

    def exit_loop():
        nonlocal done
        done = True

    def resume():
        servo_1.start()
        servo_2.start()

    def stop():
        servo_1.stop()
        servo_2.stop()

    buttons = []

    servo_1 = Servo(19)
    servo_2 = Servo(26)

    def servo_1_counter_clockwise(channel):
        servo_1.speed = 1.0

    def servo_1_clockwise(channel):
        servo_1.speed = -1.0

    def servo_1_zero(channel):
        servo_1.speed = 0.0

    def servo_2_counter_clockwise(channel):
        servo_2.speed = 1.0

    def servo_2_clockwise(channel):
        servo_2.speed = -1.0

    def servo_2_zero(channel):
        servo_2.speed = 0.0

    buttons.append(ModalButton((160, 120), "STOP", "Resume", stop, resume))
    buttons.append(Button((160, 200), "Quit", exit_loop))
    buttons.append(Button(( 40, 200), "S1 +", servo_1_clockwise))
    buttons.append(Button(( 80, 200), "S1 0", servo_1_zero))
    buttons.append(Button((120, 200), "S1 -", servo_1_counter_clockwise))
    buttons.append(Button((200, 200), "S2 +", servo_1_clockwise))
    buttons.append(Button((240, 200), "S2 0", servo_1_zero))
    buttons.append(Button((280, 200), "S2 -", servo_1_counter_clockwise))

    clock = Clock()

    while not done:
        for event in pygame.event.get():

            if event.type is pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print("Mouse Down:", event.type, pos)
            elif event.type is pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print("Mouse Up:", event.type, pos)
            elif event.type == pygame.QUIT:
                sys.exit()
            else:
                continue

            for button in buttons:
                button.interact(pos)

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        screen.fill(black)

        for button in buttons:
            button.update(screen, frame_time_s)

        pygame.display.flip()

    return True


MODULE = {
    "blink": blink,
    "pwm_calibrate": pwm_calibrate,
    "servo_control_beta": servo_control_beta,
    "servo_control": servo_control,
    "two_wheel": two_wheel,
    "rolling_control": rolling_control,
}
