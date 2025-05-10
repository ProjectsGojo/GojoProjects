import pygame
import random
import time
import json
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Размеры экрана
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Настройки игры
DIFFICULTY = {
    "easy": {"fps": 8, "grid": 20},
    "medium": {"fps": 12, "grid": 20},
    "hard": {"fps": 15, "grid": 20}
}
current_difficulty = "medium"
FPS = DIFFICULTY[current_difficulty]["fps"]

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()

# Звуки
try:
    eat_sound = mixer.Sound("eat.wav")  # Создайте или найдите звуковой файл
    game_over_sound = mixer.Sound("game_over.wav")
    bonus_sound = mixer.Sound("bonus.wav")
except:
    print("Звуковые файлы не найдены, игра продолжится без звука")

class Particle:
    def __init__(self, x, y):
        self.x = x * GRID_SIZE + GRID_SIZE // 2
        self.y = y * GRID_SIZE + GRID_SIZE // 2
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = random.choice([RED, YELLOW, ORANGE])
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class Bonus:
    def __init__(self):
        self.position = (0, 0)
        self.active = False
        self.time_left = 0
        self.type = random.choice(["double_score", "invincibility", "teleport"])
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 5000  # 5 секунд

    def randomize_position(self, snake_positions, obstacles):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                           random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions and self.position not in obstacles:
                break
        self.spawn_time = pygame.time.get_ticks()
        self.active = True

    def draw(self):
        if self.active:
            now = pygame.time.get_ticks()
            if now - self.spawn_time < self.duration:
                if self.type == "double_score":
                    color = YELLOW
                elif self.type == "invincibility":
                    color = CYAN
                else:  # teleport
                    color = BLUE
                
                # Мигающий эффект
                if (now // 200) % 2 == 0:
                    rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                                     self.position[1] * GRID_SIZE, 
                                     GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)
            else:
                self.active = False

