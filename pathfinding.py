from tkinter import messagebox, Tk
import pygame
import button
import sys
import random
import math
import time

pygame.init()

#settings
window_width, window_height = 800, 800

rows, columns = 50, 50

cell_width = window_width // rows
cell_height = window_height // columns



pygame.display.set_caption("Pathfinding Visualiser")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (50, 50, 50)
DARKGREY = (10,10,10)
TURQUOISE = (64, 224, 208)

window = pygame.display.set_mode((window_width,window_height))


#game buttons(left click, right click, run,clear, [?]/ESC)
run_img = pygame.image.load("images/run.png").convert_alpha()
clear_img = pygame.image.load("images/clear.png").convert_alpha()
escape_img = pygame.image.load("images/escape.png").convert_alpha()

#menue buttons(maze, slow, fast, bfs, dfs, dijkstras, A*)
maze_img = pygame.image.load("images/maze.png").convert_alpha()
bfs_img = pygame.image.load("images/button_bfs.png").convert_alpha()
dfs_img = pygame.image.load("images/button_dfs.png").convert_alpha()
dijkstras_img = pygame.image.load("images/button_dijkstras.png").convert_alpha()
a_star_img = pygame.image.load("images/button_a.png").convert_alpha()
fast_img = pygame.image.load("images/button_fast.png").convert_alpha()
slow_img = pygame.image.load("images/button_slow.png").convert_alpha()


#create button instances
run_button = button.Button(0, 0, run_img, 0.1)
clear_button = button.Button(0, 50, clear_img, 0.1)
escape_button = button.Button(0, 100, escape_img, 0.1)
maze_button = button.Button(0, 150, maze_img, 0.1)
bfs_button = button.Button(0, 200, bfs_img, 0.5)
dfs_button = button.Button(0, 250, dfs_img, 0.5)
dijkstras_button = button.Button(0, 300, dijkstras_img, 0.5)
a_star_button = button.Button(0, 350, a_star_img, 0.5)
fast_button = button.Button(0, 400, fast_img, 0.5)
slow_button = button.Button(0, 450, slow_img, 0.5)


class Cell:
    def __init__(self, i, j):
        self.x = i
        self.y = j
        self.start = False
        self.wall = False
        self.target = False
        self.blank = True
        self.queued = False
        self.stacked = False
        self.visited = False
        self.prior = None
        self.neighbours = []

        self.f, self.g, self.h = 0,0,0

    def draw(self, win, colour):
        pygame.draw.rect(win, colour, (self.x * cell_width, self.y * cell_height, cell_width - 2, cell_height - 2))# if the (-2)lines are removed it will look aesthetic in a maze

    def set_neighbours(self, grid):
        if self.x > 0:
            self.neighbours.append(grid[self.x-1][self.y]) #left
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y-1]) #down
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x+1][self.y]) #right
        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y+1]) #up
        
#Create grid
def make_grid():
    grid = []
    for i in range(columns): 
        arr = []
        for j in range(rows):
            arr.append(Cell(i,j))
        grid.append(arr)
    return grid


#Set Neighbours
def set_neighbours(grid):
    for i in range(columns):
        for j in range(rows):
            grid[i][j].set_neighbours(grid)

def get_mouse_pos():
    x = pygame.mouse.get_pos()[0]
    y = pygame.mouse.get_pos()[1]
    
    return x,y

#manhattan distance
def heuristics(a, b):
    return math.sqrt((a.x - b.x)**2 + abs(a.y - b.y)**2)


def dijkstra(start_cell, target_cell, searching, queue, path):#bfs = dijkstras as weight of each edge equals 1
    if len(queue) > 0 and searching:
        #queue.append(start_cell)
        current_cell = queue.pop(0)
        current_cell.visited = True
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            while current_cell.prior != start_cell: 
                path.append(current_cell.prior)
                current_cell = current_cell.prior
        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_cell #stores the prior cell
                    queue.append(neighbour)
    else:
        if searching:
            Tk().wm_withdraw()
            messagebox.showinfo("No Solution", "There is no solution")
            searching = False

    return searching
            
