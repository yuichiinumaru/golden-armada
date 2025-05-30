import pygame
from settings import *

class Snake:
    def __init__(self):
        self.body = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = "right"
        self.new_direction = self.direction # added to avoid reversing

    def set_direction(self, direction):
        if (direction == "up" and self.direction != "down") or \
           (direction == "down" and self.direction != "up") or \
           (direction == "left" and self.direction != "right") or \
           (direction == "right" and self.direction != "left"):
            self.new_direction = direction

    def move(self):
        self.direction = self.new_direction
        x, y = self.body[0]
        if self.direction == "up":
            y -= GRID_SIZE
        elif self.direction == "down":
            y += GRID_SIZE
        elif self.direction == "left":
            x -= GRID_SIZE
        elif self.direction == "right":
            x += GRID_SIZE
        self.body.insert(0, (x, y))
        self.body.pop()

    def grow(self):
        x, y = self.body[0]
        if self.direction == "up":
            y -= GRID_SIZE
        elif self.direction == "down":
            y += GRID_SIZE
        elif self.direction == "left":
            x -= GRID_SIZE
        elif self.direction == "right":
            x += GRID_SIZE
        self.body.insert(0, (x, y))

    def check_collision(self):
        # Check collision with itself
        if len(self.body) > 1 and self.body[0] in self.body[1:]:
            return True
        return False

    def draw(self, screen):
        for x, y in self.body:
            pygame.draw.rect(screen, GREEN, (x, y, GRID_SIZE, GRID_SIZE))