class Food:
    def __init__(self):
        self.types = [
            {"color": WHITE, "effect": "grow", "score": 1},
            {"color": RED, "effect": "speed_up", "score": 3},
            {"color": BLUE, "effect": "slow_down", "score": 2},
            {"color": YELLOW, "effect": "reverse", "score": 5}
        ]
        self.current = random.choice(self.types)
        self.position = (0, 0)
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
        self.current = random.choice(self.types)
    
    def draw(self):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, 
                          self.position[1] * GRID_SIZE, 
                          GRID_SIZE, GRID_SIZE)
        pygame.draw.ellipse(screen, self.current["color"], rect)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.speed_multiplier = 1
        self.invincible = False
        self.invincible_timer = 0
        self.just_ate = False
        self.particles = []
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self, obstacles):
        # Обновление комбо
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
            
        # Обновление неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
            
        # Обновление позиции
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x) % GRID_WIDTH
        new_y = (head_y + dir_y) % GRID_HEIGHT
        
        # Проверка на столкновение с собой
        if (new_x, new_y) in self.positions[1:] and not self.invincible:
            return False
            
        # Проверка на столкновение с препятствиями
        if (new_x, new_y) in obstacles and not self.invincible:
            return False
            
        self.positions.insert(0, (new_x, new_y))
        if len(self.positions) > self.length:
            self.positions.pop()
            
        # Обновление частиц
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
        self.just_ate = False
        return True
    
    def grow(self, amount=1):
        self.length += amount
        self.score += amount * (1 + self.combo)
        self.combo += 1
        self.combo_timer = 30
        self.just_ate = True
        
        # Создание частиц
        for _ in range(10):
            self.particles.append(Particle(*self.get_head_position()))
        
        try:
            eat_sound.play()
        except:
            pass
    
    def activate_bonus(self, bonus):
        try:
            bonus_sound.play()
        except:
            pass
            
        if bonus.type == "double_score":
            self.score += 10
        elif bonus.type == "invincibility":
            self.invincible = True
            self.invincible_timer = 200  # 200 кадров
        elif bonus.type == "teleport":
            self.positions[0] = (random.randint(0, GRID_WIDTH - 1), 
                                random.randint(0, GRID_HEIGHT - 1))
    
    def change_speed(self, multiplier):
        self.speed_multiplier = multiplier
    
    def reverse(self):
        self.direction = (-self.direction[0], -self.direction[1])
        self.positions = self.positions[::-1]
    
    def draw(self):
        # Отрисовка частиц
        for particle in self.particles:
            particle.draw(screen)
            
        # Отрисовка змейки
        for i, (x, y) in enumerate(self.positions):
            if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
                color = CYAN if i == 0 else (0, 255, 255)
            else:
                color = GREEN if i == 0 else (0, 200 - i*2, 0)
                
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 100, 0), rect, 1)
            
        # Отрисовка комбо
        if self.combo > 1:
            font = pygame.font.SysFont('arial', 20)
            combo_text = font.render(f'x{self.combo}', True, WHITE)
            head_pos = self.get_head_position()
            screen.blit(combo_text, (head_pos[0] * GRID_SIZE + GRID_SIZE//2 - combo_text.get_width()//2,
                                    head_pos[1] * GRID_SIZE - 20))

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.bonus = Bonus()
        self.obstacles = []
        self.generate_map()
        self.running = True
        self.game_over = False
        self.paused = False
        self.high_score = self.load_highscore()
        self.bg_color = [0, 0, 0]
        self.color_direction = 1
        self.day_night_cycle = 0
        
    def generate_map(self):
        # Генерация случайных препятствий
        self.obstacles = []
        for _ in range(20):
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), 
                      random.randint(0, GRID_HEIGHT - 1))
                if pos not in self.snake.positions and pos != self.food.position:
                    self.obstacles.append(pos)
                    break
    
    def load_highscore(self):
        try:
            with open("highscore.json", "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except:
            return 0
    
    def save_highscore(self):
        data = {"high_score": max(self.snake.score, self.high_score)}
        with open("highscore.json", "w") as f:
            json.dump(data, f)
    
    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))
    
    def draw_obstacles(self):
        for obs in self.obstacles:
            rect = pygame.Rect(obs[0] * GRID_SIZE, obs[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    def show_game_over(self):
        font = pygame.font.SysFont('arial', 36)
        text = font.render(f'Игра окончена! Счет: {self.snake.score}', True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 
                          HEIGHT // 2 - text.get_height() // 2))
        
        font_small = pygame.font.SysFont('arial', 24)
        restart_text = font_small.render('Нажмите SPACE для новой игры', True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 
                                  HEIGHT // 2 + 50))
        
        high_score_text = font_small.render(f'Рекорд: {max(self.snake.score, self.high_score)}', True, YELLOW)
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 
                                     HEIGHT // 2 + 100))
        
        pygame.display.update()
        
        try:
            game_over_sound.play()
        except:
            pass
    
    def show_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('arial', 36)
        text = font.render('ПАУЗА', True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 
                          HEIGHT // 2 - text.get_height() // 2))
        
        font_small = pygame.font.SysFont('arial', 24)
        continue_text = font_small.render('Нажмите P для продолжения', True, WHITE)
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, 
                                   HEIGHT // 2 + 50))
        
        pygame.display.update()
    
    def draw_hud(self):
        font = pygame.font.SysFont('arial', 20)
        
        # Счет
        score_text = font.render(f'Счет: {self.snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Рекорд
        high_score_text = font.render(f'Рекорд: {max(self.snake.score, self.high_score)}', True, YELLOW)
        screen.blit(high_score_text, (10, 40))
        
        # Сложность
        difficulty_text = font.render(f'Сложность: {current_difficulty}', True, WHITE)
        screen.blit(difficulty_text, (WIDTH - difficulty_text.get_width() - 10, 10))
        
        # Неуязвимость
        if self.snake.invincible:
            inv_text = font.render(f'Неуязвимость: {self.snake.invincible_timer//10}s', True, CYAN)
            screen.blit(inv_text, (WIDTH - inv_text.get_width() - 10, 40))
    
    def update_background(self):
        # Плавное изменение цвета фона (день/ночь)
        self.day_night_cycle += 0.1
        self.bg_color[0] = int(50 + 50 * abs(pygame.math.Vector2(1, 0).rotate(self.day_night_cycle).x))
        self.bg_color[1] = int(50 + 50 * abs(pygame.math.Vector2(1, 0).rotate(self.day_night_cycle * 1.3).x))
        self.bg_color[2] = int(50 + 50 * abs(pygame.math.Vector2(1, 0).rotate(self.day_night_cycle * 0.7).x))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.__init__()  # Перезапуск игры
                elif self.paused:
                    if event.key == pygame.K_p:
                        self.paused = False
                else:
                    if event.key == pygame.K_UP and self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)
                    elif event.key == pygame.K_p:
                        self.paused = True
                    elif event.key == pygame.K_1:
                        global current_difficulty, FPS
                        current_difficulty = "easy"
                        FPS = DIFFICULTY[current_difficulty]["fps"]
                    elif event.key == pygame.K_2:
                        current_difficulty = "medium"
                        FPS = DIFFICULTY[current_difficulty]["fps"]
                    elif event.key == pygame.K_3:
                        current_difficulty = "hard"
                        FPS = DIFFICULTY[current_difficulty]["fps"]
    
    def update_game(self):
        if not self.game_over and not self.paused:
            # Обновление змейки
            if not self.snake.update(self.obstacles):
                self.game_over = True
                self.save_highscore()
            
            # Проверка на съедение еды
            if self.snake.get_head_position() == self.food.position:
                effect = self.food.current["effect"]
                if effect == "grow":
                    self.snake.grow()
                elif effect == "speed_up":
                    self.snake.change_speed(1.5)
                    self.snake.grow()
                elif effect == "slow_down":
                    self.snake.change_speed(0.7)
                    self.snake.grow()
                elif effect == "reverse":
                    self.snake.reverse()
                    self.snake.grow()
                
                self.food.randomize_position()
                # Убедимся, что еда не появилась в змейке или препятствиях
                while (self.food.position in self.snake.positions or 
                       self.food.position in self.obstacles):
                    self.food.randomize_position()
            
            # Проверка на бонус
            if (self.bonus.active and 
                self.snake.get_head_position() == self.bonus.position and
                pygame.time.get_ticks() - self.bonus.spawn_time < self.bonus.duration):
                self.snake.activate_bonus(self.bonus)
                self.bonus.active = False
            
            # Случайное появление бонуса
            if not self.bonus.active and random.random() < 0.001:  # 0.1% шанс каждый кадр
                self.bonus.randomize_position(self.snake.positions, self.obstacles)
    
    def draw_game(self):
        # Фон
        self.update_background()
        screen.fill(tuple(self.bg_color))
        
        # Сетка
        self.draw_grid()
        
        # Препятствия
        self.draw_obstacles()
        
        # Еда
        self.food.draw()
        
        # Бонус
        self.bonus.draw()
        
        # Змейка
        self.snake.draw()
        
        # HUD
        self.draw_hud()
        
        pygame.display.update()
    
    def run(self):
        while self.running:
            self.handle_events()
            
            if not self.game_over:
                self.update_game()
                self.draw_game()
            elif self.game_over:
                self.show_game_over()
            elif self.paused:
                self.show_pause()
            
            clock.tick(FPS * self.snake.speed_multiplier)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
