"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

import random
import sys
import os
import threading
import time
from typing import Tuple, Optional, List

import pygame
from pygame.time import Clock

from modules.fifo import passthrough

timestamp = time.time()

done_semaphore = threading.Semaphore(0)

running_on_pi = True if os.getenv("DEBUG") is None else False

black = 0, 0, 0
WHITE = 255, 255, 255

screen_size = 320, 240
target_framerate = 30

point = Tuple[int, int]


class Ball:
    def __init__(
            self,
            path: str,
            velocity: List[float],
            dimensions: Optional[List[int]] = None,
            playback_speed_multiplier: float = 1.0,
    ):

        self.velocity = velocity
        self.playback_speed_multiplier = playback_speed_multiplier

        self.texture = pygame.image.load(path)

        if dimensions is not None:
            self.texture = pygame.transform.scale(self.texture, dimensions)

        self.rect = self.texture.get_rect()

    def update(self, screen, time_delta: float):
        width, height = screen.get_size()

        if self.rect.left < 0 or self.rect.right > width:
            self.velocity[0] = -self.velocity[0]

        if self.rect.top < 0 or self.rect.bottom > height:
            self.velocity[1] = -self.velocity[1]

        delta_v_x = time_delta * self.velocity[0] * self.playback_speed_multiplier
        delta_v_y = time_delta * self.velocity[1] * self.playback_speed_multiplier

        self.rect = self.rect.move(delta_v_x, delta_v_y)

        screen.blit(self.texture, self.rect)

    def collide_ball(self, ball):
        if self.rect.colliderect(ball.rect):
            self.velocity[0] *= random.uniform(-1.25, -0.75)
            self.velocity[1] *= random.uniform(-1.25, -0.75)

            ball.velocity[0] *= random.uniform(-1.25, -0.75)
            ball.velocity[1] *= random.uniform(-1.25, -0.75)


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


def setup_for_pi():
    os.putenv('SDL_VIDEODRIVER', 'fbcon')  # Display on piTFT
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    # pygame.mouse.set_visible(False)


def gpio_handler_6_button(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27, 26, 19], GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
                break

            if not GPIO.input(26):
                passthrough(settings, command="seek -3 0")
                print("Rew x30 Button Pressed.")

            if not GPIO.input(19):
                passthrough(settings, command="seek 3 0")
                print("Fwd x30 Button Pressed.")

            time.sleep(0.2)

    finally:
        GPIO.cleanup()

    return True


def gpio_handler_6_button_interrupt(settings, **kwargs) -> bool:
    import RPi.GPIO as GPIO

    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup([17, 22, 23, 27, 26, 19], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        def pause(channel):
            passthrough(settings, command="pause")
            print("Pause Button Pressed.")

        def seek_forwards_1(channel):
            passthrough(settings, command="seek 1 0")
            print("Fwd x10 Button Pressed.")

        def seek_back_1(channel):
            passthrough(settings, command="seek -1 0")
            print("Rew x10 Button Pressed.")

        def seek_back_3(channel):
            passthrough(settings, command="seek -3 0")
            print("Rew x30 Button Pressed.")

        def seek_forwards_3(channel):
            passthrough(settings, command="seek 3 0")
            print("Fwd x30 Button Pressed.")

        def quit(channel):
            passthrough(settings, command="quit")
            print("Quit Button Pressed.")
            done_semaphore.release()

        GPIO.add_event_detect(17, GPIO.FALLING, callback=pause, bouncetime=300)
        GPIO.add_event_detect(19, GPIO.FALLING, callback=seek_forwards_3, bouncetime=300)
        GPIO.add_event_detect(22, GPIO.FALLING, callback=seek_forwards_1, bouncetime=300)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=seek_back_1, bouncetime=300)
        GPIO.add_event_detect(26, GPIO.FALLING, callback=seek_back_3, bouncetime=300)
        GPIO.add_event_detect(27, GPIO.FALLING, callback=quit, bouncetime=300)

        done_semaphore.acquire()
    finally:
        GPIO.cleanup()

    return True


def ball_1(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    ball1 = Ball("resources/lab2/ball.png", [120, 120], [50, 50])

    clock = Clock()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        screen.fill(black)
        ball1.update(screen, frame_time_s)
        pygame.display.flip()


def ball_2(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    ball1 = Ball("resources/lab2/ball.png", [120, 120], [50, 50])
    ball2 = Ball("resources/lab2/tennis_ball.png", [180, 120], [30, 30])

    clock = Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        screen.fill(black)
        ball1.update(screen, frame_time_s)
        ball2.update(screen, frame_time_s)
        pygame.display.flip()


def ball_2_collide(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    ball1 = Ball("resources/lab2/ball.png", [120, 120], [50, 50])
    ball2 = Ball("resources/lab2/tennis_ball.png", [180, 120], [30, 30])

    ball2.rect = ball2.rect.move([screen_size[0] / 2, screen_size[1] / 2])

    clock = Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        ball1.collide_ball(ball2)

        screen.fill(black)
        ball1.update(screen, frame_time_s)
        ball2.update(screen, frame_time_s)
        pygame.display.flip()


def ball_2_collide_quit(settings, **kwargs):
    if running_on_pi:
        setup_for_pi()

    pygame.init()

    screen = pygame.display.set_mode(screen_size)

    ball1 = Ball("resources/lab2/ball.png", [120, 120], [50, 50])
    ball2 = Ball("resources/lab2/tennis_ball.png", [180, 120], [30, 30])

    ball2.rect = ball2.rect.move([screen_size[0] / 2, screen_size[1] / 2])

    clock = Clock()

    done = False

    def exit_loop():
        nonlocal done
        done = True

    button = Button((250, 180), "quit", exit_loop)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

            if event.type is pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print("Mouse Down:", event.type, pos)
            elif event.type is pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                print("Mouse Up:", event.type, pos)
            else:
                continue

            button.interact(pos)

        frame_time_ms = clock.tick(target_framerate)
        frame_time_s = frame_time_ms / 1000

        ball1.collide_ball(ball2)

        screen.fill(black)
        ball1.update(screen, frame_time_s)
        ball2.update(screen, frame_time_s)
        button.update(screen, frame_time_s)
        pygame.display.flip()

    return True


def ball_2_collide_quit_start(settings, **kwargs):
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
    "six_button": gpio_handler_6_button,
    "six_button_interrupt": gpio_handler_6_button_interrupt,
    "ball_1": ball_1,
    "ball_2": ball_2,
    "ball_2_collide": ball_2_collide,
    "quit_button": ball_2_collide_quit,
    "quit_start_button": ball_2_collide_quit_start,
}
