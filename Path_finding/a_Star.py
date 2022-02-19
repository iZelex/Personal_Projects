from queue import PriorityQueue
import pygame, sys, math


## GLOBAL CONSTANTS ##
FPS = 60
WIDTH = 800
ROWS = 50


## COLOR STATES FOR THE DISPLAY ##
color = {'dark': '#1A1A40',
        'white': '#EEEEEE',
        'dark_blue': '#30475E',
        'blue': '#270082',
        'purple': '#7A0BC0',
        'pink': '#FA58B6',
        'red': '#CF6679',
        'gold': '#FEC260'
}


class Node:
    def __init__(self, row, col, size, t_rows):
        self.color = color['dark']
        self.row = row
        self.col = col
        self.x = col * size
        self.y = row * size
        self.size = size
        self.total_rows = t_rows
        self.g_score = float('inf')
        self.f_score = float('inf')
    
    def set_g(self, g):
        self.g_score = g

    def set_f(self, f):
        self.f_score = f

    def is_empty(self):
        return self.color == color['dark']
    
    def is_obstacle(self):
        return self.color == color['white']

    def is_end(self):
        return self.color == color['gold']
    
    def is_start(self):
        return self.color == color['red']

    def is_edge(self):
        return self.color == color['blue']
    
    def is_checked(self):
        return self.color == color['purple']
    
    def is_path(self):
        return self.color == color['pink']

    def set_edge(self):
        self.color = color['blue']

    def set_checked(self):
        self.color = color['purple']

    def set_path(self):
        self.color = color['pink']

    def set_obstacle(self):
        self.color = color['white']
    
    def set_start(self):
        self.color = color['red']

    def set_end(self):
        self.color = color['gold']

    def reset(self):
        self.color = color['dark']
        self.g_score = float('inf')
        self.f_score = float('inf')

    def get_pos(self):
        return (self.col, self.row)
    
    def get_f(self):
        return self.f_score
    
    def get_g(self):
        return self.g_score

    def update_neighbors(self,grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row+1][self.col])
        # UP
        if self.row > 0 and not grid[self.row-1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row-1][self.col])
        # RIGHT
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col+1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col-1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col-1])
        # UP-LEFT
        if self.col > 0 and self.row > 0 and not grid[self.row-1][self.col-1].is_obstacle() and not grid[self.row-1][self.col].is_obstacle() and not grid[self.row][self.col-1].is_obstacle():
            self.neighbors.append(grid[self.row-1][self.col-1])
        # UP-RIGHT
        if self.row > 0 and self.col < self.total_rows-1 and not grid[self.row-1][self.col+1].is_obstacle() and not grid[self.row-1][self.col].is_obstacle() and not grid[self.row][self.col+1].is_obstacle():
            self.neighbors.append(grid[self.row-1][self.col+1])
        # DOWN-LEFT
        if self.row < self.total_rows-1 and self.col > 0 and not grid[self.row+1][self.col-1].is_obstacle() and not grid[self.row+1][self.col].is_obstacle() and not grid[self.row][self.col-1].is_obstacle():
            self.neighbors.append(grid[self.row+1][self.col-1])
        # DOWN-RIGHT
        if self.row < self.total_rows-1 and self.col < self.total_rows-1 and not grid[self.row+1][self.col+1].is_obstacle() and not grid[self.row-1][self.col].is_obstacle() and not grid[self.row][self.col+1].is_obstacle():
            self.neighbors.append(grid[self.row+1][self.col+1])

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))


class Game:
    def __init__(self):
        pygame.init()
        
        ## CLASS ATTRIBUTES ##

        # FPS parameters
        self.clock = pygame.time.Clock()

        # Window display
        self.width = WIDTH
        self.screen = pygame.display.set_mode((WIDTH,WIDTH))
        pygame.display.set_caption('A* Path Finding Algorithm')

        # Game parameters
        self.rows = ROWS
        self.gap = WIDTH // ROWS
        
    # Runs the game
    def run(self):
        start = None
        end = None
        running = False
        self.make_node_grid()

        while True:
            self.draw_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if running:
                    continue

                if pygame.mouse.get_pressed()[0]: # LEFT CLICK
                    row, col = self.get_click_pos()
                    node = self.grid[row][col]

                    if not start and node != end: # SET STARTING POINT
                        start = node
                        start.set_start()
                    elif not end and node != start: # SET ENDING POINT
                        end = node
                        end.set_end()
                    elif node != start and node != end:
                        node.set_obstacle()
                elif pygame.mouse.get_pressed()[2]: # RIGHT CLICK
                    row, col = self.get_click_pos()
                    node = self.grid[row][col]

                    if node.is_start():
                        start = None
                    elif node.is_end():
                        end = None
                    node.reset()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        for row in self.grid:
                            for node in row:
                                node.update_neighbors(self.grid)

                        algorithm(lambda: self.draw_screen(), self.grid, start, end)

                    if event.key == pygame.K_c:
                        start = None
                        end = None
                        self.make_node_grid()


            self.clock.tick(FPS)
    
    # Generates a grid of nodes
    def make_node_grid(self):
        self.grid = []

        for row in range(self.rows):
            sub_list = []
            for col in range(self.rows):
                temp_node = Node(row, col, self.gap, self.rows)
                sub_list.append(temp_node)
            self.grid.append(sub_list)

    # Draws the grid on the background
    def draw_grid(self):
        for row in range(self.rows):
            pygame.draw.line(self.screen, color['dark_blue'], (0, row*self.gap), (self.width, row*self.gap))
            for col in range(self.rows):
                pygame.draw.line(self.screen, color['dark_blue'], (col*self.gap, 0), (col*self.gap, self.width))

    # Draws the screen and updates it
    def draw_screen(self):
        self.screen.fill(color['dark'])

        for row in self.grid:
            for node in row:
                node.draw(self.screen)

        self.draw_grid()
        pygame.display.update()

    def get_click_pos(self):
        x, y = pygame.mouse.get_pos()
        
        row = y // self.gap
        col = x // self.gap
        
        return row, col


def h(goal, pt):
    gx, gy = goal
    px, py = pt
    return math.sqrt((gx - px)**2 + (gy - py)**2)


def final_path(parent_set, prev, draw, fast):
    while prev in parent_set:
        prev = parent_set[prev]
        prev.set_path()
        if not fast:
            draw()


def algorithm(draw, grid, start, end):
    count = 0
    fast = False
    start.set_g(0) 
    start.set_f(h(end.get_pos(), start.get_pos()))

    open_set = PriorityQueue()
    open_set.put((start.get_f(), count, start))
    
    buffer = {start}
    parent_set = {}
    

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    fast = True

                if event.key == pygame.K_c:
                    game.run()
            
        current = open_set.get()[2]
        buffer.remove(current)

        if current == end:
            final_path(parent_set, end, draw, fast)
            end.set_end()
            start.set_start()
            return True
    
        for neighbor in current.neighbors:
            temp_g = current.get_g() + 1

            if temp_g < neighbor.get_g():
                parent_set[neighbor] = current
                neighbor.set_g(temp_g)
                neighbor.set_f(neighbor.get_g() + h(end.get_pos(), neighbor.get_pos()))
                neighbor.set_checked()
                
                if neighbor not in buffer:
                    count += 1
                    open_set.put((neighbor.get_f(), count, neighbor))
                    buffer.add(neighbor)
                    neighbor.set_edge()

        if not fast:
            draw()

        if current != start:
            current.set_checked()

    return False




if __name__ == '__main__':
    game = Game()
    game.run()
