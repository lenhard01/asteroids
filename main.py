import pygame
from constants import *


def main():
    pygame.init
    print("Starting Asteroids!")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Fill the screen with a solid "black" color
        screen.fill("black")

        # Refresh the screen (must be called last)
        pygame.display.flip()


if __name__ == "__main__":
    main()
