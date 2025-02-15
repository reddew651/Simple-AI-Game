import pygame
import random
import math

# 初始化 Pygame 和音频
pygame.init()
pygame.mixer.init()

# 处理音效
try:
    pygame.mixer.music.load("sounds/music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1) 
    victory_sound = pygame.mixer.Sound("sounds/victory.wav")
    get_sound = pygame.mixer.Sound("sounds/get.wav")
    nice_sound = pygame.mixer.Sound("sounds/nice.wav")
    hit_sound = pygame.mixer.Sound("sounds/hit.wav")
except pygame.error:
    print("Warning: Missing sounds file!")
    get_sound = nice_sound = hit_sound = victory_sound = None

# 屏幕设置
screen = pygame.display.set_mode((800, 600))

# 玩家初始化
player = pygame.Rect(400, 300, 50, 50)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((148, 0, 211))
        rx = list(range(0, 301)) + list(range(500, 801))
        ry = list(range(0, 201)) + list(range(400, 601))
        x, y = random.choice(rx), random.choice(ry)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
        self.state = "patrol"
        self.patrol_points = [(x, y) for x in range(0, 800, 200) for y in range(9, 600, 200)]
        self.target_point = random.choice(self.patrol_points)
        self.attack_range = 200
        self.disengage_range = 300

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

# 创建敌人组
number = 4
enemies = pygame.sprite.Group(Enemy() for _ in range(number))

class Powerup(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(random.randint(0, 800), random.randint(0, 600)))
        self.speed_x = random.choice([-2, 2])
        self.speed_y = random.choice([-2, 2])
        
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # 边缘反弹
        if self.rect.left < 0 or self.rect.right > 800:
            self.speed_x = -self.speed_x
        if self.rect.top < 0 or self.rect.bottom > 600:
            self.speed_y = -self.speed_y

# 创建移动道具，而不是pygame.Rect
powerup = Powerup()
player_has_power = False

# 计时器
clock = pygame.time.Clock()
running = True
next_powerup_time = pygame.time.get_ticks() + 10000

# 游戏主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 玩家控制
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player.y -= 4
    if keys[pygame.K_s]: player.y += 4
    if keys[pygame.K_a]: player.x -= 4
    if keys[pygame.K_d]: player.x += 4
    if keys[pygame.K_LSHIFT]: 
        if keys[pygame.K_w]: player.y -= 6
        if keys[pygame.K_s]: player.y += 6
        if keys[pygame.K_a]: player.x -= 6
        if keys[pygame.K_d]: player.x += 6
    if keys[pygame.K_ESCAPE]:  # ESC 退出
        running = False

    # 确保玩家不会超出屏幕边界
    player.clamp_ip(screen.get_rect())

    # 更新道具位置
    if powerup:
        powerup.update()

    # 如果有道具，检测和玩家的碰撞
    if powerup and player.colliderect(powerup.rect):
        player_has_power = True
        if get_sound:
            get_sound.play()
        powerup = None  # 道具消失

    # 每隔 10 秒生成一个道具（如果当前没有道具）
    if not powerup and pygame.time.get_ticks() >= next_powerup_time and not player_has_power:
        powerup = Powerup()
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
                powerup = Powerup()
                next_powerup_time = pygame.time.get_ticks() + 10000
            else:
                # 无道具则游戏结束
                if hit_sound:
                    hit_sound.play()
                font_game_over = pygame.font.Font(None, 74)
                game_over_text = font_game_over.render("Game Over, Press r Again", True, (255, 0, 0))
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
                                enemies.add(Enemy() for _ in range(number))
                                powerup = Powerup()
                                player_has_power = False
                                waiting = False
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                                waiting = False
                break

    # 如果所有敌人都消灭，则胜利
    if len(enemies) == 0:
        pygame.mixer.music.stop()
        font_win = pygame.font.Font(None, 74)
        win_text = font_win.render("You Win!", True, (255, 255, 0))
        screen.blit(win_text, win_text.get_rect(center=(400, 300)))
        if victory_sound:
            victory_sound.play()
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    # 渲染
    screen.fill((0, 0, 0))
    # 道具
    if powerup:
        screen.blit(powerup.image, powerup.rect)

    # 玩家
    if player_has_power:
        if keys[pygame.K_LSHIFT]:
            pygame.draw.rect(screen, (255, 165, 0), player)
        else:
            pygame.draw.rect(screen, (255, 255, 0), player)
    else:
        if keys[pygame.K_LSHIFT]:
            pygame.draw.rect(screen, (80, 169, 0), player)
        else:
            pygame.draw.rect(screen, (0, 255, 0), player)

    enemies.draw(screen)

    # 显示敌人数量
    font = pygame.font.Font(None, 36)
    text = font.render(f"Enemies: {len(enemies)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(50)

pygame.quit()