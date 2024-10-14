import pygame
import random
import math

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('CRT Effect Example')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Set up the font
font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 48)  # Font for menu items
timer_font = pygame.font.Font(None, 48)  # Slightly larger font for timer

# Initialize game state
state = "menu"  # Possible states: "menu", "initial", "survive", "triangle", "game_over"
current_text = 'You have awoken!'
text_surface = font.render(current_text, True, WHITE)
text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Triangle properties
triangle_pos = None  # Initially, the triangle is not drawn
triangle_angle = 0  # Angle in degrees
triangle_speed = 0.5  # Speed for forward/backward movement
triangle_velocity = [0, 0]  # Initial velocity

# Asteroid properties
asteroids = []  # List to hold asteroids
asteroid_size = 30  # Size of the asteroid
max_asteroids = 50  # Maximum number of asteroids (increasing indefinitely)
timer_started = False  # To track if the timer should start
timer_seconds = 0  # Timer in seconds

# Projectile properties
projectiles = []  # List to hold projectiles
projectile_speed = 10  # Speed of the projectile
projectile_size = 5  # Size of the projectile

# Function to draw scanlines
def draw_scanlines(surface, intensity=0.5):
    for y in range(0, SCREEN_HEIGHT, 2):  # Draw every other line
        pygame.draw.rect(surface, (0, 0, 0), (0, y, SCREEN_WIDTH, 1))
        if random.random() < intensity:
            pygame.draw.rect(surface, (30, 30, 30), (0, y, SCREEN_WIDTH, 1))

# Function to draw the triangle (player)
def draw_triangle(surface, pos, angle):
    points = [
        (pos[0] + 20 * math.cos(math.radians(angle)), pos[1] + 20 * math.sin(math.radians(angle))),  # Tip
        (pos[0] + 20 * math.cos(math.radians(angle + 140)), pos[1] + 20 * math.sin(math.radians(angle + 140))),  # Bottom left
        (pos[0] + 20 * math.cos(math.radians(angle - 140)), pos[1] + 20 * math.sin(math.radians(angle - 140)))   # Bottom right
    ]
    pygame.draw.polygon(surface, RED, points)

# Function to draw the asteroid
def draw_asteroid(surface, pos):
    pygame.draw.circle(surface, WHITE, (int(pos[0]), int(pos[1])), asteroid_size)

# Function to draw projectiles
def draw_projectile(surface, pos):
    pygame.draw.circle(surface, WHITE, (int(pos[0]), int(pos[1])), projectile_size)

# Function to check collision between the triangle and the asteroid
def check_collision(triangle_pos, asteroid_pos):
    triangle_radius = 20  # Radius of the triangle tip
    asteroid_radius = asteroid_size
    distance = math.sqrt((triangle_pos[0] - asteroid_pos[0]) ** 2 + (triangle_pos[1] - asteroid_pos[1]) ** 2)
    return distance < (triangle_radius + asteroid_radius)

