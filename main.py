import pygame
from logger import log_state
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pygame.time.Clock()
    dt = 0
    
    while True:
        log_state()
        for event in pygame.event.get():
            pass
        screen.fill("black")
        player.draw(screen)
        pygame.display.flip()
        player.update(dt)

        dt = pygame.time.Clock().tick(60) / 1000.0
        # print(f"Delta time: {dt} seconds")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
    
    # print("Starting Asteroids with pygame version: VERSION")
    # print("Screen width: 1280")
    # print("Screen height: 720")


if __name__ == "__main__":
    main()
