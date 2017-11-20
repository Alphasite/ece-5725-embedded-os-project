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


class Slider(Entity):
    TRI_SIZE = 6

    def __init__(self, initial_position: float, height: float, center: point, bar_colour: colour, tri_colour: colour) -> None:
        self.__position = 0
        self.position = initial_position
        self.center = center
        self.height = height
        self.width = 1.5
        self.bar_colour = bar_colour
        self.tri_colour = tri_colour

        self.rail = pygame.Rect(
            center[0] - self.width,
            center[1] - self.height / 2,
            self.width,
            self.height
        )

        self.dragging = False

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        if value > 1:
            value = 1

        if value < 0:
            value = 0

        self.__position = 1 - value

    def __compute_position(self, percentage: float):
        return (
            self.center[0],
            self.rail.top + self.height * percentage
        )

    @property
    def rect(self):
        center = self.__compute_position(self.position)

        return pygame.Rect(
            center[0],
            center[1] - Slider.TRI_SIZE / 2,
            center[0] + Slider.TRI_SIZE,
            center[1] + Slider.TRI_SIZE / 2,
        )

    def interact(self, loop: 'RunLoop', interact_point: 'point'):
        self.dragging = False

    def drag(self, loop: 'RunLoop', start_point: 'point', current_point: 'point'):
        rect = self.rect.inflate(10, 10)

        if rect.collidepoint(*current_point):
            self.dragging = True

        if self.dragging:
            dy = current_point[1] - self.rail.top
            self.position = dy / self.height

    def draw(self, screen):
        position = self.__compute_position(1 - self.position)

        points = [
            (position[0], position[1] - Slider.TRI_SIZE),
            (position[0] + Slider.TRI_SIZE, position[1]),
            (position[0], position[1] + Slider.TRI_SIZE),
        ]

        pygame.draw.rect(screen, self.bar_colour, self.rail)
        pygame.draw.polygon(screen, self.tri_colour, points)


class ProgressBar(Entity):
    def __init__(self, initial_position: float, height: float, width: float, center: point, colour: colour) -> None:
        self.__position = 0
        self.position = initial_position
        self.center = center
        self.height = height
        self.width = width
        self.colour = colour

        self.rail = pygame.Rect(
            center[0] - self.width / 2,
            center[1] - self.height / 2,
            self.width,
            self.height
        )

        self.dragging = False

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        if value > 1:
            value = 1

        if value < 0:
            value = 0

        self.__position = value

    def __compute_position(self, percentage: float):
        return (
            self.center[0],
            self.rail.top + self.height * (1 - percentage)
        )

    def interact(self, loop: 'RunLoop', interact_point: 'point'):
        self.dragging = False

    def draw(self, screen):
        position = self.__compute_position(self.position)
        filled_rect = pygame.Rect(position, (self.width, self.height * self.position))

        pygame.draw.rect(screen, self.colour, filled_rect)


class LinkedProgressSlider(Entity):
    def __init__(self, initial_position: float, height: float, width: float, center: point, bar_colour: colour, tri_colour: colour) -> None:
        self.bar = ProgressBar(initial_position, height, width, center, bar_colour)
        self.slider = Slider(initial_position, height, center, bar_colour, tri_colour)

    @property
    def position(self):
        return self.slider.position

    @position.setter
    def position(self, value):
        self.bar.position = value

    def drag(self, loop: 'RunLoop', start_point: 'point', current_point: 'point'):
        self.slider.drag(loop, start_point, current_point)

    def interact(self, loop: 'RunLoop', interact_point: 'point'):
        self.slider.interact(loop, interact_point)

    def draw(self, screen):
        self.bar.draw(screen)
        self.slider.draw(screen)


class Sprite(Entity):
    def __init__(self, path: str, center: point, width: float, height: float) -> None:
        self.texture = pygame.image.load(path)
        self.texture = pygame.transform.scale(self.texture, (width, height))
        self.rect = self.texture.get_rect()
        self.rect = self.rect.move(*center)
        self.enabled = True

    def draw(self, screen):
        screen.blit(self.texture, self.rect)


class StatusPip(Entity):
    def __init__(self, center: point, radius: float, colour: colour) -> None:
        self.center = center
        self.radius = radius
        self.colour = colour

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.center, self.radius)


class FrameUpdateEvent(Entity):
    def __init__(self, handler: callable) -> None:
        self.handler = handler

    def update(self, loop: 'RunLoop', time_delta: float):
        self.handler(loop, time_delta)