# Function to spawn a new asteroid
def spawn_asteroid(triangle_pos):
    while True:
        asteroid_pos = [random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT // 2)]
        # Ensure the asteroid doesn't spawn at the triangle's position
        if not (abs(asteroid_pos[0] - triangle_pos[0]) < 50 and abs(asteroid_pos[1] - triangle_pos[1]) < 50):
            return [asteroid_pos, [random.uniform(-1, 1), random.uniform(-1, 1)]]

# Function to create a new projectile
def create_projectile(triangle_pos, angle):
    return [triangle_pos[0], triangle_pos[1], angle]

# Initialize clock for frame rate control
clock = pygame.time.Clock()
run = True
normal_text_jitter_intensity = 3  # Normal text jitter intensity
temporary_text_jitter_intensity = 10  # Increased text jitter intensity during spawn
temporary_jitter_duration = 30  # Frames for temporary jitter
temporary_jitter_counter = 0  # Counter for jitter duration

normal_triangle_jitter_intensity = 1.5  # Triangle jitter intensity
normal_asteroid_jitter_intensity = 1.5  # Asteroid jitter intensity
friction = 0.1  # Friction for slippery effect
asteroid_spawn_counter = 0  # Counter to spawn asteroids
asteroid_spawn_interval = 60  # Frames between asteroid spawns

while run:
    previous_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "menu":
                # Start the game when clicked
                
                
                state = "initial"
            elif event.button == 1:  # Left mouse button
                if state == "initial":
                    current_text = 'You have to survive!'
                    text_surface = font.render(current_text, True, WHITE)
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    state = "survive"
                elif state == "survive":
                    triangle_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
                    state = "triangle"
                    temporary_jitter_counter = temporary_jitter_duration  # Start temporary jitter
                    timer_started = True  # Start the timer

    keys = pygame.key.get_pressed()
    
    # Rotate left or right
    if state == "triangle":  # Only allow movement if the triangle is present
        if keys[pygame.K_LEFT]:
            triangle_angle -= 3  # Rotate left
        if keys[pygame.K_RIGHT]:
            triangle_angle += 3  # Rotate right

        # Move forward/backward
        if keys[pygame.K_UP]:
            triangle_velocity[0] += triangle_speed * math.cos(math.radians(triangle_angle))
            triangle_velocity[1] += triangle_speed * math.sin(math.radians(triangle_angle))
        if keys[pygame.K_DOWN]:
            triangle_velocity[0] -= triangle_speed * math.cos(math.radians(triangle_angle))
            triangle_velocity[1] -= triangle_speed * math.sin(math.radians(triangle_angle))

        # Shoot projectiles
        if keys[pygame.K_SPACE]:  # Space key to shoot
            current_time = pygame.time.get_ticks()
            if current_time - previous_time > 500:
                previous_time = current_time
                projectiles.append(create_projectile(triangle_pos, triangle_angle))

    # Apply friction to create slippery effect
    triangle_velocity[0] *= (1 - friction)
    triangle_velocity[1] *= (1 - friction)

    # Update triangle position based on velocity
    if triangle_pos:
        triangle_pos[0] += triangle_velocity[0]
        triangle_pos[1] += triangle_velocity[1]

    # Only spawn asteroids when the triangle is present
    if state == "triangle":
        # Spawn new asteroids over time
        asteroid_spawn_counter += 1
        if asteroid_spawn_counter >= asteroid_spawn_interval and len(asteroids) < max_asteroids:
            asteroids.append(spawn_asteroid(triangle_pos))
            asteroid_spawn_counter = 0

        # Move asteroids
        for asteroid in asteroids:
            asteroid[0][0] += asteroid[1][0]
            asteroid[0][1] += asteroid[1][1]

            # Bounce the asteroid off the walls
            if asteroid[0][0] <= asteroid_size or asteroid[0][0] >= SCREEN_WIDTH - asteroid_size:
                asteroid[1][0] *= -1
            if asteroid[0][1] <= asteroid_size or asteroid[0][1] >= SCREEN_HEIGHT - asteroid_size:
                asteroid[1][1] *= -1

    # Fill the screen with black
    screen.fill(BLACK)

    # Draw menu if in menu state
    if state == "menu":
        menu_text = "Click to Start"
        menu_surface = menu_font.render(menu_text, True, WHITE)
        menu_rect = menu_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        jitter_x = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
        jitter_y = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
        
        screen.blit(menu_surface, menu_rect)
    else:
        # Draw the timer if it has started
        if timer_started:
            timer_seconds += 1 / 60  # Increment timer by one frame
            timer_surface = timer_font.render(f'{int(timer_seconds)}', True, WHITE)
            
            # Apply jitter to the timer
            timer_jitter_x = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
            timer_jitter_y = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
            jittered_timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 30)).move(timer_jitter_x, timer_jitter_y)
            screen.blit(timer_surface, jittered_timer_rect)

        # Apply jitter effect to the text
        jitter_x = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
        jitter_y = random.randint(-normal_text_jitter_intensity, normal_text_jitter_intensity)
        
        # Increase jitter intensity temporarily when the triangle spawns
        if temporary_jitter_counter > 0:
            jitter_x = random.randint(-temporary_text_jitter_intensity, temporary_text_jitter_intensity)
            jitter_y = random.randint(-temporary_text_jitter_intensity, temporary_text_jitter_intensity)

        jittered_rect = text_rect.move(jitter_x, jitter_y)

        # Draw the text with jitter
        screen.blit(text_surface, jittered_rect)

        # Draw the triangle (player) if it has been initialized
        if triangle_pos:
            # Apply jitter to the triangle
            triangle_jitter_x = random.uniform(-normal_triangle_jitter_intensity, normal_triangle_jitter_intensity)
            triangle_jitter_y = random.uniform(-normal_triangle_jitter_intensity, normal_triangle_jitter_intensity)
            jittered_triangle_pos = (triangle_pos[0] + triangle_jitter_x, triangle_pos[1] + triangle_jitter_y)
            draw_triangle(screen, jittered_triangle_pos, triangle_angle)

        # Draw asteroids with jitter
        for asteroid in asteroids:
            asteroid_jitter_x = random.uniform(-normal_asteroid_jitter_intensity, normal_asteroid_jitter_intensity)
            asteroid_jitter_y = random.uniform(-normal_asteroid_jitter_intensity, normal_asteroid_jitter_intensity)
            jittered_asteroid_pos = (asteroid[0][0] + asteroid_jitter_x, asteroid[0][1] + asteroid_jitter_y)
            draw_asteroid(screen, jittered_asteroid_pos)

            # Check for collision with the triangle
            if triangle_pos and check_collision(triangle_pos, asteroid[0]):
                state = "game_over"  # Set game state to game over
                current_text = "You didn't survive!"
                text_surface = font.render(current_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Update projectiles
        for projectile in projectiles[:]:
            projectile[0] += projectile_speed * math.cos(math.radians(projectile[2]))
            projectile[1] += projectile_speed * math.sin(math.radians(projectile[2]))

            # Draw the projectile
            draw_projectile(screen, projectile[:2])

            # Check for collisions with asteroids
            for asteroid in asteroids[:]:
                if check_collision(projectile[:2], asteroid[0]):
                    asteroids.remove(asteroid)  # Remove asteroid on hit
                    projectiles.remove(projectile)  # Remove projectile on hit
                    break

    # Draw the CRT scanlines effect
    draw_scanlines(screen, intensity=0.4)

    # Update the display
    pygame.display.flip()

    # Decrease the temporary jitter counter
    if temporary_jitter_counter > 0:
        temporary_jitter_counter -= 1

    # Limit frame rate to 60 FPS
    clock.tick(60)

pygame.quit()