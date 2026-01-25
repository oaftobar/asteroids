import sys

import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_event, log_state
from player import Player
from shot import Shot


def main():
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Failed to initialize pygame: {e}")
        return
    clock = pygame.time.Clock()

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = updatable
    asteroid_field = AsteroidField()

    Player.containers = (updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    dt = 0
    score = 0
    game_over = False

    while not game_over:
        # log_state()  # Disabled for performance

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break

        updatable.update(dt)

        # Check player-asteroid collisions
        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                print("Game over!")
                print(f"Final score: {score}")
                game_over = True
                break

        # Check asteroid-shot collisions using sprite group collision detection
        shots_hit = pygame.sprite.groupcollide(
            asteroids, shots, False, True, collided=lambda a, s: a.collides_with(s)
        )
        for asteroid in shots_hit:
            log_event("asteroid_shot")
            score += 100
            asteroid.split()

        screen.fill("black")

        for obj in drawable:
            obj.draw(screen)

        pygame.display.flip()

        # limit framerate to 60 fps
        dt = clock.tick(60) / 1000.0


if __name__ == "__main__":
    main()
