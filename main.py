import pygame
from config.settings import *
from utils.sound import load_sounds
from sprites.enemy import Enemy, ShootingEnemy
from sprites.powerup import Powerup

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.sounds = load_sounds()
        self.init_game()

    def init_game(self):
        self.player = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)
        self.enemies = pygame.sprite.Group()
        self.spawn_enemies()
        self.powerup = Powerup()
        self.player_has_power = False
        self.next_powerup_time = pygame.time.get_ticks() + POWERUP_INTERVAL

    def spawn_enemies(self, number=1):
        self.enemies.add(Enemy() for _ in range(number))
        self.enemies.add(ShootingEnemy() for _ in range(number))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = PLAYER_SPRINT_SPEED if keys[pygame.K_LSHIFT] else PLAYER_SPEED
        
        if keys[pygame.K_w]: self.player.y -= speed
        if keys[pygame.K_s]: self.player.y += speed
        if keys[pygame.K_a]: self.player.x -= speed
        if keys[pygame.K_d]: self.player.x += speed
        
        self.player.clamp_ip(self.screen.get_rect())

    def update(self):
        # Update powerup
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
            if current_time >= self.next_powerup_time:
                self.powerup = Powerup()
                self.next_powerup_time = current_time + POWERUP_INTERVAL

        # Update enemies
        for enemy in self.enemies:
            if isinstance(enemy, ShootingEnemy):
                enemy.update(self.player.center, self.player_has_power)
            else:
                enemy.update(self.player.center)

    def check_collisions(self):
        for enemy in self.enemies:
            if self.player.colliderect(enemy.rect):
                if self.player_has_power:
                    if self.sounds['nice']:
                        self.sounds['nice'].play()
                    self.enemies.remove(enemy)
                    self.player_has_power = False
                    self.powerup = Powerup()
                    self.next_powerup_time = pygame.time.get_ticks() + POWERUP_INTERVAL
                else:
                    return True  # Game Over

            if isinstance(enemy, ShootingEnemy):
                for bullet in enemy.bullets:
                    if self.player.colliderect(bullet.rect):
                        if self.player_has_power:
                            if self.sounds['nice']:
                                self.sounds['nice'].play()
                            bullet.kill()
                            self.player_has_power = False
                            self.powerup = Powerup()
                            self.next_powerup_time = pygame.time.get_ticks() + POWERUP_INTERVAL
                        else:
                            return True  # Game Over
        return False

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw powerup
        if self.powerup:
            self.screen.blit(self.powerup.image, self.powerup.rect)
        
        # Draw player
        color = (ORANGE if self.player_has_power and pygame.key.get_pressed()[pygame.K_LSHIFT] else
                YELLOW if self.player_has_power else
                GREEN)
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
                        self.init_game()
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

            # Modified victory condition
            if len(self.enemies) == 0:
                if self.sounds['victory']:
                    self.sounds['victory'].play()
                running = self.game_win_screen()

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()