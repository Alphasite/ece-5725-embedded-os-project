"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

from __future__ import division, print_function
import time
import os
import pygame
from pygame.time import Clock

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = Mock()

from entities import black

running_on_pi = True if os.getenv("DEBUG") is None else False

screen_size = 320, 240
target_framerate = 30


def setup_for_pi():
    os.putenv('SDL_VIDEODRIVER', 'fbcon')  # Display on piTFT
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')  # Track mouse clicks on piTFT
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    # pygame.mouse.set_visible(False)


class RunLoop(object):
    def __init__(self):
        self.done = False
        self.previous_mouse_down = None

        if running_on_pi:
            setup_for_pi()

        GPIO.setmode(GPIO.BCM)
        pygame.init()

        self.screen = pygame.display.set_mode(screen_size)

    def start_loop(self, entities):
        clock = Clock()

        previous_time = time.time()

        while not self.done:
            # frame_time_ms = clock.tick(target_framerate)
            # frame_time_s = frame_time_ms / 1000

            # time.sleep(1.0 / target_framerate)

            current_time = time.time()
            frame_time_s = current_time - previous_time
            previous_time = current_time

            # print("Frametime (render):", frame_time_s)

            for event in list(pygame.event.get()):
                if event.type is pygame.MOUSEBUTTONUP:
                    pos = event.pos

                    print("Mouse Up:", event.type, pos)

                    self.previous_mouse_down = None

                    for entity in entities:
                        entity.interact(self, pos)

                if event.type is pygame.MOUSEBUTTONDOWN:
                    pos = event.pos

                    print("Mouse Down:", event.type, pos)

                    self.previous_mouse_down = pos

                if event.type is pygame.MOUSEMOTION:
                    pos = event.pos

                    # print("Mouse move:", event.type, pos)

                for entity in entities:
                        if self.previous_mouse_down is not None:
                            entity.drag(self, self.previous_mouse_down, pos)

                if event.type == pygame.QUIT:
                    self.done = True

            for entity in entities:
                entity.update(self, frame_time_s)

            self.screen.fill(black)

            for entity in entities:
                entity.draw(self.screen)

            pygame.display.flip()
