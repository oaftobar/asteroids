import sys

import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_event, log_state
from player import Player
from shot import Shot


def show_game_over(screen, clock, score):
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                elif event.key == pygame.K_q:
                    return False  # Quit game

        screen.fill("black")

        # Game Over text
        game_over_text = font_large.render("GAME OVER", True, "white")
        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        )
        screen.blit(game_over_text, game_over_rect)

        # Score text
        score_text = font_medium.render(f"Final Score: {score}", True, "white")
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        # Instructions
        restart_text = font_medium.render("Press R to Restart", True, "white")
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        )
        screen.blit(restart_text, restart_rect)

        quit_text = font_medium.render("Press Q to Quit", True, "white")
        quit_rect = quit_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        )
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()
        clock.tick(60)


def main():
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Failed to initialize pygame: {e}")
        return

    clock = pygame.time.Clock()

    while True:  # Main game loop for restarts
        # Initialize sprite groups
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

        while not game_over:  # Single game loop
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
                    game_over = True
                    break

            # Check asteroid-shot collisions (optimized version)
            for asteroid in asteroids:
                for shot in shots:
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        score += 100
                        shot.kill()
                        asteroid.split()
                        break  # Only one shot can hit an asteroid per frame

            screen.fill("black")

            for obj in drawable:
                obj.draw(screen)

            pygame.display.flip()

            # limit framerate to 60 fps
            dt = clock.tick(60) / 1000.0

        # Show game over screen and check if player wants to restart
        if show_game_over(screen, clock, score):
            continue  # Restart the game
        else:
            break  # Quit the game


if __name__ == "__main__":
    main()
