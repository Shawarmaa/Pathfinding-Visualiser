from tkinter import messagebox, Tk
import pygame
import sys
import random
import math
import time
import heapq

pygame.init()

#settings
window_width, window_height = 800, 800

window_center = window_width/2

button_gap = 10

rows, columns = 50, 50

cell_width = window_width // rows
cell_height = window_height // columns

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
resume_img = pygame.image.load("images/button_resume.png").convert_alpha()

#classes
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
        self.distance = float('inf')

        self.f, self.g, self.h = 0,0,0
    
    def __gt__(self, other): #for heapfunction to operate
        pass

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

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.insert(0,item)

    def pop(self):
        return self.items.pop(0)

    def peek(self):
        return self.items[0]

    def size(self):
        return len(self.items)

#create button instances
escape_button = Button(0, 0, escape_img, 1)
clear_button = Button(0, 50, clear_img, 1)
run_button = Button(0, 100, run_img, 1)
maze_button = Button(window_center -150/2 , window_center - 100, maze_img, 1)
bfs_button = Button(window_center + button_gap*2 + 150, window_center, bfs_img, 1)
dfs_button = Button(window_center -300 - button_gap*2, window_center, dfs_img, 1)
dijkstras_button = Button(window_center -150 - button_gap, window_center, dijkstras_img, 1)
a_star_button = Button(window_center + button_gap, window_center, a_star_img, 1)
fast_button = Button(window_center -150 - button_gap, window_center+100, fast_img, 1)
slow_button = Button(window_center + button_gap , window_center+ 100, slow_img, 1)
resume_button = Button(window_center -150/2 , window_center+ 200, resume_img, 1)

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

def create_path(start_cell, path, current_cell):
    while current_cell.prior != start_cell: 
        path.append(current_cell.prior)
        current_cell = current_cell.prior

def error_msg(searching):
    if searching:
            Tk().wm_withdraw()
            messagebox.showinfo("No Solution", "There is no solution")
            searching = False

    return searching

def dijkstra(start_cell, target_cell, searching, pq, path, heapq, processed):#bfs = dijkstras as weight of each edge equals 1
    if pq and searching:
        current_distance, current_cell = heapq.heappop(pq)
        current_cell.visited = True
        if current_cell not in processed:
            processed.add(current_cell)

            if current_cell == target_cell:
                searching = False
                # traces its prior cells that it neigboured
                create_path(start_cell, path, current_cell)
            else:
                for neighbour in current_cell.neighbours:
                    if not neighbour.queued and not neighbour.wall:
                        distance = current_distance + 1
                        if distance < neighbour.distance:
                            neighbour.distance = distance
                            neighbour.queued = True
                            neighbour.prior = current_cell #stores the prior cell
                            heapq.heappush(pq, (distance, neighbour))

    else:
        searching = error_msg(searching)

    return searching
            
def bfs(start_cell, target_cell, searching, queue, path):
    if queue.size() > 0 and searching:
        #queue.append(start_cell)
        current_cell = queue.dequeue()
        current_cell.visited = True
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            create_path(start_cell, path, current_cell)
        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.queued and not neighbour.wall:
                    neighbour.queued = True
                    neighbour.prior = current_cell #stores the prior cell
                    queue.enqueue(neighbour)
    else:
        searching = error_msg(searching)

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
            create_path(start_cell, path, current_cell)

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
         searching = error_msg(searching)

    return searching
    
def dfs(start_cell, target_cell, searching, stack, path):
    if stack.size() > 0 and searching:
        current_cell = stack.pop()
        current_cell.visited = True
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            create_path(start_cell, path, current_cell)
        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.visited and not neighbour.wall:
                    neighbour.stacked = True
                    neighbour.prior = current_cell #stores the prior cell
                    stack.push(neighbour)
    else:
        searching = error_msg(searching)

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

     #if there's enough space, do a recursive call
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
            if cell.queued or cell.stacked:#neighbours
                cell.draw(window, PURPLE)
            if cell.visited:
                cell.draw(window, TURQUOISE)
            if cell in path:
                cell.draw(window, BLUE)
            if cell.wall:
                cell.draw(window, BLACK)
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
    in_menue = True
    maze_set = False
    selected_algorithm = ""
    set_slow = False
    
    while True:
        #check if game is in the menue
        if in_menue:
            pygame.display.set_caption("Menu")
            window.fill(DARKGREY)
            #selecting maze
            if maze_button.draw(window) and maze_set == False and not begin_search:
                maze(grid)
                maze_set = True
            # selecting traversing algorithms
            if a_star_button.draw(window):
                selected_algorithm = "a*"
            if bfs_button.draw(window):
                selected_algorithm = "bfs"
            if dfs_button.draw(window):
                selected_algorithm = "dfs"
            if dijkstras_button.draw(window):
                selected_algorithm = "dijkstras"
            #selecting traversing speed
            if slow_button.draw(window):
                set_slow = True
            if fast_button.draw(window):
                set_slow = False
            if resume_button.draw(window) and selected_algorithm != "":
                in_menue = False
        else:
            #in Grid
            pygame.display.set_caption("Pathfinding Visualiser")
            window.fill(BLACK)
            draw_grid(grid, path)
            #starts the visualisation
            if run_button.draw(window) and target_cell_set == True and start_cell_set == True:
                begin_search = True
                searching = True
                start_cell.visited = True
                queue = Queue()
                stack = Stack()
                path = []
                openSet, closeSet = [], []
                queue.enqueue(start_cell)
                stack.push(start_cell)
                openSet.append(start_cell)
                
                pq = []
                start_cell.distance = 0
                processed = set()
                heapq.heappush(pq, (0, start_cell))
            #clears the grid
            if clear_button.draw(window):
                begin_search = False
                start_cell_set = False
                target_cell_set = False
                start_cell = None
                target_cell = None
                maze_set = False
                grid = make_grid()
                set_neighbours(grid)
            #switches to the menue
            if escape_button.draw(window):
                in_menue = True
                begin_search = False
                start_cell_set = False
                target_cell_set = False
                start_cell = None
                target_cell = None
                maze_set = False
                grid = make_grid()
                set_neighbours(grid)

        #event handler
        for event in pygame.event.get():
            #quit window
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            #set nodes
            if pygame.mouse.get_pressed()[0] and in_menue == False and begin_search == False:
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
            elif pygame.mouse.get_pressed()[2] and in_menue == False and begin_search == False:
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
                    in_menue = True

        #check algos
        if begin_search:
            if selected_algorithm == "a*":
                searching = a_star(start_cell, target_cell, searching, openSet, closeSet, path)
            if selected_algorithm == "dijkstras":
                searching = dijkstra(start_cell, target_cell, searching, pq, path, heapq, processed)
            if selected_algorithm == "bfs":
                searching = bfs(start_cell, target_cell, searching, queue, path)
            if selected_algorithm == "dfs":
                searching = dfs(start_cell, target_cell, searching, stack, path)
            if set_slow:
                time.sleep(0.1)
            
        pygame.display.flip()

main()