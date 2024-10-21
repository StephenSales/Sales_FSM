import pygame
import sys

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
FPS = 30
PLAYER_SIZE = 20
GUARD_SIZE = 20
GUARD_VISION_WIDTH = 120
GUARD_VISION_HEIGHT = 100
DOOR_WIDTH = 50
DOOR_HEIGHT = 30
KEY_SIZE = 15

table = [[0, 1, -1, -1, 4],
         [-1, 1, 2, -1, 4],
         [-1, -1, 2, 3, 4],
         [-1, -1, -1, 3, 4],
         [-1, -1, -1, -1, 4]]

pygame.init()

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map Test")

# Player class
class Player:
    def __init__(self):
        self.x = 40
        self.y = 600
        self.speed = 5
        self.keys_collected = 0

    def move(self, dx, dy):
        # Store the old position in case of collision
        old_x, old_y = self.x, self.y

        self.x += dx * self.speed
        self.y += dy * self.speed

        # Create the player's rectangle
        player_rect = self.get_rect()

        # Wall collision check
        for wall in walls:
            if player_rect.colliderect(wall):
                # If a collision happens, revert to the old position
                self.x, self.y = old_x, old_y
                break

        self.x = max(0, min(SCREEN_WIDTH - PLAYER_SIZE, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - PLAYER_SIZE, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x + PLAYER_SIZE // 2, self.y + PLAYER_SIZE // 2), PLAYER_SIZE // 2)

# Door class
class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, DOOR_WIDTH, DOOR_HEIGHT))

# Key class
class Key:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, KEY_SIZE, KEY_SIZE)

    def draw(self):
        if not self.collected:  # Only draw the key if it hasn't been collected
            pygame.draw.circle(screen, BLUE, (self.x + KEY_SIZE // 2, self.y + KEY_SIZE // 2), KEY_SIZE // 2)

# Guard class
class Guard:
    def __init__(self, x, y, patrol_distance, vertical = False):
        self.x = x
        self.y = y
        self.patrol_distance = patrol_distance
        self.speed = 5
        self.direction = 1  # 1: right, -1: left
        self.vertical = vertical  # Determines if the guard patrols vertically

    def move(self):
        if self.vertical:
            self.y += self.speed * self.direction
            if self.y > self.patrol_distance[1] or self.y < self.patrol_distance[0]:
                self.direction *= -1
        else:
            self.x += self.speed * self.direction
            if self.x > self.patrol_distance[1] or self.x < self.patrol_distance[0]:
                self.direction *= -1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, GUARD_SIZE, GUARD_SIZE)

    def get_vision_rect(self):
        # Adjust vision range based on movement direction
        if self.vertical:  # Vertical movement (up/down)
            if self.direction == 1:  # Moving down
                return pygame.Rect(self.x + 20 - GUARD_VISION_WIDTH // 2, self.y + GUARD_SIZE, GUARD_VISION_HEIGHT, GUARD_VISION_WIDTH)
            else:  # Moving up
                return pygame.Rect(self.x + 20 - GUARD_VISION_WIDTH // 2, self.y - GUARD_SIZE - GUARD_VISION_HEIGHT, GUARD_VISION_HEIGHT, GUARD_VISION_WIDTH)
        else:  # Horizontal movement (left/right)
            if self.direction == 1:  # Moving right
                return pygame.Rect(self.x + GUARD_SIZE, self.y + 10 - GUARD_VISION_HEIGHT // 2, GUARD_VISION_WIDTH, GUARD_VISION_HEIGHT)
            else:  # Moving left
                return pygame.Rect(self.x - GUARD_VISION_WIDTH, self.y + 10 - GUARD_VISION_HEIGHT // 2, GUARD_VISION_WIDTH, GUARD_VISION_HEIGHT)
            
    def draw(self):
        pygame.draw.rect(screen, GREEN, self.get_rect())
        pygame.draw.rect(screen, (0, 255, 0, 50), self.get_vision_rect(), 2)

# Define walls as rectangles
walls = [
    pygame.Rect(100, 300, 20, 800),
    pygame.Rect(100, 0, 20, 200),
    pygame.Rect(200, 180, 400, 20),
    pygame.Rect(600, 0, 20, 200),
    pygame.Rect(100, 300, 500, 20),
    pygame.Rect(600, 300, 20, 220),
    pygame.Rect(200, 500, 400, 20),
]

def main():
    clock = pygame.time.Clock()
    player = Player()
    door = Door(680, 0)
    item_keys = [Key(500, 400), Key(500, 80)]
    guards = [Guard(40, 20, (20, 300), vertical=True), Guard(250, 80, (250, 450)), Guard(450, 400, (250, 450)), Guard(700, 450, (150, 450), vertical=True)]
    guards[2].direction = -1
    guards[3].direction = -1
    state = 0

    # Main game loop
    running = True
    while running:
        input = state
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the user clicks the close button
                running = False

        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        player.move(dx, dy)

        # Check for collision with the door (only if both keys are collected)
        if (door.x < player.x < door.x + DOOR_WIDTH and
            door.y < player.y < door.y + DOOR_HEIGHT and
            state == 2):  # Player needs all keys
            input = 3
            print("You've reached the exit and collected all keys! You win!")

        # Check for collisions with keys
        player_rect = player.get_rect()
        for key in item_keys:
            if player_rect.colliderect(key.get_rect()) and not key.collected:
                key.collected = True
                player.keys_collected += 1
                match state:
                    case 0:
                        input = 1
                    case 1:
                        input = 2
                print(f"Key collected! Total keys: {player.keys_collected}")

        # Move the guards
        for guard in guards:
            guard.move()

            # Check if the player is caught by a guard (either in vision range or direct collision)
            if guard.get_rect().colliderect(player_rect) or guard.get_vision_rect().colliderect(player_rect):
                print("Caught by a guard! Restarting...")
                input = 4

        state = table[state][input]
        match state:
            case 3:
                running = False
            case 4:
                main()

        # Clear screen
        screen.fill(BLACK)

        # Draw the player and the door
        player.draw()
        door.draw()
        for key in item_keys:
            key.draw()

        # Draw the guards
        for guard in guards:
            guard.draw()

        # Draw walls
        for wall in walls:
            pygame.draw.rect(screen, (100, 100, 100), wall)

        # Display score
        font = pygame.font.Font(None, 36)
        text = font.render(f'Keys: {player.keys_collected}', True, WHITE)
        screen.blit(text, (10, 10))
        
        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()