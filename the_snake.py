from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
HUD_HEIGHT = 40
PLAY_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Расчет стартовой позиции:
START_X = (GRID_WIDTH // 2) * GRID_SIZE
START_Y = (GRID_HEIGHT // 2) * GRID_SIZE
DEFAULT_POS = (START_X, START_Y)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь разрешенных поворотов (Защита от разворота на 180 градусов).
ROTATION_MAP = {
    (pygame.K_UP, LEFT): UP,
    (pygame.K_UP, RIGHT): UP,
    (pygame.K_UP, UP): UP,
    (pygame.K_DOWN, LEFT): DOWN,
    (pygame.K_DOWN, RIGHT): DOWN,
    (pygame.K_DOWN, DOWN): DOWN,
    (pygame.K_LEFT, UP): LEFT,
    (pygame.K_LEFT, DOWN): LEFT,
    (pygame.K_LEFT, LEFT): LEFT,
    (pygame.K_RIGHT, UP): RIGHT,
    (pygame.K_RIGHT, DOWN): RIGHT,
    (pygame.K_RIGHT, RIGHT): RIGHT,
}

# Цвета:
BOARD_BACKGROUND_COLOR = (30, 30, 30)
BORDER_COLOR = (20, 20, 20)
WHITE = (255, 255, 255)
RED = (200, 40, 40)
PURPLE = (150, 40, 150)
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

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()

# Инициализация шрифтов:
pygame.font.init()
FONT_HUD = pygame.font.SysFont('Arial', 18)
FONT_HUD_BOLD = pygame.font.SysFont('Arial', 18, bold=True)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=(0, 0), body_color=WHITE):
        """Инициализирует позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовка объекта."""
        raise NotImplementedError

    def draw_cell(self, position, color):
        """Вспомогательный метод для отрисовки одной ячейки сетки."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, occupied_positions):
        """Перемещает объект в случайную свободную ячейку поля ниже HUD."""
        occupied_set = set(occupied_positions)
        while True:
            random_x = choice(range(GRID_WIDTH)) * GRID_SIZE
            random_y = HUD_HEIGHT + choice(range(GRID_HEIGHT)) * GRID_SIZE
            new_position = (random_x, random_y)
            if new_position not in occupied_set:
                self.position = new_position
                break


class Snake(GameObject):
    """Поведение, отрисовка змейки."""

    def __init__(self, position=None, body_color=GREEN):
        """Инициализирует змейку."""
        super().__init__(position, body_color)
        self.last = None
        self.reset()
        self.direction = RIGHT

    def get_head_position(self):
        """Возвращает координаты текущего положения головы."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки."""
        self.direction = new_direction

    def move(self, new_direction=None):
        """Перемещает змейку вперед на одну ячейку с учетом границ HUD."""
        if new_direction:
            self.update_direction(new_direction)

        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        relative_y = head_y - HUD_HEIGHT
        new_head_y = HUD_HEIGHT + (relative_y + dy * GRID_SIZE) % PLAY_HEIGHT
        new_head = (new_head_x, new_head_y)
        self.positions.insert(0, new_head)
        self.last = self.positions.pop()

    def grow(self):
        """Увеличивает длину змейки."""
        self.positions.append(self.positions[-1])
        self.last = None

    def shrink(self):
        """Уменьшение длины и возврат позиции удаленного хвоста."""
        if len(self.positions) > 1:
            return self.positions.pop()
        return None

    def draw(self):
        """Отрисовывает все сегменты змейки."""
        for position in self.positions[1:-1]:
            self._draw_circle(position, self.body_color, GRID_SIZE // 2 - 1)

        if len(self.positions) > 1:
            tail = self.positions[-1]
            self._draw_circle(tail, DARK_GREEN, GRID_SIZE // 2 - 3)

        head = self.get_head_position()
        self._draw_circle(head, LIGHT_GREEN, GRID_SIZE // 2)

    def _draw_circle(self, position, color, radius):
        """Вспомогательный метод для рисования круглого сегмента."""
        cx, cy = position
        cx += GRID_SIZE // 2
        cy += GRID_SIZE // 2

        pygame.draw.circle(screen, color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)

    def check_self_collision(self):
        """Проверяет собственную коллизию головы с хвостом."""
        head = self.get_head_position()
        return head in self.positions[1:]

    def reset(self):
        """Сброс змейки в стартовое состояние в центре игрового поля."""
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = HUD_HEIGHT + (GRID_HEIGHT // 2) * GRID_SIZE
        self.positions = [(start_x, start_y)]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])


class Apple(GameObject):
    """Класс, описывающий полезную еду."""

    def draw(self):
        """Отрисовывает яблоко."""
        x, y = self.position
        cx = x + GRID_SIZE // 2
        cy = y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 1
        pygame.draw.circle(screen, self.body_color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)


class BadFood(GameObject):
    """Класс, описывающий плохую еду."""

    def draw(self):
        """Отрисовывает плохую еду."""
        x, y = self.position
        cx = x + GRID_SIZE // 2
        cy = y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2
        pygame.draw.circle(screen, self.body_color, (cx, cy), radius)
        pygame.draw.circle(screen, BORDER_COLOR, (cx, cy), radius, 1)


def handle_keys(current_direction):
    """Обрабатывает ввод пользователя и возвращает выбранное направление."""
    new_direction = current_direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            new_direction = ROTATION_MAP.get(
                (event.key, new_direction), new_direction
            )
    return new_direction


def draw_grid():
    """Рисует сетку игрового поля."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, HUD_HEIGHT), (x, SCREEN_HEIGHT), 1)
    for y in range(HUD_HEIGHT, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)


def clear_cell(position):
    """Затирает одну ячейку цветом фона и восстанавливает сетку вокруг неё."""
    if position is None:
        return
    x, y = position
    rect = pygame.Rect(x - 1, y - 1, GRID_SIZE + 2, GRID_SIZE + 2)
    pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
    orig_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, GRAY, orig_rect, 1)


def format_time(seconds):
    """Преобразует секунды в строку MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f'{minutes:02d}:{secs:02d}'


def draw_hud(score, elapsed_seconds, best_score):
    """Отрисовка интерфейса (HUD)."""
    hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT)
    pygame.draw.rect(screen, (20, 20, 20), hud_rect)
    pygame.draw.line(
        screen, WHITE, (0, HUD_HEIGHT), (SCREEN_WIDTH, HUD_HEIGHT), 2
    )
    current_time_formatted = format_time(elapsed_seconds)
    score_text = FONT_HUD_BOLD.render(f'Счёт: {score}', True, WHITE)
    time_text = FONT_HUD_BOLD.render(
        f'Время: {current_time_formatted}', True, WHITE
    )
    screen.blit(
        score_text, (20, (HUD_HEIGHT - score_text.get_height()) // 2)
    )
    screen.blit(
        time_text, (
            SCREEN_WIDTH - time_text.get_width() - 20,
            (HUD_HEIGHT - time_text.get_height()) // 2,
        ),
    )
    if best_score > 0:
        record_text = FONT_HUD.render(f'Рекорд: {best_score}', True, GOLD)
        screen.blit(
            record_text, (
                (SCREEN_WIDTH - record_text.get_width()) // 2,
                (HUD_HEIGHT - record_text.get_height()) // 2,
            ),
        )


def reset_game_screen(snake, apple, bad_food):
    """Полная очистка и подготовка экрана при старте или проигрыше."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_grid()
    apple.randomize_position(snake.positions)
    bad_food.randomize_position(snake.positions + [apple.position])


def main():
    """Главный цикл игры."""
    snake = Snake()
    apple = Apple(body_color=RED)
    bad_food = BadFood(body_color=PURPLE)

    reset_game_screen(snake, apple, bad_food)

    score = 0
    best_score = 0
    start_ticks = pygame.time.get_ticks()

    next_direction = snake.direction

    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_grid()

    while True:
        current_speed = min(START_SPEED + (score // 30), MAX_SPEED)
        clock.tick(current_speed)

        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000

        next_direction = handle_keys(next_direction)
        snake.move(next_direction)

        head_position = snake.get_head_position()

        if snake.check_self_collision():

            if score > best_score:

                best_score = score
            score = 0
            snake.reset()
            next_direction = snake.direction
            start_ticks = pygame.time.get_ticks()
            reset_game_screen(snake, apple, bad_food)
            continue

        if head_position == apple.position:
            clear_cell(apple.position)
            clear_cell(bad_food.position)

            if snake.last:
                clear_cell(snake.last)
            snake.grow()
            score += APPLE_POINTS
            apple.randomize_position(snake.positions)
            bad_food.randomize_position(snake.positions + [apple.position])

        elif head_position == bad_food.position:
            clear_cell(bad_food.position)

            if snake.last:
                clear_cell(snake.last)

            removed_tail = snake.shrink()
            if removed_tail:
                clear_cell(removed_tail)

            score = max(0, score - (APPLE_POINTS // 2))

            bad_food.randomize_position(snake.positions + [apple.position])

        else:
            if snake.last:
                clear_cell(snake.last)

        apple.draw()
        bad_food.draw()
        snake.draw()
        draw_hud(score, elapsed_seconds, best_score)
        pygame.display.update()


if __name__ == '__main__':
    main()
