import pygame
from config.settings import *
from utils.sound import load_sounds
from sprites.enemy import Enemy, ShootingEnemy, StrongEnemy
from sprites.powerup import Powerup

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.sounds = load_sounds()
        self.init_game()

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
            self.enemies.add(Enemy() for _ in range(1))
            self.enemies.add(ShootingEnemy() for _ in range(1))
            self.enemies.add(StrongEnemy() for _ in range(1))
        elif level == 2:
            # 生成普通敌人 + 射击敌人
            self.enemies.add(Enemy() for _ in range(1))
            self.enemies.add(ShootingEnemy() for _ in range(1))
        elif level == 3:
            # 生成普通敌人 + 射击敌人 + 强敌
            self.enemies.add(Enemy() for _ in range(1))
            self.enemies.add(ShootingEnemy() for _ in range(1))
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

    def game_over_screen(self):
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
                        # 调用 init_game 时，将 self.current_level 传进去
                        self.init_game(self.current_level)
                        current_time = pygame.time.get_ticks()
                        self.player_invincible = True
                        self.invincible_until = pygame.time.get_ticks() + 2000
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
        return True

    def game_win_screen(self):
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
                        self.init_game()
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
        return True

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            self.handle_input()
            self.update()
            
            if self.check_collisions():
                if self.sounds['hit']:
                    self.sounds['hit'].play()
                running = self.game_over_screen()
            
            self.draw()

            # 当所有敌人清空时，切换到下一关或显示胜利画面
            if len(self.enemies) == 0:
                if self.current_level == 1:
                    # 切换到第二关
                    self.current_level = 2
                    self.spawn_enemies(self.current_level)
                    self.player_invincible = True
                    self.invincible_until = pygame.time.get_ticks() + 2000
                    self.powerup = Powerup()
                elif self.current_level == 2:
                    # 切换到第三关
                    self.current_level = 3
                    self.spawn_enemies(self.current_level)
                    self.player_invincible = True
                    self.invincible_until = pygame.time.get_ticks() + 2000
                    self.powerup = Powerup()
                else:
                    # 已通过最后一关
                    if self.sounds['victory']:
                        self.sounds['victory'].play()
                    running = self.game_win_screen()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()