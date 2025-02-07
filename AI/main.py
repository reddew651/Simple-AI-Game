# main.py
import pygame
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30,30))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center=(400,300))
        self.speed = 3
        
    # 简单AI：向玩家移动
    def update(self, player_pos):
        dx = player_pos[0] - self.rect.x
        dy = player_pos[1] - self.rect.y
        distance = (dx**2 + dy**2)**0.5
        if distance != 0:
            self.rect.x += self.speed * dx/distance
            self.rect.y += self.speed * dy/distance

pygame.init()
screen = pygame.display.set_mode((800,600))
player = pygame.Rect(400,300,50,50)
enemies = pygame.sprite.Group(Enemy() for _ in range(5))

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 玩家控制
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -=5
    if keys[pygame.K_s]: player.y +=5
    if keys[pygame.K_a]: player.x -=5
    if keys[pygame.K_d]: player.x +=5
    
    # AI更新
    enemies.update(player.center)
    

    
    # 渲染
    screen.fill((0,0,0))
    pygame.draw.rect(screen, (0,255,0), player)
    enemies.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()


class Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.state = "patrol"  # patrol/attack
        self.patrol_points = [(x,y) for x in range(100,700,200) for y in range(100,500,200)]
        self.target_point = random.choice(self.patrol_points)
        
    def update(self, player_pos):
        if self.state == "patrol":
            self._patrol()
            if pygame.math.Vector2(player_pos).distance_to(self.rect.center) < 200:
                self.state = "attack"
        else:
            self._attack(player_pos)
            if pygame.math.Vector2(player_pos).distance_to(self.rect.center) > 300:
                self.state = "patrol"
                
    def _patrol(self):
        # 实现巡逻逻辑
        pass
        
    def _attack(self, target):
        # 实现攻击逻辑
        pass

# 在渲染循环中添加
font = pygame.font.Font(None, 36)
text = font.render(f"Enemies: {len(enemies)}", True, (255,255,255))
screen.blit(text, (10,10))

pygame.mixer.init()
hit_sound = pygame.mixer.Sound("hit.wav")
hit_sound.play()