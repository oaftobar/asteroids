import os
import json
import platform
import array
import math

import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    INITIAL_HIGH_SCORE,
    PLAYER_STARTING_LIVES,
    PLAYER_INVINCIBILITY_SECONDS,
    FLASH_DURATION,
    FLASH_COLOR,
)
from logger import log_event, log_state
from player import Player
from shot import Shot


def generate_sound(frequency, duration, volume=0.3, wave_type="square"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    samples = []

    for i in range(n_samples):
        t = i / sample_rate
        value = 0

        if wave_type == "square":
            value = 1 if (t * frequency) % 1 < 0.5 else -1
        elif wave_type == "sine":
            value = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "sawtooth":
            value = 2 * ((t * frequency) % 1) - 1

        # Apply fade out
        fade = 1 - (i / n_samples)
        samples.append(int(32767 * volume * value * fade))

    return pygame.mixer.Sound(buffer=array.array("h", samples))


def load_sounds():
    pygame.mixer.init()
    shoot_sound = generate_sound(880, 0.1, 0.2, "square")  # High beep
    explosion_sound = generate_sound(110, 0.2, 0.3, "sawtooth")  # Low buzz
    death_sound = generate_sound(220, 0.3, 0.3, "sawtooth")  # Descending feel
    return shoot_sound, explosion_sound, death_sound


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


class GameState:
    def __init__(self):
        self.score = 0
        self.high_score, self.high_score_initials = load_high_score()
        self.lives = PLAYER_STARTING_LIVES

    def add_score(self, points):
        self.score += points

    def reset(self):
        self.score = 0
        self.lives = PLAYER_STARTING_LIVES

    def lose_life(self):
        self.lives -= 1

    def is_alive(self):
        return self.lives > 0

    def check_new_high_score(self):
        return self.score > self.high_score

    def update_high_score(self, initials=""):
        self.high_score = self.score
        self.high_score_initials = initials
        save_high_score(self.high_score, self.high_score_initials)


def create_fonts():
    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 36)
    return font_large, font_medium


def render_centered_text(screen, font, text, color, center_pos):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=center_pos)
    screen.blit(rendered_text, text_rect)


def draw_ui_overlay(screen, font, score, high_score, high_score_initials="", lives=3):
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

    # Lives
    lives_text = font.render(f"Lives: {lives}", True, "white")
    screen.blit(lives_text, (10, 90))


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
    game_state = GameState()

    # Load sounds
    shoot_sound, explosion_sound, death_sound = load_sounds()

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

        player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, shoot_sound)

        dt = 0
        game_state.reset()
        game_over = False
        paused = False
        flash_timer = 0

        while not game_over:  # Single game loop
            # log_state()  # Disabled for performance

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused

            if not paused:
                # Update asteroid field with score for difficulty scaling
                asteroid_field.update(dt, game_state.score)
                # Update all other sprites
                for sprite in updatable:
                    if sprite is not asteroid_field:
                        sprite.update(dt)

                # Check player-asteroid collisions
                for asteroid in asteroids:
                    if player.collides_with(asteroid) and not player.invincible:
                        log_event("player_hit")
                        death_sound.play()
                        flash_timer = FLASH_DURATION
                        game_state.lose_life()
                        if game_state.is_alive():
                            # Respawn player at center
                            player.position = pygame.Vector2(
                                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
                            )
                            player.invincible = True
                            player.invincibility_timer = PLAYER_INVINCIBILITY_SECONDS
                        else:
                            game_over = True
                        break

                # Check asteroid-shot collisions using pygame's groupcollide
                hits = pygame.sprite.groupcollide(asteroids, shots, False, True)
                for asteroid in hits:
                    log_event("asteroid_shot")
                    game_state.add_score(100)
                    explosion_sound.play()
                    asteroid.split()

            screen.fill("black")

            for obj in drawable:
                obj.draw(screen)

            # Draw UI overlay
            draw_ui_overlay(
                screen,
                font,
                game_state.score,
                game_state.high_score,
                game_state.high_score_initials,
                game_state.lives,
            )

            # Draw pause overlay if paused
            if paused:
                font_large, _ = create_fonts()
                render_centered_text(
                    screen,
                    font_large,
                    "PAUSED",
                    "white",
                    (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                )

            # Draw screen flash effect
            if flash_timer > 0:
                flash_timer -= dt
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill(FLASH_COLOR)
                flash_surface.set_alpha(128)
                screen.blit(flash_surface, (0, 0))

            pygame.display.flip()

            # limit framerate to 60 fps
            dt = clock.tick(60) / 1000.0

        # Update high score if current score is higher
        if game_state.check_new_high_score():
            initials = show_high_score_input(screen, clock, game_state.score)
            if initials:  # If not quit
                game_state.update_high_score(initials)
            else:
                game_state.high_score_initials = ""

        # Show game over screen and check if player wants to restart
        if show_game_over(screen, clock, game_state.score):
            continue  # Restart the game
        else:
            break  # Quit the game


if __name__ == "__main__":
    main()
