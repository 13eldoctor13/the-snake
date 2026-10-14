from random import choice
from typing import Optional

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (30, 30, 30)
BORDER_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (200, 40, 40)
PURPLE = (150, 40, 150)
LIGHT_RED = (255, 90, 90)
YELLOW = (255, 220, 0)
GREEN = (60, 200, 60)
DARK_GREEN = (40, 140, 40)
LIGHT_GREEN = (120, 240, 120)
GRAY = (60, 60, 60)
GOLD = (255, 200, 60)

# Скорость движения змейки:
START_SPEED = 5
MAX_SPEED = 25

# Очки за одно яблоко:
APPLE_POINTS = 10

# Время жизни яблока в миллисекундах (10 секунд):
FOOD_LIFETIME = 10000

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pygame.time.Clock()

# Глобальные переменные:
FONT_HUD: Optional[pygame.font.Font] = None
FONT_HUD_BOLD: Optional[pygame.font.Font] = None


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=(0, 0), body_color=WHITE):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовка объекта"""
        raise NotImplementedError

    def update_direction(self):
        """Обновление направления"""
        pass


class Snake(GameObject):
    """Поведение, отрисовка змейки"""

    def __init__(self, position, body_color=GREEN):
        """
        Инициализирует змейку в центре поля
        с начальной длиной в 3 сегмента
        """
        super().__init__(position, body_color)
        x, y = position
        self.positions = [(x, y), (x - GRID_SIZE, y), (x - 2 * GRID_SIZE, y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет текущее направление движения на следующее"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на один шаг вперед"""
        self.update_direction()
        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = (head_x + dx * GRID_SIZE, head_y + dy * GRID_SIZE)
        # Телепорт через границы
        new_head = (new_head[0] % SCREEN_WIDTH, new_head[1] % SCREEN_HEIGHT)
        self.positions.insert(0, new_head)
        self.positions.pop()

    def grow(self):
        """Увеличивает длину змейки"""
        self.positions.append(self.positions[-1])

    def shrink(self):
        """Уменьшение длины (не меньше 3 сегментов)"""
        if len(self.positions) > 3:
            self.positions.pop()

    def draw(self):
        """Отрисовывает все сегменты змейки"""
        # Тело — круги
        for position in self.positions[1:-1]:
            self._draw_circle(position, self.body_color, GRID_SIZE // 2 - 1)

        # Хвост — чуть меньше
        if len(self.positions) > 1:
            tail = self.positions[-1]
            self._draw_circle(tail, DARK_GREEN, GRID_SIZE // 2 - 3)

        # Голова — крупнее и светлее
        head = self.positions[0]
        self._draw_circle(head, LIGHT_GREEN, GRID_SIZE // 2)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def _draw_circle(self, position, color, radius):
        """Вспомогательный метод для рисования сегмента"""
        cx = position[0] + GRID_SIZE // 2
        cy = position[1] + GRID_SIZE // 2
        pygame.draw.circle(screen, color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)

    def check_self_collision(self):
        """Проверяет собственную коллизию"""
        head = self.positions[0]
        return head in self.positions[1:]

    def reset(self):
        """Сброс змейки в стартовое состояние."""
        x = (GRID_WIDTH // 2) * GRID_SIZE
        y = (GRID_HEIGHT // 2) * GRID_SIZE
        self.positions = [(x, y), (x - GRID_SIZE, y), (x - 2 * GRID_SIZE, y)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


class Apple(GameObject):
    """Класс, описывающий полезную еду"""

    def __init__(self, position=(0, 0), body_color=RED):
        super().__init__(position, body_color)

    def draw(self):
        """Отрисовывает яблоко"""
        cx = self.position[0] + GRID_SIZE // 2
        cy = self.position[1] + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 1
        pygame.draw.circle(screen, self.body_color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)

    def randomize_position(self, occupied):
        """Перемещает еду в рандомную клетку"""
        occupied_set = set(occupied)
        free_cells = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_set
        ]
        if free_cells:
            self.position = choice(free_cells)


class BadFood(GameObject):
    """Класс, описывающий плохую еду"""

    def __init__(self, position=(0, 0), body_color=PURPLE):
        super().__init__(position, body_color)

    def draw(self):
        """Отрисовывает плохую еду"""
        cx = self.position[0] + GRID_SIZE // 2
        cy = self.position[1] + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2
        pygame.draw.circle(screen, self.body_color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)

    def randomize_position(self, occupied):
        """Перемещает еду в рандомную клетку"""
        occupied_set = set(occupied)
        free_cells = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_set
        ]
        if free_cells:
            self.position = choice(free_cells)


def handle_keys(game_object):
    """Обрабатывает ввод пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            curr = game_object.next_direction or game_object.direction

            if event.key == pygame.K_UP and curr != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and curr != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and curr != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and curr != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


def draw_grid():
    """Рисует сетку игрового поля"""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)


def format_time(seconds):
    """Преобразует секунды в строку MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f'{minutes:02d}:{secs:02d}'


def draw_hud(score, elapsed_seconds, best_score, best_time):
    """Отрисовка интерфейса (HUD)."""
    current_time_formatted = format_time(elapsed_seconds)
    best_time_formatted = format_time(best_time)

    score_text = FONT_HUD_BOLD.render(f'Счёт: {score}', True, WHITE)
    time_str = f'Время: {current_time_formatted}'
    time_text = FONT_HUD_BOLD.render(time_str, True, WHITE)
    screen.blit(score_text, (10, 8))
    screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 10, 8))

    if best_score > 0:
        record_str = f'Рекорд: {best_score} ({best_time_formatted})'
        record_text = FONT_HUD.render(record_str, True, GOLD)
    else:
        record_text = FONT_HUD.render('Рекорд: —', True, GOLD)
    screen.blit(
        record_text,
        (SCREEN_WIDTH // 2 - record_text.get_width() // 2, 8)
    )


def main():
    """Основная функция: запускает игровой цикл"""
    global FONT_HUD, FONT_HUD_BOLD
    pygame.display.set_caption('Змейка')

    FONT_HUD = pygame.font.SysFont('arial', 18)
    FONT_HUD_BOLD = pygame.font.SysFont('arial', 20, bold=True)

    start_x = (GRID_WIDTH // 2) * GRID_SIZE
    start_y = (GRID_HEIGHT // 2) * GRID_SIZE

    snake = Snake((start_x, start_y))
    apple = Apple()
    apple.randomize_position(snake.positions)

    bad_food = BadFood()
    bad_food.randomize_position(snake.positions + [apple.position])

    score = 0
    start_ticks = pygame.time.get_ticks()
    apple_start_ticks = pygame.time.get_ticks()
    bad_food_start_ticks = pygame.time.get_ticks()

    elapsed_seconds = 0
    best_score = 0
    best_time = 0
    current_speed = START_SPEED

    while True:
        clock.tick(current_speed)
        handle_keys(snake)

        current_ticks = pygame.time.get_ticks()
        elapsed_seconds = (current_ticks - start_ticks) // 1000

        if current_ticks - apple_start_ticks >= FOOD_LIFETIME:
            apple.randomize_position(snake.positions + [bad_food.position])
            apple_start_ticks = current_ticks

        if current_ticks - bad_food_start_ticks >= FOOD_LIFETIME:
            bad_food.randomize_position(snake.positions + [apple.position])
            bad_food_start_ticks = current_ticks

        snake.move()

        if snake.check_self_collision():
            if score > best_score:
                best_score = score
                best_time = elapsed_seconds
            snake.reset()
            apple.randomize_position(snake.positions)
            bad_food.randomize_position(snake.positions + [apple.position])
            score = 0
            current_speed = START_SPEED
            start_ticks = pygame.time.get_ticks()
            apple_start_ticks = pygame.time.get_ticks()
            bad_food_start_ticks = pygame.time.get_ticks()
            elapsed_seconds = 0
            continue

        if snake.get_head_position() == apple.position:
            snake.grow()
            score += APPLE_POINTS
            apple.randomize_position(snake.positions + [bad_food.position])
            apple_start_ticks = current_ticks
            current_speed = min(START_SPEED + (score // 20), MAX_SPEED)

        elif snake.get_head_position() == bad_food.position:
            score = max(0, score - APPLE_POINTS)
            snake.shrink()
            bad_food.randomize_position(snake.positions + [apple.position])
            bad_food_start_ticks = current_ticks
            current_speed = min(START_SPEED + (score // 20), MAX_SPEED)

        screen.fill(BOARD_BACKGROUND_COLOR)
        draw_grid()
        apple.draw()
        bad_food.draw()
        snake.draw()
        draw_hud(score, elapsed_seconds, best_score, best_time)
        pygame.display.update()


if __name__ == '__main__':
    main()
