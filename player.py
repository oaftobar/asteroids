import pygame
from circleshape import CircleShape
from constants import (
    LINE_WIDTH,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_INVINCIBILITY_SECONDS,
)
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y, shoot_sound=None):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.shoot_timer = 0
        self.invincible = False
        self.invincibility_timer = 0.0
        self.shoot_sound = shoot_sound

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), LINE_WIDTH)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def update(self, dt):
        self.shoot_timer -= dt
        if self.invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
        self.wrap_around(SCREEN_WIDTH, SCREEN_HEIGHT)
        keys = pygame.key.get_pressed()

        # Smooth rotation
        if keys[pygame.K_a]:
            self.rotation -= PLAYER_TURN_SPEED * dt
        if keys[pygame.K_d]:
            self.rotation += PLAYER_TURN_SPEED * dt

        # Smooth movement (allows diagonal)
        move_direction = 0
        if keys[pygame.K_w]:
            move_direction += 1
        if keys[pygame.K_s]:
            move_direction -= 1

        if move_direction != 0:
            self.move(dt * move_direction)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        if self.shoot_timer > 0:
            return
        self.shoot_timer = PLAYER_SHOOT_COOLDOWN_SECONDS
        # Spawn at triangle tip (forward point)
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        spawn_pos = self.position + forward * self.radius
        shot = Shot(spawn_pos.x, spawn_pos.y)
        shot.velocity = forward * PLAYER_SHOOT_SPEED
        if self.shoot_sound:
            self.shoot_sound.play()

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
