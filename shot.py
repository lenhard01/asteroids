from typing import ClassVar

import pygame

from circleshape import CircleShape
from constants import SHOT_RADIUS


class Shot(CircleShape):
    containers: ClassVar[tuple[pygame.sprite.Group, ...]]

    def __init__(self, x: int, y: int, velocity: pygame.Vector2) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.velocity += velocity

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt: int | float) -> None:
        self.position += self.velocity * dt
