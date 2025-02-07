import pygame
import random
import math

# 初始化 Pygame 和音频
pygame.init()
pygame.mixer.init()

# 处理音效
try:
    hit_sound = pygame.mixer.Sound("hit.wav")
except pygame.error:
    print("Warning: Missing hit sound file!")
    hit_sound = None  # 避免程序崩溃

# 屏幕设置
screen = pygame.display.set_mode((800, 600))

# 玩家初始化
player = pygame.Rect(400, 300, 50, 50)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))# 红色
        self.rect = self.image.get_rect(center=(random.randint(0, 800), random.randint(0, 600)))# 随机位置
        self.speed = 3
        self.state = "patrol"
        self.patrol_points = [(x, y) for x in range(100, 700, 200) for y in range(100, 500, 200)]# 巡逻点，100是起始位置，700是终点，200是间隔
        self.target_point = random.choice(self.patrol_points)
        self.attack_range = 200
        self.disengage_range = 300

    def update(self, player_pos):# 更新敌人位置
        player_vector = pygame.math.Vector2(player_pos)
        enemy_vector = pygame.math.Vector2(self.rect.center)

        if self.state == "patrol":
            self._patrol()
            if player_vector.distance_to(enemy_vector) < self.attack_range:
                self.state = "attack"
        else:
            self._attack(player_pos)
            if player_vector.distance_to(enemy_vector) > self.disengage_range:
                self.state = "patrol"
                self.target_point = self.rect.center  

    def _patrol(self):
        target_vector = pygame.math.Vector2(self.target_point)
        enemy_vector = pygame.math.Vector2(self.rect.center)
        direction = target_vector - enemy_vector

        if direction.length() > self.speed:
            direction = direction.normalize() * self.speed
        else:
            self.target_point = random.choice(self.patrol_points)

        self.rect.x += direction.x
        self.rect.y += direction.y

    def _attack(self, target):
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance != 0:
            self.rect.x += self.speed * dx / distance
            self.rect.y += self.speed * dy / distance

# 创建敌人组
enemies = pygame.sprite.Group(Enemy() for _ in range(5))

# 计时器
clock = pygame.time.Clock()
running = True

# 游戏主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 玩家控制
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -= 5
    if keys[pygame.K_s]: player.y += 5
    if keys[pygame.K_a]: player.x -= 5
    if keys[pygame.K_d]: player.x += 5
    if keys[pygame.K_ESCAPE]:  # ESC 退出
        running = False

    # 确保玩家不会超出屏幕边界
    player.clamp_ip(screen.get_rect())

    # 更新 AI
    enemies.update(player.center)

    # 检测碰撞并播放音效
    for enemy in enemies:
        if player.colliderect(enemy.rect) and hit_sound:
            hit_sound.play()

    # 渲染
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), player)
    enemies.draw(screen)

    # 显示敌人数量
    font = pygame.font.Font(None, 36)
    text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()