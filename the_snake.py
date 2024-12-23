import random

import pygame as pg


# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Все игровые клетки поля
ALL_BOARD_POSITIONS = {(width, height) for width in
                       range(0, SCREEN_WIDTH, GRID_SIZE)
                       for height in range(0, SCREEN_HEIGHT, GRID_SIZE)}

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """GameObject — это базовый класс, от которого наследуются другие игровые
    объекты.
    """

    def __init__(self):
        """Конструктор класса GameObject."""
        self.position = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.body_color = None

    @staticmethod
    def draw_rect(position, body_color):
        """Рисует прямоугольный объект."""
        rect = pg.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    @staticmethod
    def clean_rect(position):
        """Затирание прямоугольного объекта."""
        rect = pg.Rect(
            (position[0], position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def draw(self):
        """Это абстрактный метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект будет
        отрисовываться на экране. По умолчанию — pass.
        """
        raise NotImplementedError(
            f'Определите draw в {self.__class__.__name__}.'
        )


class Apple(GameObject):
    """Класс унаследованный от GameObject, описывающий яблоко
    и действия с ним.
    """

    def __init__(self, busy_positions=None):
        """Конструктор класса Apple."""
        super().__init__()
        self.busy_positions = busy_positions
        self.position = self.randomize_position(self.busy_positions)
        self.body_color = APPLE_COLOR

    @staticmethod
    def randomize_position(busy_positions):
        """Устанавливает случайное положение яблока на игровом поле."""
        all_positions = ALL_BOARD_POSITIONS
        if busy_positions is None:
            busy_positions = []
        all_positions -= set(busy_positions)
        return random.choice(tuple(all_positions))

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_rect(self.position, self.body_color)


class Snake(GameObject):
    """Класс унаследованный от GameObject, описывающий змейку
    и действия с ней.
    """

    def __init__(self):
        super().__init__()
        self.reset()
        self.last = None
        self.direction = RIGHT
        self.next_direction = None
        self.length = 1
        self.body_color = SNAKE_COLOR

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки."""
        if next_direction:
            self.direction = next_direction

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и
        удаляя последний элемент, если длина змейки не увеличилась.
        """
        head_position = self.get_head_position()
        direction_x, direction_y = self.direction
        self.positions.insert(0, (
            (head_position[0] + (direction_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_position[1] + (direction_y * GRID_SIZE)) % SCREEN_HEIGHT,
        ))
        self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        # Отрисовка головы змейки
        self.draw_rect(self.get_head_position(), self.body_color)

        # Затирание последнего сегмента
        if self.last:
            self.clean_rect((self.last[0], self.last[1]))

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения
        с собой.
        """
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def snake_position(self):
        """Возвращает координаты змеи без учёта головы."""
        return self.positions[1:]


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш, чтобы изменить направление
    движения змейки
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной цикл программы."""
    snake = Snake()
    apple = Apple(snake.positions)
    while True:
        clock.tick(SPEED)
        pg.display.update()
        handle_keys(snake)
        snake.update_direction(snake.next_direction)
        apple.draw()
        snake.draw()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.positions.append(snake.last)
            apple = Apple(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        elif snake.get_head_position() in snake.snake_position():
            snake.reset()


if __name__ == '__main__':
    main()
