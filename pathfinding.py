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

START = (0,128,0)
END = (255, 0, 0)
WALL = (8, 8, 8)
BLANK = (238,215,218)
VISITED = (172,58,74)
PATH = (205, 141, 0)
WAITING = (102,0,102)

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
        self.waiting = False
        self.visited = False
        self.prior = None
        self.neighbours = []
        self.distance = float('inf')

        self.f, self.g, self.h = 0,0,0
    
    def __gt__(self, other): #for heapfunction to operate
        pass

    def draw(self, win, colour):
        
        pygame.draw.rect(win, colour, (self.x * cell_width, self.y * cell_height, cell_width, cell_height))# if the (-2)lines are removed it will look aesthetic in a maze

    def set_neighbours(self, grid):

        if self.y < rows - 1:
            self.neighbours.append(grid[self.x][self.y+1]) #up
        if self.x < columns - 1:
            self.neighbours.append(grid[self.x+1][self.y]) #right
        if self.y > 0:
            self.neighbours.append(grid[self.x][self.y-1]) #down
        if self.x > 0:
            self.neighbours.append(grid[self.x-1][self.y]) #left

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

def dijkstra(start_cell, target_cell, searching, pq, path, heapq):

    #when the queue is not empty
    if pq and searching:
        current_distance, current_cell = heapq.heappop(pq)
        current_cell.visited = True
       
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            create_path(start_cell, path, current_cell)

        else:
            for neighbour in current_cell.neighbours:

                if not neighbour.waiting and not neighbour.wall:
                    distance = current_distance + 1

                    #change the distance of each cell when searching to find the shortest path
                    if distance < neighbour.distance:
                        neighbour.distance = distance
                        neighbour.waiting = True
                        heapq.heappush(pq, (distance, neighbour))
                        neighbour.prior = current_cell 

    else:
        searching = error_msg(searching)

    return searching
            
def bfs(start_cell, target_cell, searching, queue, path):

    if queue.size() > 0 and searching:
        current_cell = queue.dequeue()
        current_cell.visited = True
        
        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            create_path(start_cell, path, current_cell)

        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.waiting and not neighbour.wall:

                    neighbour.waiting = True
                    #stores the prior cell
                    neighbour.prior = current_cell 
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
        closeSet.append(current_cell)

        if current_cell == target_cell:
            searching = False
            # traces its prior cells that it neigboured
            create_path(start_cell, path, current_cell)

        else:
            for neighbour in current_cell.neighbours:
                if not neighbour.visited and not neighbour.wall:
                    tempG = current_cell.g + 1

                    if neighbour in openSet:
                        if tempG < neighbour.g:
                            neighbour.g = tempG

                    else:
                        neighbour.g = tempG
                        openSet.append(neighbour)
                        neighbour.waiting = True
                        
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

                    neighbour.waiting = True
                     #stores the prior cell
                    neighbour.prior = current_cell
                    stack.push(neighbour)
    else:
        searching = error_msg(searching)

    return searching
    
def maze(grid):
    
    #Fill in the outside walls
    create_outside_walls(grid)

    #Start the recursive process
    make_maze_recursive_call(grid, columns - 1, 0, 0, rows - 1)

#border walls
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

#recursive division
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

#setting a colour to each cell    
def draw_grid(grid, path):
    
    for i in range(columns):

        for j in range(rows):

            cell = grid[i][j]
            if cell.blank:
                cell.draw(window,BLANK)
            if cell.waiting:
                cell.draw(window, WAITING)
            if cell.visited:
                cell.draw(window, VISITED)
            if cell in path:
                cell.draw(window, PATH)
            if cell.wall:
                cell.draw(window, WALL)
            if cell.start:
                cell.draw(window, START)
            if cell.target:
                cell.draw(window, END)

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
            window.fill(WALL)

            #selecting maze
            if maze_button.draw(window) and maze_set == False and not begin_search:
                maze(grid)
                maze_set = True

            # selecting traversing algorithms
            if a_star_button.draw(window):
                selected_algorithm = "A*"
                pygame.display.set_caption(selected_algorithm)

            if bfs_button.draw(window):
                selected_algorithm = "BFS"
                pygame.display.set_caption(selected_algorithm)

            if dfs_button.draw(window):
                selected_algorithm = "DFS"
                pygame.display.set_caption(selected_algorithm)

            if dijkstras_button.draw(window):
                selected_algorithm = "Dijkstra's"
                pygame.display.set_caption(selected_algorithm)

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
            
            #window.fill(BLACK)
            draw_grid(grid, path)

            #starts the visualisation
            if run_button.draw(window) and target_cell_set == True and start_cell_set == True and not begin_search:
                begin_search = True
                searching = True
                start_cell.visited = True
                path = []
                stack = Stack()
                stack.push(start_cell)
                openSet, closeSet = [], []
                openSet.append(start_cell)
                queue = Queue()
                queue.enqueue(start_cell)
                pq = []
                start_cell.distance = 0
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
            if selected_algorithm == "A*":
                searching = a_star(start_cell, target_cell, searching, openSet, closeSet, path)
            if selected_algorithm == "Dijkstra's":
                searching = dijkstra(start_cell, target_cell, searching, pq, path, heapq)
            if selected_algorithm == "BFS":
                searching = bfs(start_cell, target_cell, searching, queue, path)
            if selected_algorithm == "DFS":
                searching = dfs(start_cell, target_cell, searching, stack, path)
            if set_slow:
                time.sleep(0.05)
            
        pygame.display.flip()

main()