def bfs(start_cell, target_cell, searching, queue, path):
    if len(queue) > 0 and searching:
        current_cell = queue.pop(0)
        current_cell.visited = True
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            while current_cell.prior != start_cell: 
                path.append(current_cell.prior)
                current_cell = current_cell.prior
        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_cell #stores the prior cell
                    queue.append(neighbour)
    else:
        if searching:
            Tk().wm_withdraw()
            messagebox.showinfo("No Solution", "There is no solution")
            searching = False

    return searching


def a_star(start_cell, target_cell, searching, openSet, closeSet, path):

    if len(openSet) > 0 and searching:
        winner = 0
        for i in range(len(openSet)):
            if openSet[i].f < openSet[winner].f:
                winner = i

        current_cell = openSet[winner]
        current_cell.visited = True
        openSet.remove(current_cell)
        
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            while current_cell.prior != start_cell:
                path.append(current_cell.prior)
                current_cell = current_cell.prior

        else:
            closeSet.append(current_cell)
            for neighbour in current_cell.neighbours:
                if not neighbour.visited and not neighbour.wall:
                    tempG = current_cell.g + 1

                    if neighbour in openSet:
                        if tempG < neighbour.g:
                            neighbour.g = tempG
                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)
                        neighbour.queued = True

                    
                    neighbour.h = heuristics(neighbour, target_cell)
                    neighbour.f = neighbour.g + neighbour.h
                    neighbour.prior = current_cell

    else:
         if searching:
            Tk().wm_withdraw()
            messagebox.showinfo("No Solution", "There was no solution" )
            searching = False

    return searching
    

def dfs(start_cell, target_cell, searching, stack, path):
    if len(stack) > 0 and searching:
        current_cell = stack.pop()
        current_cell.visited = True
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            while current_cell.prior != start_cell: 
                path.append(current_cell.prior)
                current_cell = current_cell.prior
        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.visited and not neighbour.wall:
                    neighbour.stacked = True
                    neighbour.prior = current_cell #stores the prior cell
                    stack.append(neighbour)
    else:
        if searching:
            Tk().wm_withdraw()
            messagebox.showinfo("No Solution", "There is no solution")
            searching = False

    return searching
    

def maze(grid):
    
    #Fill in the outside walls
    create_outside_walls(grid)

    #Start the recursive process
    make_maze_recursive_call(grid, columns - 1, 0, 0, rows - 1)

def create_outside_walls(grid):
    #Create outside border walls
        #Create left and right walls
        for i in range(len(grid)):
            (grid[i][0]).wall = True
            (grid[i][len(grid[i])-1]).wall = True

        #Create top and bottom walls
        for j in range(1, len(grid[0]) - 1):
            (grid[0][j]).wall = True
            (grid[len(grid) - 1][j]).wall = True

def make_maze_recursive_call(grid, top, bottom, left, right):
    #where to divide horizontally
    start_range = bottom + 2
    end_range = top - 1
    y = random.randrange(start_range, end_range, 2)

    #division
    for j in range(left + 1, right):
        (grid[y][j]).wall = True

    #where to divide vertically
    start_range = left + 2
    end_range = right - 1
    x = random.randrange(start_range, end_range, 2)
 
     #division
    for i in range(bottom + 1, top):
        (grid[i][x]).wall = True
 
     #make a gap on 3 of the 4 walls and which wall does NOT get a gap
    wall = random.randrange(4)
    if wall != 0:
        gap = random.randrange(left + 1, x, 2)
        (grid[y][gap]).blank = True
        (grid[y][gap]).wall = False

    if wall != 1:
        gap = random.randrange(x + 1, right, 2)
        (grid[y][gap]).blank = True
        (grid[y][gap]).wall = False

    if wall != 2:
        gap = random.randrange(bottom + 1, y, 2)
        (grid[gap][x]).blank = True
        (grid[gap][x]).wall = False

    if wall != 3:
        gap = random.randrange(y + 1, top, 2)
        (grid[gap][x]).blank = True
        (grid[gap][x]).wall = False

     #if there's enough space, to a recursive call
    if top > y + 3 and x > left + 3:
        make_maze_recursive_call(grid, top, y, left, x)

    if top > y + 3 and x + 3 < right:
        make_maze_recursive_call(grid, top, y, x, right)

    if bottom + 3 < y and x + 3 < right:
        make_maze_recursive_call(grid, y, bottom, x, right)

    if bottom + 3 < y and x > left + 3:
        make_maze_recursive_call(grid, y, bottom, left, x)
    
