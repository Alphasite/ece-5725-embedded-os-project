"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

import os
import pygame
from pygame.time import Clock

try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import Mock
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


class RunLoop:
    def __init__(self) -> None:
        self.done = False

        if running_on_pi:
            setup_for_pi()

        GPIO.setmode(GPIO.BCM)
        pygame.init()

        self.screen = pygame.display.set_mode(screen_size)

    def start_loop(self, entities):
        clock = Clock()

        previous_mouse_down = None

        while not self.done:
            for event in pygame.event.get():
                if event.type is pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    previous_mouse_down = None

                    print("Mouse Up:", event.type, pos)

                    for entity in entities:
                        entity.interact(self, pos)

                if event.type is pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    previous_mouse_down = pos

                    print("Mouse Down:", event.type, pos)

                if event.type is pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()

                    # print("Mouse Move:", event.type, pos)

                    for entity in entities:
                        if previous_mouse_down is not None:
                            entity.drag(self, previous_mouse_down, pos)

                if event.type == pygame.QUIT:
                    self.done = True

            frame_time_ms = clock.tick(target_framerate)
            frame_time_s = frame_time_ms / 1000

            for entity in entities:
                entity.update(self, frame_time_s)

            self.screen.fill(black)

            for entity in entities:
                entity.draw(self.screen)

            pygame.display.flip()
