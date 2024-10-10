## **Pathfinding Visualizer**

**A Python application for visualizing pathfinding algorithms**

This project implements a pathfinding visualizer in Python using the Pygame library. It allows users to interactively explore various pathfinding algorithms on a grid-based environment.

**Features:**

* Visualizes popular pathfinding algorithms including Dijkstra's, A*, Breadth-First Search (BFS), and Depth-First Search (DFS).
* Allows users to create custom start and target nodes for pathfinding.
* Provides options for generating maze layouts.
* Offers real-time visualization of the search process, highlighting explored nodes and the final path.
* Customizable grid size and visualization options.

**Technologies:**

* Python 3
* Pygame

**Getting Started:**

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/pathfinding-visualizer.git
   ```

2. **Install dependencies:**

   ```bash
   pip install pygame
   ```

3. **Run the application:**

   ```bash
   python main.py
   ```

**User Interface:**

The visualizer features a user-friendly interface with the following elements:

* **Grid:** Represents the search space where the pathfinding algorithm operates.
* **Nodes:** Individual cells within the grid. Users can set the start and target nodes for pathfinding.
* **Algorithms:** A menu allows users to select different pathfinding algorithms.
* **Speed:** Option to adjust the visualization speed for algorithms.
* **Maze Generation:** Button to generate a random maze layout on the grid.
* **Clear:** Button to reset the grid and visualization.

**Visual Representation:**

* **Start Node:** Highlighted in green.
* **Target Node:** Highlighted in red.
* **Wall:** Represented by a dark grey color.
* **Blank Node:** Represented by white.
* **Visited Node:** Indicated by a light blue color during the search process.
* **Path:** The final path found by the selected algorithm is displayed in yellow.

**Project Structure:**

The project code is organized into well-defined modules for maintainability:

* `cell.py`: Defines the `Cell` class representing individual grid nodes.
* `grid.py`: Handles grid creation, node initialization, and neighbor relationships.
* `algorithms.py`: Implements the core pathfinding algorithms (Dijkstra's, A*, BFS, DFS).
* `maze.py`: Generates random maze layouts on the grid.
* `button.py`: Defines interactive buttons for user interaction.
* `dropdown.py`: Implements dropdown menus for selecting algorithms and speed.
* `main.py`: The main program entry point, initializing the visualization and handling user interactions.

**Customization:**

* The code allows customization of various parameters through user interface interactions and configurable settings within the codebase. Users can adjust grid size, cell colors, and visualization speed.

**Further Development:**

Potential enhancements for future development include:

* Implementing additional pathfinding algorithms.
* Integrating heuristic functions for A* optimization.
* Visualizing pathfinding performance metrics.

**Contributing:**

This project welcomes contributions from the community. Feel free to fork the repository and submit pull requests with improvements or additional features.
