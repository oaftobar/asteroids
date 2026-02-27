import sys
import os
import json
import platform

import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, INITIAL_HIGH_SCORE
from logger import log_event, log_state
from player import Player
from shot import Shot


def get_high_score_path():
    if platform.system() == "Windows":
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        base_dir = os.path.join(app_data, "asteroids")
    else:
        base_dir = os.path.expanduser("~/.asteroids")

    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "highscore.json")


def load_high_score():
    path = get_high_score_path()
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("score", 0), data.get("initials", "")
    except (json.JSONDecodeError, IOError):
        pass
    return 0, ""


def save_high_score(score, initials):
    path = get_high_score_path()
    try:
        with open(path, "w") as f:
            json.dump({"score": score, "initials": initials}, f)
    except IOError:
        pass


def create_fonts():
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 36)
    return font_large, font_medium


def render_centered_text(screen, font, text, color, center_pos):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=center_pos)
    screen.blit(rendered_text, text_rect)


def draw_ui_overlay(screen, font, score, high_score, high_score_initials=""):
    # Current score
    score_text = font.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 10))

    # High score
    if high_score_initials:
        high_score_text = font.render(
            f"High Score: {high_score} ({high_score_initials})", True, "white"
        )
    else:
        high_score_text = font.render(f"High Score: {high_score}", True, "white")
    screen.blit(high_score_text, (10, 50))


def show_high_score_input(screen, clock, score):
    font_large, font_medium = create_fonts()

    initials = ["A", "A", "A"]
    selected_slot = 0
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""  # Return empty if quit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_slot = (selected_slot - 1) % 3
                elif event.key == pygame.K_RIGHT:
                    selected_slot = (selected_slot + 1) % 3
                elif event.key == pygame.K_UP:
                    current_idx = alphabet.index(initials[selected_slot])
                    initials[selected_slot] = alphabet[(current_idx + 1) % 26]
                elif event.key == pygame.K_DOWN:
                    current_idx = alphabet.index(initials[selected_slot])
                    initials[selected_slot] = alphabet[(current_idx - 1) % 26]
                elif event.key == pygame.K_RETURN:
                    return "".join(initials)

        screen.fill("black")

        # Title
        render_centered_text(
            screen,
            font_large,
            "NEW HIGH SCORE!",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100),
        )

        # Score
        render_centered_text(
            screen,
            font_medium,
            f"Score: {score}",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40),
        )

        # Initials input
        for i, letter in enumerate(initials):
            color = "yellow" if i == selected_slot else "white"
            letter_x = SCREEN_WIDTH // 2 - 60 + i * 60
            letter_y = SCREEN_HEIGHT // 2 + 40
            render_centered_text(
                screen, font_large, letter, color, (letter_x, letter_y)
            )

        # Instructions
        render_centered_text(
            screen,
            font_medium,
            "Use LEFT/RIGHT to select, UP/DOWN to change, ENTER to confirm",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120),
        )

        pygame.display.flip()
        clock.tick(60)


def show_game_over(screen, clock, score):
    font_large, font_medium = create_fonts()

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
        render_centered_text(
            screen,
            font_large,
            "GAME OVER",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60),
        )

        # Score text
        render_centered_text(
            screen,
            font_medium,
            f"Final Score: {score}",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        )

        # Instructions
        render_centered_text(
            screen,
            font_medium,
            "Press R to Restart",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60),
        )
        render_centered_text(
            screen,
            font_medium,
            "Press Q to Quit",
            "white",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100),
        )

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
    font = pygame.font.Font(None, 36)  # UI font
    high_score, high_score_initials = load_high_score()

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

            # Draw UI overlay
            draw_ui_overlay(screen, font, score, high_score, high_score_initials)

            pygame.display.flip()

            # limit framerate to 60 fps
            dt = clock.tick(60) / 1000.0

        # Update high score if current score is higher
        new_high_score = False
        if score > high_score:
            high_score = score
            new_high_score = True

        # If new high score, get initials
        if new_high_score:
            initials = show_high_score_input(screen, clock, score)
            if initials:  # If not quit
                high_score_initials = initials
                save_high_score(high_score, high_score_initials)
            else:
                high_score_initials = ""

        # Show game over screen and check if player wants to restart
        if show_game_over(screen, clock, score):
            continue  # Restart the game
        else:
            break  # Quit the game


if __name__ == "__main__":
    main()
