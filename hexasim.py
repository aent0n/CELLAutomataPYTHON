import pygame
import numpy as np
import math
import random

# Game parameters
grid_size = (300, 200)
cell_size = 4
num_generations = 10000
gui_width = 200
last_clicked_cell = None
first_clicked_cell = None
furthest_clicked_cell = None
thumbnail_cell_size = cell_size * 3


# Initialize the grid
grid = np.zeros(grid_size)
initial_grid = np.copy(grid)  # Store the initial state of the grid


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((grid_size[0]*cell_size+gui_width, grid_size[1]*cell_size))
font = pygame.font.Font(None, 36)
thumbnail_size = 50  # Size of the thumbnail in pixels



def draw_hexagon(surface, x, y, cell_size, color):
    hex_points = [(x + cell_size * math.cos(angle), y + cell_size * math.sin(angle)) for angle in [2 * math.pi / 6 * i for i in range(6)]]
    pygame.draw.polygon(surface, color, hex_points)
    border_color = (255, 255, 255) if color == (0, 0, 0) else (128, 128, 128)  # Set border color to white for black cells and gray for white cells
    pygame.draw.polygon(surface, border_color, hex_points, 1)  # Draw border
    return hex_points

def draw_grid():
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            x = j * cell_size * 1.5
            y = i * cell_size * math.sqrt(3) + (j % 2) * cell_size * math.sqrt(3) / 2  # Offset every other row
            color = (0, 0, 0) if grid[i, j] == 1 else (255, 255, 255)
            draw_hexagon(screen, x, y, cell_size, color)

def hexagonal_neighbors(grid, i, j):
    neighbors = []
    rows, cols = grid.shape
    neighbors.append(grid[(i - 1) % rows][j])
    neighbors.append(grid[(i + 1) % rows][j])
    neighbors.append(grid[i][(j - 1) % cols])
    neighbors.append(grid[i][(j + 1) % cols])
    neighbors.append(grid[(i - 1) % rows][(j + 1) % cols])
    neighbors.append(grid[(i + 1) % rows][(j - 1) % cols])
    return neighbors

def step(grid):
    new_grid = np.zeros_like(grid)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            total = sum(hexagonal_neighbors(grid, i, j))
            if grid[i, j] == 1:
                if total < 2 or total > 3:
                    new_grid[i, j] = 0
                else:
                    new_grid[i, j] = 1
            elif total == 2:  # Change this line
                new_grid[i, j] = 1
    return new_grid

def draw_gui(gen_count, initial_grid):
    # Clear the GUI area
    pygame.draw.rect(screen, (255, 255, 255), (grid_size[0]*cell_size, 0, gui_width, grid_size[1]*cell_size))

    # Draw the generation counter with smaller font
    small_font = pygame.font.Font(None, 24)  # Adjust the font size as needed
    gen_text = small_font.render(f"Generation: {gen_count}", True, (0, 0, 0))
    screen.blit(gen_text, (grid_size[0]*cell_size + 10, 10))

    # Draw the "Start Pattern" text
    pattern_text = font.render("Start Pattern", True, (0, 0, 0))
    screen.blit(pattern_text, (grid_size[0]*cell_size + 10, 40))  # Adjust the position as needed

    # Create a subgrid around the first clicked cell if it exists
    if first_clicked_cell is not None:
        i, j = first_clicked_cell
        furthest_i, furthest_j = furthest_clicked_cell
        radius = max(abs(furthest_i - i), abs(furthest_j - j)) + 1  # Calculate the radius of the subgrid
        subgrid = initial_grid[max(0, i-radius):min(grid_size[0], i+radius+1), max(0, j-radius):min(grid_size[1], j+radius+1)]  # Extract the subgrid

        # Invert the coloration
        subgrid = 1 - subgrid

        # Convert the subgrid to a 3D array with the same value for all color channels
        subgrid_rgb = np.stack([subgrid]*3, axis=-1)

        # Create a new surface for the thumbnail
        thumbnail_surface = pygame.Surface((subgrid.shape[1]*thumbnail_cell_size, subgrid.shape[0]*thumbnail_cell_size))

        # Draw the hexagonal grid on the thumbnail surface
        for i in range(subgrid.shape[0]):
            for j in range(subgrid.shape[1]):
                x = j * cell_size * 1.5
                y = i * cell_size * math.sqrt(3) + (j % 2) * cell_size * math.sqrt(3) / 2  # Offset every other row
                color = (0, 0, 0) if subgrid[i, j] == 1 else (255, 255, 255)
                draw_hexagon(thumbnail_surface, x, y, cell_size, color)

        # Scale the thumbnail surface to the desired size
        thumbnail = pygame.transform.scale(thumbnail_surface, (thumbnail_size, thumbnail_size))

        # Draw the thumbnail
        screen.blit(thumbnail, (grid_size[0]*cell_size + 10, 70))  # Adjust the position as needed

    # Draw more live insights
    live_cells = np.sum(initial_grid)
    live_text = font.render(f"Live cells: {live_cells}", True, (0, 0, 0))
    screen.blit(live_text, (grid_size[0]*cell_size + 10, 100))  # Adjust the position as needed

# Game loop
running = True
simulation = False
gen_count = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            j = int(x / (cell_size * 1.5))
            i = int((y - (j % 2) * cell_size * math.sqrt(3) / 2) / (cell_size * math.sqrt(3)))
            grid[i, j] = 1 if grid[i, j] == 0 else 0
            initial_grid = np.copy(grid)  # Update the initial state when the user modifies the grid
            if first_clicked_cell is None:
                first_clicked_cell = (i, j)  # Set the first clicked cell
            furthest_clicked_cell = (i, j)  # Update the furthest clicked cell
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                simulation = True

    screen.fill((255, 255, 255))  # Set background to white
    draw_grid()
    draw_gui(gen_count, initial_grid)
    pygame.display.update()

    if simulation:
        grid = step(grid)
        gen_count += 1
        pygame.time.wait(100)

pygame.quit()