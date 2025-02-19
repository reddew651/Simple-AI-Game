import pygame
from config.settings import *
from utils.sound import load_sounds
from sprites.enemy import Enemy, ShootingEnemy, StrongEnemy, CopyEnemy
from sprites.powerup import Powerup

class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 74)
        self.title_font = pygame.font.Font(None, 100)
        self.buttons = [
            {"rect": pygame.Rect(SCREEN_WIDTH//2-100, 200, 200, 50), "text": "Level 1", "level": 1},
            {"rect": pygame.Rect(SCREEN_WIDTH//2-100, 300, 200, 50), "text": "Level 2", "level": 2},
            {"rect": pygame.Rect(SCREEN_WIDTH//2-100, 400, 200, 50), "text": "Level 3", "level": 3}
        ]
        self.hovered = None

    def draw(self):
        self.screen.fill(BLACK)
        # 绘制标题
        title = self.title_font.render("Space Shooter", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # 绘制按钮
        for btn in self.buttons:
            color = GREEN if self.hovered == btn["level"] else GRAY
            pygame.draw.rect(self.screen, color, btn["rect"])
            text = self.font.render(btn["text"], True, WHITE)
            text_rect = text.get_rect(center=btn["rect"].center)
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = None
        for btn in self.buttons:
            if btn["rect"].collidepoint(mouse_pos):
                self.hovered = btn["level"]
                if pygame.mouse.get_pressed()[0]:
                    return btn["level"]
        return None

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.sounds = load_sounds()
        self.menu = StartMenu(self.screen)
        self.state = "menu"  # 游戏状态：menu/playing/game_over/victory
        self.init_game()

    # ... 保持原有 init_game 方法不变 ...
    def init_game(self, level=1):
        """增加 level 参数，用于控制重开的关卡。"""
        self.current_level = level
        self.player = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)
        self.enemies = pygame.sprite.Group()
        self.spawn_enemies(self.current_level)
        self.powerup = Powerup()
        self.player_has_power = False
        self.next_powerup_time = pygame.time.get_ticks() + POWERUP_INTERVAL
        #增加无敌帧
        self.player_invincible = True
        self.invincible_until = 1000

    def spawn_enemies(self, level=1):
        if level == 1:
            # 仅生成普通敌人
            #self.enemies.add(Enemy() for _ in range(1))
            copy_enemy = CopyEnemy()
            copy_enemy.enemy_group = self.enemies
            self.enemies.add(copy_enemy)

        elif level == 2:
            # 生成普通敌人 + 射击敌人
            #self.enemies.add(Enemy() for _ in range(1))
            self.enemies.add(ShootingEnemy() for _ in range(1))
        elif level == 3:
            # 生成普通敌人 + 射击敌人 + 强敌
            #self.enemies.add(Enemy() for _ in range(1))
            #self.enemies.add(ShootingEnemy() for _ in range(1))
            self.enemies.add(StrongEnemy() for _ in range(1))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = PLAYER_SPRINT_SPEED if self.player_has_power else PLAYER_SPEED
        
        if keys[pygame.K_w]: self.player.y -= speed
        if keys[pygame.K_s]: self.player.y += speed
        if keys[pygame.K_a]: self.player.x -= speed
        if keys[pygame.K_d]: self.player.x += speed
        
        self.player.clamp_ip(self.screen.get_rect())

    def update(self):
        if self.powerup:
            self.powerup.update()

        # Check powerup collection
        if self.powerup and self.player.colliderect(self.powerup.rect):
            self.player_has_power = True
            if self.sounds['get']:
                self.sounds['get'].play()
            self.powerup = None

        # Spawn new powerup
        if not self.powerup and not self.player_has_power:
            current_time = pygame.time.get_ticks()
            if current_time >= self.next_powerup_time: #if 
                self.powerup = Powerup()
                self.next_powerup_time = current_time + POWERUP_INTERVAL

        # Update enemies
        for enemy in self.enemies:
            if isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.center, self.player_has_power)
            else:
                enemy.update(self.player.center)

    def check_collisions(self):
        current_time = pygame.time.get_ticks()
        # 如果玩家处于无敌状态则跳过碰撞检测
        if self.player_invincible and current_time < self.invincible_until:
            return False
        
        self.player_invincible = False #重要一步，否则无敌状态会一直保持

        for enemy in self.enemies.copy():
            if self.player.colliderect(enemy.rect):
                if isinstance(enemy, StrongEnemy):#检查和强敌的碰撞
                    if self.player_has_power:
                        if self.sounds['nice']:
                            self.sounds['nice'].play()
                        # 当 StrongEnemy 受到碰撞时调用 hit() 方法
                        if enemy.hit():
                            self.enemies.remove(enemy)
                        self.player_has_power = False
                        #self.powerup = Powerup() # if add this the powerup will appear once the enemy is killed
                        self.next_powerup_time = current_time + POWERUP_INTERVAL
                        # 设置无敌状态，给予玩家反应时间
                        self.player_invincible = True
                        self.invincible_until = current_time + 200
                    else:
                        return True  # Game Over
                else:#检查和普通敌人的碰撞
                    if self.player_has_power:
                        if self.sounds['nice']:
                            self.sounds['nice'].play()
                        self.enemies.remove(enemy)
                        self.player_has_power = False
                        #self.powerup = Powerup()
                        self.next_powerup_time = current_time + POWERUP_INTERVAL
                        self.player_invincible = True
                        self.invincible_until = current_time + 200
                    else:
                        return True  # Game Over

            if isinstance(enemy, ShootingEnemy):#检查和射击敌人子弹的碰撞
                for bullet in enemy.bullets.copy():
                    if self.player.colliderect(bullet.rect):
                        if self.player_has_power:
                            if self.sounds['nice']:
                                self.sounds['nice'].play()
                            bullet.kill()
                            self.player_has_power = False
                            #self.powerup = Powerup()
                            self.next_powerup_time = current_time + POWERUP_INTERVAL
                            self.player_invincible = True
                            self.invincible_until = current_time + 200
                        else:
                            return True  # Game Over
        return False
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw powerup
        if self.powerup:
            self.screen.blit(self.powerup.image, self.powerup.rect)
        
        # Draw player
        color = (ORANGE if self.player_invincible == True else YELLOW if self.player_has_power and self.player_invincible == False else GREEN)
        pygame.draw.rect(self.screen, color, self.player)
        
        # Draw enemies and bullets
        self.enemies.draw(self.screen)
        for enemy in self.enemies:
            if isinstance(enemy, ShootingEnemy):
                enemy.bullets.draw(self.screen)
        
        pygame.display.flip()

        

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    else:
                        running = False

            if self.state == "menu":
                # 处理菜单界面
                selected_level = self.menu.handle_input()
                if selected_level:
                    self.init_game(selected_level)
                    self.state = "playing"
                    self.player_invincible = True
                    self.invincible_until = pygame.time.get_ticks() + 2000
                self.menu.draw()
            
            elif self.state == "playing":
                # 处理游戏逻辑
                self.handle_input()
                self.update()
                
                if self.check_collisions():
                    if self.sounds['hit']:
                        self.sounds['hit'].play()
                    self.state = "game_over"
                
                self.draw()

                # 关卡通关检测
                if len(self.enemies) == 0:
                    if self.current_level < 3:
                        self.current_level += 1
                        self.spawn_enemies(self.current_level)
                        self.player_invincible = True
                        self.invincible_until = pygame.time.get_ticks() + 2000
                        self.powerup = Powerup()
                    else:
                        if self.sounds['victory']:
                            self.sounds['victory'].play()
                        self.state = "victory"

            elif self.state == "game_over":
                running = self.game_over_screen()
            
            elif self.state == "victory":
                running = self.game_win_screen()

        pygame.quit()

    # 修改游戏结束画面处理
    def game_over_screen(self):
        # ... 保持原有绘制代码不变 ...
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over, Press R to Restart", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
    
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.state = "menu"
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
        return True

    def game_win_screen(self):
        # ... 保持原有绘制代码不变 ...
        font = pygame.font.Font(None, 74)
        text = font.render("Victory! Press R to Restart", True, GREEN)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.state = "menu"
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
        return True

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()