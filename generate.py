import random
import numpy as np
from PIL import Image

def load_binary_maze(file_path):
    """
    Load a binary maze from a text file into a NumPy array.

    Args:
        file_path (str): Path to the text file containing the binary maze.

    Returns:
        np.ndarray: 2D binary array representing the maze.
    """
    # Load the text file into a NumPy array
    binary_maze = np.loadtxt(file_path, dtype=int).reshape((25, 25))
    return binary_maze


def generate_solvable_binary_maze(size):
    # Initialize grid with walls (0s)
    maze = np.zeros((size, size), dtype=np.uint8)

    # Start and end points
    start = (0, 0)
    end = (size - 1, size - 1)

    # Create a stack for iterative DFS
    stack = [start]
    maze[start] = 1  # Mark the starting point as path (1)

    # Directions: Right, Down, Left, Up
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)  # Randomize direction order
        carved = False

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # Check bounds and ensure the cell is not already visited
            if 0 <= nx < size and 0 <= ny < size and maze[nx, ny] == 0:
                # Ensure we're not creating isolated walls
                if np.sum(maze[max(nx - 1, 0):nx + 2, max(ny - 1, 0):ny + 2]) <= 2:
                    maze[nx, ny] = 1  # Mark as path
                    stack.append((nx, ny))
                    carved = True
                    break

        if not carved:
            stack.pop()  # Backtrack

    # Ensure start and end are connected
    maze[start] = 1
    maze[end] = 1

    return maze


def binary_maze_to_image(binary_maze, path_color, wall_color, output_path):
    """
    Convert a binary maze (1s and 0s) into a PNG image with specified colors.

    Args:
        binary_maze (np.ndarray): 2D array where 1 represents paths and 0 represents walls.
        path_color (tuple): RGBA color for paths (1s).
        wall_color (tuple): RGBA color for walls (0s).
        output_path (str): Path to save the resulting PNG file.

    Returns:
        None
    """
    # Get the dimensions of the maze
    height, width = binary_maze.shape

    # Initialize an RGBA image array
    image = np.zeros((height, width, 4), dtype=np.uint8)

    # Assign the colors to paths and walls
    image[binary_maze == 1] = path_color  # Assign gray to paths (1s)
    image[binary_maze == 0] = wall_color  # Assign black to walls (0s)

    # Convert to PIL Image
    img = Image.fromarray(image)

    # Save the image
    img.save(output_path)
    print(f"Maze saved as PNG at: {output_path}")

# Generate a 500x500 solvable binary maze
maze_size = 50
# binary_maze = generate_solvable_binary_maze(maze_size)
# binary_maze = load_binary_maze('maze_hard_v2.txt')
binary_maze = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1],
    [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0],
    [1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0],
    [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1],
    [1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1],
    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1]
])
print(binary_maze.shape)

# Define colors
gray_color = (70, 70, 70, 255)  # RGBA for paths (1s)
black_color = (0, 0, 0, 255)    # RGBA for walls (0s)

# Output file path
output_file_path = "maze_image.png"

# Convert the binary maze to an image and save it
binary_maze_to_image(binary_maze, gray_color, black_color, output_file_path)