def draw_grid(grid, path):
    for i in range(columns):
        for j in range(rows):
            cell = grid[i][j]
            cell.draw(window, GREY)
            if cell.blank:
                cell.draw(window,GREY)
            if cell.queued or cell.stacked:
                cell.draw(window, PURPLE)
            if cell.visited:
                cell.draw(window, TURQUOISE)
            if cell in path:
                cell.draw(window, BLUE)
            if cell.wall:
                cell.draw(window, DARKGREY)
            if cell.start:
                cell.draw(window, ORANGE)
            if cell.target:
                cell.draw(window, RED)


def main():
    grid = make_grid()
    set_neighbours(grid)
    path = []
    begin_search = False
    searching = True
    start_cell_set = False
    target_cell_set = False
    start_cell = None
    target_cell = None
    run = True
    in_menue = True
    maze_set = False

    selected_algorithm = ""
    
   

    while run:
        #check if game is paused
        if in_menue:
            window.fill(WHITE)

            if maze_button.draw(window) and maze_set == False:
                maze(grid)
                maze_set = True
            if a_star_button.draw(window):
                selected_algorithm = "a*"
                in_menue = False
            if bfs_button.draw(window):
                selected_algorithm = "bfs"
                in_menue = False
            if dfs_button.draw(window):
                selected_algorithm = "dfs"
                in_menue = False
            if dijkstras_button.draw(window):
                selected_algorithm = "dijkstras"
                in_menue = False
                
        else:
            window.fill(BLACK)
            draw_grid(grid, path)

            if run_button.draw(window) and target_cell_set == True and start_cell_set == True:
                begin_search = True
                searching = True
                start_cell.visited = True
                queue = []
                stack = []
                path = []
                openSet, closeSet = [], []
                queue.append(start_cell)
                stack.append(start_cell)
                openSet.append(start_cell)

            if clear_button.draw(window):
                start_cell_set = False
                target_cell_set = False
                start_cell = None
                target_cell = None
                maze_set = False
                grid = make_grid()
                set_neighbours(grid)

            if escape_button.draw(window):
                in_menue = True
                time.sleep(1)
            
        #event handler
        for event in pygame.event.get():
            #quit window
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            #set nodes
            if pygame.mouse.get_pressed()[0] and in_menue == False:
                x, y= get_mouse_pos()
                i = x // cell_width
                j = y // cell_height
                cell = grid[i][j]
                #set start
                if start_cell_set == False:
                    cell.start = True
                    start_cell = cell
                    start_cell_set = True
                    cell.blank = False
                    cell.wall = False
                #set target
                elif target_cell_set == False and not cell.start: # not will return True if the expression is False
                    cell.target = True
                    target_cell = cell
                    target_cell_set = True
                    cell.blank = False
                    cell.wall = False
                #set wall
                elif not cell.start and not cell.target:
                    cell.wall = True
                    cell.blank = False
            #remove nodes
            elif pygame.mouse.get_pressed()[2] and in_menue == False:
                x, y= get_mouse_pos()
                i = x // cell_width
                j = y // cell_height
                cell = grid[i][j]
                cell.blank = True
                #remove start
                if cell.start:
                    cell.start = False
                    start_cell_set = False
                #remove target
                elif cell.target:
                    cell.target = False
                    target_cell_set = False
                cell.wall = False

            #check states
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_menue = False

        #check algos
        if begin_search:
            if selected_algorithm == "a*":
                searching = a_star(start_cell, target_cell, searching, openSet, closeSet, path)
            if selected_algorithm == "dijkstras":
                searching = dijkstra(start_cell, target_cell, searching, queue, path)
            if selected_algorithm == "bfs":
                searching = bfs(start_cell, target_cell, searching, queue, path)
            if selected_algorithm == "dfs":
                searching = dfs(start_cell, target_cell, searching, stack, path)
            
            
        
            
        pygame.display.flip()

main()