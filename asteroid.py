import random
import math

import pygame
from circleshape import CircleShape
from constants import LINE_WIDTH, ASTEROID_MIN_RADIUS
from logger import log_event

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

        self.points = self._generate_points()

    def _generate_points(self):
        num_points = random.randint(8, 12)
        points = []

        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            lumpy_radius = self.radius * random.uniform(0.7, 1.0)

            x = lumpy_radius * math.cos(angle)
            y = lumpy_radius * math.sin(angle)
            points.append((x, y))

        return points

    def draw(self, screen):
        if not hasattr(self, 'points'):
            self.points = self._generate_points()

        absolute_points = [
            (self.position.x + px, self.position.y + py)
            for px, py in self.points
        ]
        pygame.draw.polygon(screen, "white", absolute_points, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        
        log_event("asteroid_split")

        rand_angle = random.uniform(20, 50)

        new_velocity1 = self.velocity.rotate(rand_angle)
        new_velocity2 = self.velocity.rotate(-rand_angle)
        
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid.velocity = new_velocity1 * 1.2
        asteroid = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid.velocity = new_velocity2 * 1.2