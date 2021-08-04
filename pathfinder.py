import pygame
import math
from queue import PriorityQueue
pygame.font.init()

#################
# GAME SETTINGS #
#################

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Path Finding Algorithm")
FPS = 80
DISTANCE_FONT = pygame.font.Font(pygame.font.get_default_font(), 30)

###########
# COLOURS #
###########

WHITE = (255, 255, 255)  # Initial blocks
BLUE = (0, 0, 255)  # Closed blocks
TURQUOISE = (65, 225, 208)  # Open blocks
BLACK = (0, 0, 0)  # Barrier blocks
PURPLE = (188, 19, 254)  # Path blocks
GREEN = (0,190,0)  # Start blocks
RED = (255, 0, 0)  # End blocks
GREY = (128, 128, 128)  # Grid lines

##################
# IMPLEMENTATION #
##################


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.neighbours = []
        self.total_rows = total_rows
        self.colour = WHITE

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.colour == BLUE

    def is_open(self):
        return self.colour == TURQUOISE

    def is_barrier(self):
        return self.colour == BLACK

    def is_start(self):
        return self.colour == GREEN

    def is_end(self):
        return self.colour == RED

    def reset(self):
        self.colour = WHITE

    def make_closed(self):
        self.colour = BLUE

    def make_open(self):
        self.colour = TURQUOISE

    def make_barrier(self):
        self.colour = BLACK

    def make_start(self):
        self.colour = GREEN

    def make_end(self):
        self.colour = RED

    def make_path(self):
        self.colour = PURPLE

    def draw(self, window):
        pygame.draw.rect(window, self.colour, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        # Check right neighbour
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col + 1])
        # Check left neighbour
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col - 1])
        # Check up neighbour
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])
        # Check down neighbour
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])

    def __lt__(self, other):
        return False


def construct_path(node_from, current_node, draw_window):
    while current_node in node_from:
        current_node = node_from[current_node]
        current_node.make_path()
        draw_window()


def h(current, goal):
    cx, cy = current
    gx, gy = goal
    return abs(cx - gx) + abs(cy - gy)


def algorithm(draw_window, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    node_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current_node = open_set.get()[2]
        open_set_hash.remove(current_node)

        if current_node == end:
            construct_path(node_from, end, draw_window)
            end.make_end()
            start.make_start()
            return True

        for neighbour in current_node.neighbours:
            temp_g_score = g_score[current_node] + 1
            if g_score[neighbour] > temp_g_score:
                node_from[neighbour] = current_node
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()

        draw_window()

        if current_node != start:
            current_node.make_closed()
    return False


def make_grid(rows, width):
    grid = []
    space = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, space, rows)
            grid[i].append(node)
    return grid


def draw_grid(window, rows, width):
    space = width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * space), (width, i * space))
    for j in range(rows):
        pygame.draw.line(window, GREY, (j * space, 0), (j * space, width))


def draw_window(window, grid, rows, width):
    window.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(window)
    draw_grid(window, rows, width)
    pygame.display.update()


def get_mouse_pos(pos, rows, width):
    space = width // rows
    y, x = pos
    row = y // space
    col = x // space
    return row, col


def main(window, width):
    # clock = pygame.tick.Clock()
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    while run:
        draw_window(window, grid, ROWS, width)
        # clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    node.make_end()
                elif node != start and node != end:
                    node.make_barrier()
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)

                    algorithm(lambda: draw_window(window, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_SPACE:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


if __name__ == "__main__":
    main(WIN, WIDTH)
