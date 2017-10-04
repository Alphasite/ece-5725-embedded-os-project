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

class Button:
    def __init__(self, center: point, text: str, action: callable):
        self.font = my_font = pygame.font.Font(None, 25)
        self.center = center
        self.text = center
        self.action = action
        self.surface = my_font.render(text, True, WHITE)
        self.rect = self.surface.get_rect(center=center)

    def update(self, screen, time_delta: float):
        screen.blit(self.surface, self.rect)

    def interact(self, interact_point: point):
        if self.rect.collidepoint(interact_point):
            self.action()


class Servo:
    zero_pulse_width = 1.5
    maximum_pulse_width_range = 0.2

    def __init__(self, servo_pin) -> None:
        self.pulse_width = Servo.zero_pulse_width

        GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(servo_pin, self.frequency)
        self.pwm.start(self.duty_cycle)

    def set_pwm(self):
        self.pwm.ChangeFrequency(self.frequency)
        self.pwm.ChangeDutyCycle(self.duty_cycle)

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

    servo1 = Servo(19)
    servo2 = Servo(26)

    servo1.speed = 0
    servo2.speed = 0

    time.sleep(5)

    servo1.speed = 0.5
    servo2.speed = -0.5

    time.sleep(5)
    
    return True

def servo_control_beta(settings, **kwargs):

    done_semaphore = threading.Semaphore(0)

    #Default Frequency/PWM Settings
    p1_freq = 46.5
    p2_freq = 46.5
    p1_pwm = 7
    p2_pwm = 7

    # Set up TFT Buttons as Inputs, GPIO Pins 26, 19 as Outputs
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([17, 22, 23, 27], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([26, 19], GPIO.OUT, initial=GPIO.LOW)

    # Create PWM Instances
    p1 = GPIO.PWM(26, p1_freq)  # Frequency of 1Hz
    p2 = GPIO.PWM(19, p2_freq)  # Frequenxy of 2Hz

    # Start PWM
    p1.start(p1_pwm)  # 6.5% Duty Cycle ~ 1.3mS = Min Speed
    p2.start(p2_pwm)  # 8.5% Duty Cycle ~ 1.7mS = Max Speed

    #Adjustment Code
    def adjust_pwm_p1(channel):
        nonlocal p1_freq

        time.sleep(0.5)
        if GPIO.input(17):
            p1_freq = p1_freq + 1 #add 1Hz to the signal
        else:
            p1_freq = p1_freq - 1 #subtract 1Hz from the signal

        #Supplementary "KILL" Function by holding Buttons 1 & 2
        if not GPIO.input(22):
            p1.stop(p1)
            p2.stop(p2)
            print("Servos Stopped")

        p1.ChangeFrequency(p1_freq)
        print("Servo 1 Frequency: ", p1_freq)

    def adjust_pwm_p2(channel):
        nonlocal p2_freq

        time.sleep(0.5)
        if GPIO.input(22):
            p2_freq = p2_freq + 1 #add 1Hz to the signal
        else:
            p2_freq = p2_freq - 1 #subtract 1Hz from the signal

        p2.ChangeFrequency(p2_freq)
        print("Servo 2 Frequency: ", p2_freq)

    def adjust_freq_p1(channel):
        nonlocal p1_pwm

        time.sleep(0.5)
        if GPIO.input(23):
            p1_pwm = p1_pwm + 0.1 #add 0.1% to the signal
        else:
            p1_pwm = p1_pwm - 0.1 #subtract 0.1% from the signal

        p1.ChangeDutyCycle(p1_freq)
        print("Servo 1 Duty Cycle: ", p1_pwm)

    def adjust_freq_p2(channel):
        nonlocal p2_pwm

        time.sleep(0.5)
        if GPIO.input(27):
            p2_pwm = p2_pwm + 0.1 #add 1Hz to the signal
        else:
            p2_pwm = p2_pwm - 0.1 #subtract 1Hz from the signal

        p2.ChangeDutyCycle(p1_freq)
        print("Servo 2 Duty Cycle: ", p2_pwm)

    GPIO.add_event_detect(17, GPIO.FALLING, callback=adjust_pwm_p1, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=adjust_pwm_p2, bouncetime=300)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=adjust_freq_p1, bouncetime=300)
    GPIO.add_event_detect(27, GPIO.FALLING, callback=adjust_freq_p2, bouncetime=300)

    done_semaphore.acquire()

    return True

def two_wheel(settings, **kwargs):
    return True

def rolling_control(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    ball1 = Ball("resources/lab2/ball.png", [120, 120], [50, 50])
    ball2 = Ball("resources/lab2/tennis_ball.png", [180, 120], [30, 30])

    ball2.rect = ball2.rect.move([screen_size[0] / 2, screen_size[1] / 2])

    clock = Clock()

    done = False
    go = False

    def exit_loop():
        nonlocal done
        done = True

    def start_loop():
        nonlocal go
        go = True

    def speedup_loop():
        ball1.playback_speed_multiplier = 1.25 * ball1.playback_speed_multiplier
        ball2.playback_speed_multiplier = 1.25 * ball2.playback_speed_multiplier

    def slowdown_loop():
        ball1.playback_speed_multiplier = 0.75 * ball1.playback_speed_multiplier
        ball2.playback_speed_multiplier = 0.75 * ball2.playback_speed_multiplier

    button_quit = Button((250, 210), "quit", exit_loop)
    button_start = Button((70, 210), "start", start_loop)
    button_fast = Button((130, 210), "fast", speedup_loop)
    button_slow = Button((190, 210), "slow", slowdown_loop)

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

            button_quit.interact(pos)
            button_start.interact(pos)
            button_fast.interact(pos)
            button_slow.interact(pos)

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        ball1.collide_ball(ball2)

        screen.fill(black)
        if go:
            ball1.update(screen, frame_time_s)
            ball2.update(screen, frame_time_s)

        button_quit.update(screen, frame_time_s)
        button_start.update(screen, frame_time_s)
        button_fast.update(screen, frame_time_s)
        button_slow.update(screen, frame_time_s)
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
