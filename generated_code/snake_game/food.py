import pygame
import random
from settings import *

class Food:
    def __init__(self):
        self.position = self.randomize_position()
        self.is_powerup = False
        self.determine_powerup()

    def randomize_position(self):
        x = random.randrange(0, SCREEN_WIDTH // GRID_SIZE) * GRID_SIZE
        y = random.randrange(0, SCREEN_HEIGHT // GRID_SIZE) * GRID_SIZE
        self.position = (x, y)
        return self.position

    def determine_powerup(self):
        self.is_powerup = random.random() < POWERUP_PROBABILITY

    def draw(self, screen):
        if self.is_powerup:
            pygame.draw.rect(screen, BLUE, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))
        else:
            pygame.draw.rect(screen, RED, (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))
