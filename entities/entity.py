from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.loop import RunLoop
    from entities import point


class Entity:
    def update(self, loop: 'RunLoop', time_delta: float):
        pass

    def draw(self, screen):
        pass

    def interact(self, loop: 'RunLoop', interact_point: 'point'):
        pass