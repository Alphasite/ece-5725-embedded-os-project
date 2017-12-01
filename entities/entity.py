"""
Nishad Mathur (nm594) & Adam Halverson (abh222)
Lab 3, Lab Section 02, 17/10/17
"""

from __future__ import division, print_function


class Entity(object):
    def update(self, loop, time_delta):
        pass

    def draw(self, screen):
        pass

    def interact(self, loop, interact_point):
        pass

    def drag(self, loop, start_point, current_point):
        pass
