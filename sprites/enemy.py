import pygame
import random
import math
from config.settings import *
from .bullet import Bullet

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(PURPLE)
        self._init_position()
        self._init_movement()

    def _init_position(self):
        rx = list(range(0, 301)) + list(range(500, SCREEN_WIDTH + 1))
        ry = list(range(0, 201)) + list(range(400, SCREEN_HEIGHT + 1))
        x, y = random.choice(rx), random.choice(ry)
        self.rect = self.image.get_rect(center=(x, y))

    def _init_movement(self):
        self.speed = ENEMY_SPEED
        self.state = "patrol"
        self.patrol_points = [(x, y) for x in range(0, SCREEN_WIDTH, 200) 
                            for y in range(0, SCREEN_HEIGHT, 200)]
        self.target_point = random.choice(self.patrol_points)
        self.attack_range = ATTACK_RANGE
        self.disengage_range = DISENGAGE_RANGE

    def update(self, player_pos):
        pv = pygame.math.Vector2(player_pos)
        ev = pygame.math.Vector2(self.rect.center)

        if self.state == "patrol":
            self._patrol()
            if pv.distance_to(ev) < self.attack_range:
                self.state = "attack"
        else:
            self._attack(player_pos)
            if pv.distance_to(ev) > self.disengage_range:
                self.state = "patrol"
                self.target_point = self.rect.center

    def _patrol(self):
        tv = pygame.math.Vector2(self.target_point)
        ev = pygame.math.Vector2(self.rect.center)
        d = tv - ev

        if d.length() > self.speed:
            d = d.normalize() * self.speed
        else:
            self.target_point = random.choice(self.patrol_points)

        self.rect.x += d.x
        self.rect.y += d.y

    def _attack(self, target):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist != 0:
            self.rect.x += self.speed * dx / dist
            self.rect.y += self.speed * dy / dist

class ShootingEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.speed = SHOOTING_ENEMY_SPEED
        self.image = pygame.Surface((SHOOTING_ENEMY_SIZE, SHOOTING_ENEMY_SIZE)) #很重要，要先设置大小，再填充颜色，新的Surface会覆盖原有的Surface，没搞懂
        self.image.fill(RED)
        self.shoot_cooldown = SHOOT_COOLDOWN
        self.last_shot = 0
        self.bullets = pygame.sprite.Group()

    def update(self, player_pos, player_has_power=False):
        if player_has_power:
            self.runaway(player_pos)
        else:
            super().update(player_pos)
            
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            self.shoot_bullet(player_pos)
            self.last_shot = now
        self.bullets.update()

    def shoot_bullet(self, target):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        direction = pygame.math.Vector2(dx, dy).normalize()
        self.bullets.add(Bullet(self.rect.center, direction))

    def runaway(self, player_pos):
        dx = self.rect.centerx - player_pos[0]
        dy = self.rect.centery - player_pos[1]
        dist = math.hypot(dx, dy)
        if dist != 0:
            new_x = self.rect.x + self.speed * dx / dist
            new_y = self.rect.y + self.speed * dy / dist
            if 0 <= new_x <= SCREEN_WIDTH-ENEMY_SIZE and 0 <= new_y <= SCREEN_HEIGHT-ENEMY_SIZE:
                self.rect.x = new_x
                self.rect.y = new_y

class StrongEnemy(Enemy):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((STRONG_ENEMY_SIZE, STRONG_ENEMY_SIZE))
        self.image.fill(PURPLE)  # 初始颜色
        self.speed = STRONG_ENEMY_SPEED
        self.hp = STRONG_ENEMY_HP
        # 删除左右往返移动的属性

    def update(self, player_pos):
        # 始终向玩家追随
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            # 使用归一化方向向量更新位置
            self.rect.x += int(self.speed * dx / dist)
            self.rect.y += int(self.speed * dy / dist)

    def hit(self):
        self.hp -= 1
        # 根据剩余血量改变颜色
        if self.hp == 2:
            self.image.fill(DARK_PURPLE)
        elif self.hp == 1:
            self.image.fill(MIDNIGHT_PURPLE)
        # 血量归零时移除敌人
        if self.hp <= 0:
            self.kill()
            return True
        return False