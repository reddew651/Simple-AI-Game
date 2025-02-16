import pygame
from config.settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=pos)
        self.speed = BULLET_SPEED
        self.direction = direction

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed