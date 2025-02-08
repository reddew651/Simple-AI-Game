import pygame
import random
import math

# 初始化 Pygame 和音频
pygame.init()
pygame.mixer.init()

# 处理音效
try:
    nice_sound = pygame.mixer.Sound("nice.wav")
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
        self.image = pygame.Surface((30, 30))
        self.image.fill((148, 0, 211))
        valid_x_range = list(range(0,301))+list(range(500,801))
        valid_y_range = list(range(0,201))+list(range(400,601))
        random.choice(valid_x_range)
        random.choice(valid_y_range)
        x=random.choice(valid_x_range)
        y=random.choice(valid_y_range)
        self.rect = self.image.get_rect(center=(x,y))# 随机位置
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

# 创建道具
powerup = pygame.Rect(random.randint(0, 770), random.randint(0, 570), 30, 30)
player_has_power = False

# 计时器
clock = pygame.time.Clock()
running = True

next_powerup_time = pygame.time.get_ticks() + 30000

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

    # 如果有道具，检测和玩家的碰撞
    if powerup and player.colliderect(powerup):
        player_has_power = True
        powerup = None  # 道具消失

    # 每隔 10 秒生成一个道具（如果当前没有道具）
    if not powerup and pygame.time.get_ticks() >= next_powerup_time:
        powerup = pygame.Rect(random.randint(0, 770), random.randint(0, 570), 30, 30)
        next_powerup_time = pygame.time.get_ticks() + 10000

    # 更新 AI
    enemies.update(player.center)

    # 检测碰撞
    for enemy in enemies:
        if player.colliderect(enemy.rect):
            if player_has_power:
                # 消灭敌人并失去一次道具效果
                if nice_sound:
                    nice_sound.play()
                enemies.remove(enemy)
                player_has_power = False
            else:
                # 无道具则游戏结束
                if hit_sound:
                    hit_sound.play()
                font_game_over = pygame.font.Font(None, 74)
                game_over_text = font_game_over.render("Game Over, Press r To New", True, (255, 0, 0))
                text_rect = game_over_text.get_rect(center=(400, 300))
                screen.blit(game_over_text, text_rect)
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                player.x, player.y = 400, 300
                                enemies.empty()
                                enemies.add(Enemy() for _ in range(5))
                                powerup = pygame.Rect(random.randint(0, 770), random.randint(0, 570), 30, 30)
                                player_has_power = False
                                waiting = False
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                                waiting = False
                break

    # 如果所有敌人都消灭，则胜利
    if len(enemies) == 0:
        font_win = pygame.font.Font(None, 74)
        win_text = font_win.render("You Win!", True, (255, 255, 0))
        screen.blit(win_text, win_text.get_rect(center=(400, 300)))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    # 渲染
    screen.fill((0, 0, 0))
    # 道具
    if powerup:
        pygame.draw.rect(screen, (255, 255, 0), powerup)

    # 玩家
    if player_has_power:
        pygame.draw.rect(screen, (255, 255, 0), player)
    else:
        pygame.draw.rect(screen, (0, 255, 0), player)

    enemies.draw(screen)

    # 显示敌人数量
    font = pygame.font.Font(None, 36)
    text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()