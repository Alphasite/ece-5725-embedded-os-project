"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

from datetime import timedelta, datetime
from typing import Optional

import pygame

from entities import white, point, colour
from entities.entity import Entity
from entities.loop import RunLoop


class Debouncer:
    def __init__(self, wait_time: timedelta = timedelta(milliseconds=100)) -> None:
        self.wait_time = wait_time
        self.time = datetime.now()

    def try_press(self):
        old = self.time
        now = datetime.now()

        period = now - old

        if period < self.wait_time:
            return False
        else:
            self.time = now
            return True


class Button(Entity):
    def __init__(self, center: point, text: str, action: callable, background_colour: Optional[colour] = None,
                 text_size: int = 25, debouncer: Debouncer = Debouncer()):
        self.action = action
        self.label = Label(center, text, background_colour=background_colour, text_size=text_size)
        self.debouncer = debouncer

    def draw(self, screen):
        self.label.draw(screen)

    def interact(self, loop: RunLoop, interact_point: point):
        if self.label.background_rect.collidepoint(interact_point):
            if self.debouncer.try_press():
                self.action(loop)


class Label(Entity):
    def __init__(
            self,
            center: point,
            text: str,
            text_colour: colour = white,
            background_colour: Optional[colour] = None,
            text_size: int = 25
    ):
        self.font = pygame.font.Font(None, text_size)
        self.center = center
        self.colour = text_colour
        self.background_colour = background_colour

        self.surface = None
        self.rect = None
        self.background_rect = None

        self._text = None
        self.text = text

    def draw(self, screen):
        if self.background_colour is not None:
            pygame.draw.rect(screen, self.background_colour, self.background_rect)

        screen.blit(self.surface, self.rect)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.surface = self.font.render(self.text, True, white)
        self.rect = self.surface.get_rect(center=self.center)
        self.background_rect = self.rect.inflate(10, 10)


class ModalButton(Entity):
    def __init__(self, active_button: Button, disabled_button: Button, debouncer: Debouncer = Debouncer()):
        self.debouncer = debouncer

        # Wrap the action to first swap the button before performing the action
        def swap_button_wrapper(action):
            def swap_button(loop: RunLoop):
                self.use_active_button = not self.use_active_button
                action(loop)

            return swap_button

        self.use_active_button = True

        self.active_button = active_button
        self.active_button.debouncer = debouncer
        self.active_button.action = swap_button_wrapper(self.active_button.action)

        self.disabled_button = disabled_button
        self.disabled_button.debouncer = debouncer
        self.disabled_button.action = swap_button_wrapper(self.disabled_button.action)

    def draw(self, screen):
        if self.use_active_button:
            self.active_button.draw(screen)
        else:
            self.disabled_button.draw(screen)

    def interact(self, loop: RunLoop, interact_point: point):
        if self.use_active_button:
            self.active_button.interact(loop, interact_point)
        else:
            self.disabled_button.interact(loop, interact_point)
