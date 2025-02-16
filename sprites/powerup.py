import pygame
import random
from config.settings import *

class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(
            center=(random.randint(0, SCREEN_WIDTH), 
                   random.randint(0, SCREEN_HEIGHT))
        )
        self.speed_x = random.choice([-POWERUP_SPEED, POWERUP_SPEED])
        self.speed_y = random.choice([-POWERUP_SPEED, POWERUP_SPEED])

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y *= -1