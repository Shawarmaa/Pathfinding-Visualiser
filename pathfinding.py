from tkinter import messagebox, Tk
import pygame
import sys
import random
import math
import time

pygame.init()

#settings
window_width, window_height = 800, 800

window_center = window_width/2

button_gap = 10

rows, columns = 50, 50

cell_width = window_width // rows
cell_height = window_height // columns

#cell colours
START = (0,128,0)
END = (255, 0, 0)
WALL = (8, 8, 8)
BLANK = (238,215,218)
VISITED = (172,58,74)
PATH = (205, 141, 0)
WAITING = (102,0,102)

#button colours
COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

window = pygame.display.set_mode((window_width,window_height))

#game buttons(left click, right click, run,clear, [?]/ESC)
run_img = pygame.image.load("images/run.png").convert_alpha()
clear_img = pygame.image.load("images/clear.png").convert_alpha()

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

class DropDown():

    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center = rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)
        
        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i+1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1

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

class PriorityQueue:
    def __init__(self):
        self.queue = []
 
    def insert(self, priority, val):
        self.queue.append((priority, val))
 
    def remove(self):
        max_idx = 0
        for i in range(1, len(self.queue)):
            if self.queue[i][0] < self.queue[max_idx][0]:
                max_idx = i
        val = self.queue[max_idx][1]
        while max_idx < len(self.queue) - 1:
            self.queue[max_idx] = self.queue[max_idx + 1]
            max_idx += 1
        priority = self.queue.pop()

        return priority[0], val
    
    def size(self):
        return len(self.queue)
    
#create button instances
clear_button = Button(0, 50, clear_img, 1)
run_button = Button(0, 100, run_img, 1)


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

def dijkstra(start_cell, target_cell, searching, pq, path):

    #when the queue is not empty
    if pq.size() > 0 and searching:
        current_distance, current_cell = pq.remove()
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
                        pq.insert(distance, neighbour)
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

def clear():
    pass


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
    maze_set = False
    selected_algorithm, selected_maze = "", ""
    
    algorithms = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE], 
    5, 5, 120, 40,
    pygame.font.SysFont(None, 30)," Algorithms",
    ["Dijkstra's", "A*", "BFS", "DFS"])

    maze_menue = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE], 
    130, 5, 120, 40,
    pygame.font.SysFont(None, 30)," Add-on",
    ["Maze", "Empty Grid"])

    
    while True:
        #check if game is in the menue
        event_list = pygame.event.get()

        #event handler
        for event in event_list:
            
            #quit window
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            
            #set nodes
            if pygame.mouse.get_pressed()[0] and begin_search == False:
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
            elif pygame.mouse.get_pressed()[2] and begin_search == False:
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
                
                if event.key == pygame.K_SPACE and target_cell_set == True and start_cell_set == True and not begin_search:
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
                    pq = PriorityQueue()
                    pq.insert(0,start_cell)
                
                if event.key == pygame.K_c:
                    begin_search = False
                    start_cell_set = False
                    target_cell_set = False
                    start_cell = None
                    target_cell = None
                    maze_set = False
                    grid = make_grid()
                    set_neighbours(grid)
       
        #updates drop down menu options
        selected_algo = algorithms.update(event_list)
        if selected_algo >= 0:
            selected_algorithm = algorithms.main = algorithms.options[selected_algo]
        
        selected_maze_menue = maze_menue.update(event_list)
        if selected_maze_menue >= 0:
            selected_maze = maze_menue.main = maze_menue.options[selected_maze_menue]
        
        #check algos
        if begin_search:
            if selected_algorithm == "A*":
                searching = a_star(start_cell, target_cell, searching, openSet, closeSet, path)
            if selected_algorithm == "Dijkstra's":
                searching = dijkstra(start_cell, target_cell, searching, pq, path)
            if selected_algorithm == "BFS":
                searching = bfs(start_cell, target_cell, searching, queue, path)
            if selected_algorithm == "DFS":
                searching = dfs(start_cell, target_cell, searching, stack, path)

        else:
            if selected_maze == "Maze" and maze_set == False:
                maze(grid)
                maze_set = True
            if selected_maze == "Empty Grid" and maze_set == True:
                maze_set = False
                #clear()
            

        draw_grid(grid, path)
        algorithms.draw(window)
        maze_menue.draw(window)
        pygame.display.flip()

main()