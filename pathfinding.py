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

rows, columns = 50, 50

cell_width = window_width // rows
cell_height = window_height // columns

fpsClock = pygame.time.Clock()

#cell colours
START = (0,128,0)
END = (255, 0, 0)
WALL = (33, 37, 41)
BLANK = (255,255,255)
VISITED = (172,58,74)
PATH = (205, 141, 0)
WAITING = (102,0,102)

#button colours
INACTIVE_BUTTON = (33, 37, 41)
ACTIVE_BUTTON = (8, 8, 8)


#font
font = pygame.font.SysFont(None, 30)

window = pygame.display.set_mode((window_width,window_height))


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
        self.menue = False

        self.f, self.g, self.h = 0,0,0
    
    def __gt__(self, other): #for heapfunction to operate
        pass
    
    def make_start(self):
        self.start = True
        self.blank = False
        self.wall = False
        return self.start

    def make_target(self):
        self.target = True
        self.blank = False
        self.wall = False
        return self.target

    def make_wall(self):
        self.wall = True
        self.blank = False

    def make_blank(self):
        self.blank = True

    def remove_start(self):
        self.start = False
        return self.start

    def remove_target(self):
        self.target = False
        return self.target
    
    def remove_wall(self):
        self.wall = False
        self.blank = True

    def draw(self, win, colour):
        pygame.draw.rect(win, colour, (self.x * cell_width, self.y * cell_height, cell_width -1, cell_height -1))

    def set_neighbours(self, grid):

        if self.y < rows -1:
            self.neighbours.append(grid[self.x][self.y+1]) #up
        if self.x < columns -1:
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
        msg = self.font.render(self.main, 1, (255,255,255))
        surf.blit(msg, msg.get_rect(center = self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i+1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (255,255,255))
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
    def __init__(self, font, text, width, height, pos, color, hover):
        self.original_y_pos = pos[1]
        self.color = color
        self.hover = hover
        self.clicked = False
        self.top_rect = pygame.Rect(pos,(width,height))
        self.top_color = color
        self.bottom_rect = pygame.Rect(pos,(width,height))
        font = font
        self.text_surf = font.render(text,True,'#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

    def draw_button(self, screen):
        action = False
        pos = pygame.mouse.get_pos()
        top_rect = self.top_rect.copy()

        if top_rect.collidepoint(pos):
            self.top_color = self.color
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True                

            elif pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                self.clicked = False
                action = True
            self.top_color = self.hover
        else:
            self.top_color = self.color

        top_surf = pygame.Surface(top_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(top_surf, self.top_color, (0, 0, *top_rect.size))
        screen.blit(top_surf, top_rect.topleft)

        screen.blit(self.text_surf, self.text_rect)
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

#Set Buttons
algorithms = DropDown(
    [INACTIVE_BUTTON, ACTIVE_BUTTON],
    [INACTIVE_BUTTON, ACTIVE_BUTTON], 
    5, 4, 120, 40,
    font," Algorithms",
    ["Dijkstra's", "A*", "BFS", "DFS"])
    
speed_menue = DropDown(
    [INACTIVE_BUTTON, ACTIVE_BUTTON],
    [INACTIVE_BUTTON, ACTIVE_BUTTON], 
    130, 4, 120, 40,
    font," Speed",
    ["Fast", "Slow"])

mazeButton = Button(font, "Maze", 120, 40, (255, 4),  INACTIVE_BUTTON, ACTIVE_BUTTON)
runButton = Button(font, "Visualise", 120, 40, (380, 4),  INACTIVE_BUTTON, ACTIVE_BUTTON)
clearButton = Button(font, "Clear", 120, 40, (505, 4),  INACTIVE_BUTTON, ACTIVE_BUTTON)

#Create grid
def make_grid():
    grid = []
    for i in range(columns): 
        arr = []
        for j in range(rows):
            arr.append(Cell(i,j))
        grid.append(arr)
    
    set_neighbours(grid)

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
    #Fill in the outside walls, the space behind the menue will be empty and wont be searched
    create_outside_walls(grid)

    #Start the recursive process
    make_maze_recursive_call(grid, columns - 1, 0, 2, rows - 1)

#border walls
def create_outside_walls(grid):
    #Create top and bottom border walls
    #Create left and right walls
    for i in range(len(grid)):
        (grid[i][2]).wall = True
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
    #set menue
    for k in range(len(grid)):
        for l in range(0,3):
            (grid[k][l]).menue = True
            (grid[k][l]).wall = True

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
    #resets the variables
    def clear():
        return False, False, False, None, None, False, []

    searching = False
    begin_search, start_cell_set, target_cell_set, start_cell, target_cell, maze_set, path = clear()
    grid = make_grid()
    selected_algorithm, selected_speed = "", ""

    while True:
        #FPS
        fpsClock.tick(200)

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

                if cell.menue == True:
                    pass
                #set start
                elif start_cell_set == False:
                    start_cell = cell
                    start_cell_set = cell.make_start()

                #set target
                elif target_cell_set == False and not cell.start: # not will return True if the expression is False
                    target_cell = cell
                    target_cell_set = cell.make_target()
                    
                #set wall
                elif not cell.start and not cell.target:
                    cell.make_wall()

            #remove nodes
            elif pygame.mouse.get_pressed()[2] and begin_search == False:
                x, y= get_mouse_pos()
                i = x // cell_width
                j = y // cell_height
                cell = grid[i][j]
                cell.make_blank()

                #remove start
                if cell.start:
                    start_cell_set = cell.remove_start()

                #remove target
                elif cell.target:
                    target_cell_set = cell.remove_target()

                cell.remove_wall()

        #updates drop down menu options
        selected_algo = algorithms.update(event_list)
        if selected_algo >= 0:
            selected_algorithm = algorithms.main = algorithms.options[selected_algo]
        
        selected_speed_menue = speed_menue.update(event_list)
        if selected_speed_menue >= 0:
            selected_speed = speed_menue.main = speed_menue.options[selected_speed_menue]    

        #check algos
        if begin_search:
            if selected_algorithm == "A*":
                searching = a_star(start_cell, target_cell, searching, openSet, closeSet, path)

            elif selected_algorithm == "Dijkstra's":
                searching = dijkstra(start_cell, target_cell, searching, pq, path)     

            elif selected_algorithm == "BFS":
                searching = bfs(start_cell, target_cell, searching, queue, path)

            elif selected_algorithm == "DFS":
                searching = dfs(start_cell, target_cell, searching, stack, path)

            #slow speed button
            if selected_speed == "Slow":
                time.sleep(0.2)
            #fast speed button
            elif selected_speed == "Fast":
                selected_speed = "Fast"

        #maze button
        if mazeButton.clicked == True and maze_set == False and not begin_search:
            maze(grid)
            maze_set = True

        #visualise button
        if runButton.clicked == True and target_cell_set == True and start_cell_set == True and not begin_search:
            begin_search = True
            searching = True
            start_cell.visited = True
            stack = Stack()
            stack.push(start_cell)
            openSet, closeSet = [], []
            openSet.append(start_cell)
            queue = Queue()
            queue.enqueue(start_cell)
            pq = PriorityQueue()
            pq.insert(0,start_cell)
        
        #clear button
        if clearButton.clicked == True:
            begin_search, start_cell_set, target_cell_set, start_cell, target_cell, maze_set, path = clear()
            grid = make_grid() 

        #draw functions  
        window.fill(INACTIVE_BUTTON)
        draw_grid(grid, path)
        algorithms.draw(window)
        speed_menue.draw(window)
        mazeButton.draw_button(window)
        clearButton.draw_button(window)
        runButton.draw_button(window)
        pygame.display.flip()

main()