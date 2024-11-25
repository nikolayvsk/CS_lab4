import pygame
import random

WIDTH = 700
HEIGHT = 700
GRID_SIZE = 24 # 12 / 24 / 99 
CELL_SIZE = WIDTH // GRID_SIZE

WHITE = (255, 255, 255)
BLACK = (50, 50, 50)  
BROWN = (100, 70, 50) 
RED = (180, 50, 50)      
YELLOW = (180, 180, 50)  
GREEN = (50, 180, 50)    
DARK_GREEN = (25, 75, 25)   
DARK_RED = (75, 25, 25)    
DARK_YELLOW = (150, 150, 25) 


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, 20)
        self.is_hovered = False

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

class ManagingLight:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Managing light")
        
        self.lights = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.broken_lights = set()
        
        self.pedestrians = []
        self.cell_types = self.generate_map()
        
        self.buttons = [
            Button(10, HEIGHT - 60, 150, 50, "Add Person", GREEN, DARK_GREEN),
            Button(170, HEIGHT - 60, 150, 50, "Clear Persons", YELLOW, DARK_YELLOW),
            Button(330, HEIGHT - 60, 150, 50, "Clear Broken Light", RED, DARK_RED)
        ]
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)

    def generate_map(self):
        cell_types = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if y % 3 == 1 or x % 3 == 1:
                    cell_types[y][x] = 'road'
                elif (y % 3 == 0 or y % 3 == 2) and (x % 3 == 0 or x % 3 == 2):
                    cell_types[y][x] = 'house'
        return cell_types

    def get_random_position(self):
        return random.randint(0, GRID_SIZE), random.randint(0, GRID_SIZE)

    def spawn_pedestrian(self):
        try:
            x, y = self.get_random_position()
            self.pedestrians.append({
                'x': x, 
                'y': y, 
                'speed_x': random.choice([-1, 0, 1]), 
                'speed_y': random.choice([-1, 0, 1])
            })
        except ValueError as e:
            print(f"Error spawning pedestrian: {e}")

    def move_pedestrians(self):
        for pedestrian in self.pedestrians:
            new_x = pedestrian['x'] + pedestrian['speed_x']
            new_y = pedestrian['y'] + pedestrian['speed_y']
            
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                pedestrian['x'] = new_x
                pedestrian['y'] = new_y
            else:
                pedestrian['speed_x'] *= -1
                pedestrian['speed_y'] *= -1
            
            if random.random() < 0.1:
                pedestrian['speed_x'] = random.choice([-1, 0, 1])
                pedestrian['speed_y'] = random.choice([-1, 0, 1])

    def update_lights(self):
        self.lights = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        for pedestrian in self.pedestrians:
            x, y = pedestrian['x'], pedestrian['y']
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if (nx, ny) not in self.broken_lights:
                            self.lights[ny][nx] = True

    def draw(self):
        self.screen.fill(BLACK)
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                
                if (x, y) in self.broken_lights:
                    pygame.draw.rect(self.screen, RED, rect)
                else:
                    base_color = self.get_base_color(x, y)
                    if self.lights[y][x]:
                        color = self.get_bright_color(base_color)
                    else:
                        color = base_color
                    pygame.draw.rect(self.screen, color, rect)
        
        for pedestrian in self.pedestrians:
            pedestrian_rect = pygame.Rect(pedestrian['x'] * CELL_SIZE, pedestrian['y'] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, YELLOW, pedestrian_rect)
        
        for button in self.buttons:
            button.draw(self.screen)
            
        counter_text = self.font.render(f"People: {len(self.pedestrians)}", True, WHITE)
        self.screen.blit(counter_text, (WIDTH - 150, HEIGHT - 50))

    def get_base_color(self, x, y):
        cell_type = self.cell_types[y][x]
        if cell_type == 'road':
            return BLACK
        elif cell_type == 'house':
            return BROWN

    def get_bright_color(self, color):
        r, g, b = color
        return (min(255, r + 100), min(255, g + 100), min(255, b + 100))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                for button in self.buttons:
                    button.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.buttons[0].rect.collidepoint(event.pos): 
                            self.spawn_pedestrian()
                        elif self.buttons[1].rect.collidepoint(event.pos): 
                            self.pedestrians = []
                        elif self.buttons[2].rect.collidepoint(event.pos):
                            self.broken_lights.clear()
                        else:
                            x, y = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
                            if (x, y) in self.broken_lights:
                                self.broken_lights.remove((x, y))
                            else:
                                self.broken_lights.add((x, y))

                    elif event.button == 3:
                        x, y = event.pos[0] // CELL_SIZE, event.pos[1] // CELL_SIZE
                        for dx in range(-5, 6):
                            for dy in range(-5, 6):
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                                    if (nx, ny) in self.broken_lights:
                                        self.broken_lights.remove((nx, ny))
                                    else:
                                        self.broken_lights.add((nx, ny))
            
            self.move_pedestrians()
            self.update_lights()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(5)

        pygame.quit()

if __name__ == "__main__":
    game = ManagingLight()
    game.run()
