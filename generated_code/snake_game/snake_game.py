
import pygame
import time
from snake import Snake
from food import Food
from settings import *

pygame.init()

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Difficulty selection
difficulty = None
while difficulty is None:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = EASY
            elif event.key == pygame.K_2:
                difficulty = MEDIUM
            elif event.key == pygame.K_3:
                difficulty = HARD
    screen.fill(BLACK)
    font = pygame.font.Font(None, 36)
    text1 = font.render("Select difficulty:", True, WHITE)
    text2 = font.render("1 - Easy", True, WHITE)
    text3 = font.render("2 - Medium", True, WHITE)
    text4 = font.render("3 - Hard", True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, SCREEN_HEIGHT // 4))
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, SCREEN_HEIGHT // 4 + 50))
    screen.blit(text3, (SCREEN_WIDTH // 2 - text3.get_width() // 2, SCREEN_HEIGHT // 4 + 100))
    screen.blit(text4, (SCREEN_WIDTH // 2 - text4.get_width() // 2, SCREEN_HEIGHT // 4 + 150))
    pygame.display.flip()


# Snake and Food objects
snake = Snake()
food = Food()

# Game loop
game_over = False
powerup_timer = 0

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != "down":
                snake.direction = "up"
            if event.key == pygame.K_DOWN and snake.direction != "up":
                snake.direction = "down"
            if event.key == pygame.K_LEFT and snake.direction != "right":
                snake.direction = "left"
            if event.key == pygame.K_RIGHT and snake.direction != "left":
                snake.direction = "right"

    # Snake movement
    snake.move()

    # Collision detection with food
    if snake.body[0] == food.position:
        snake.grow()
        if food.is_powerup:
            powerup_timer = 5  # Power-up lasts for 5 seconds
        food.randomize_position()
        food.determine_powerup()

    # Collision detection with walls
    if snake.body[0][0] < 0 or snake.body[0][0] >= SCREEN_WIDTH or \
       snake.body[0][1] < 0 or snake.body[0][1] >= SCREEN_HEIGHT:
        game_over = True

    # Collision detection with itself
    if snake.check_collision():
        game_over = True

    # Clear the screen
    screen.fill(BLACK)

    # Draw snake
    snake.draw(screen)

    # Draw food
    food.draw(screen)

    # Update the display
    pygame.display.flip()

    # Control game speed
    current_speed = difficulty
    if powerup_timer > 0:
        current_speed = difficulty / 2  # Increase speed during power-up
        powerup_timer -= 1
    time.sleep(current_speed)

pygame.quit()
