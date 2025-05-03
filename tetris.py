import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Grid dimensions (10x20)
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Colors (R, G, B)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),    # Cyan - I
    (0, 0, 255),      # Blue - J
    (255, 165, 0),    # Orange - L
    (255, 255, 0),    # Yellow - O
    (0, 255, 0),      # Green - S
    (128, 0, 128),    # Purple - T
    (255, 0, 0)       # Red - Z
]

# Define the shapes of the single parts
SHAPES = [
    # I shape
    [[1, 1, 1, 1]],
    # J shape
    [[1, 0, 0],
     [1, 1, 1]],
    # L shape
    [[0, 0, 1],
     [1, 1, 1]],
    # O shape
    [[1, 1],
     [1, 1]],
    # S shape
    [[0, 1, 1],
     [1, 1, 0]],
    # T shape
    [[0, 1, 0],
     [1, 1, 1]],
    # Z shape
    [[1, 1, 0],
     [0, 1, 1]]
]

class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.rotation = 0  # index of rotation state

    def image(self):
        # Return the current rotation of the shape
        return self.rotate_shape(self.shape, self.rotation)

    @staticmethod
    def rotate_shape(shape, rotation):
        # Rotate the shape clockwise rotation times
        rotated = shape
        for _ in range(rotation % 4):
            rotated = [list(row) for row in zip(*rotated[::-1])]
        return rotated

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid

def convert_shape_format(piece):
    positions = []
    shape = piece.image()

    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(GRID_WIDTH) if grid[i][j] == BLACK] for i in range(GRID_HEIGHT)]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Piece(GRID_WIDTH // 2 - 2, 0, random.randint(0, len(SHAPES) - 1))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, SCREEN_HEIGHT / 2 - label.get_height() / 2))

def draw_grid(surface, grid):
    for i in range(GRID_HEIGHT):
        pygame.draw.line(surface, GRAY, (0, i * BLOCK_SIZE), (SCREEN_WIDTH, i * BLOCK_SIZE))
        for j in range(GRID_WIDTH):
            pygame.draw.line(surface, GRAY, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, SCREEN_HEIGHT))

def clear_rows(grid, locked):
    # Need to see if row is clear then shift every other row above down one
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            # Add positions to remove from locked
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        # Shift every row above down
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < i:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_window(surface, grid, score=0):
    surface.fill(BLACK)

    # Draw score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, WHITE)
    surface.blit(label, (10, 10))

    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    draw_grid(surface, grid)
    pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    while run:
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase difficulty over time
        if level_time / 1000 > 30:
            level_time = 0
            if fall_speed > 0.1:
                fall_speed -= 0.05

        # Piece falls every fall_speed seconds
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % 4
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % 4
                elif event.key == pygame.K_SPACE:
                    # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # If piece hit the ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Clear rows and update score
            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                score += cleared * 10

        draw_window(screen, grid, score)
        pygame.display.update()

        # Check if user lost
        if check_lost(locked_positions):
            draw_text_middle(screen, "YOU LOST!", 80, (255, 0, 0))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

    pygame.quit()

if __name__ == "__main__":
    main()
