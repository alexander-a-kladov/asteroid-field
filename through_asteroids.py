#!/usr/bin/python3

import pygame
import random
import time
import math
import sys

# Initialize pygame and mixer for sounds
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 600, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Survival")

# Load images
SHIP_IMG = pygame.image.load("images/ship_small.png").convert_alpha()
ASTEROID_IMG = pygame.image.load("images/asteroid_small.png").convert_alpha()
BULLET_IMG = pygame.image.load("images/bullet_small.png").convert_alpha()

# Load sounds
CANNON_SOUND = pygame.mixer.Sound("sounds/cannon.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("sounds/explosion.wav")

# Constants
SHIP_SIZE = SHIP_IMG.get_width()
ASTEROID_SIZE = ASTEROID_IMG.get_width()
BULLET_SIZE = BULLET_IMG.get_width()
SHIP_SPEED = 6
BULLET_SPEED = 12
RELOAD_TIME = 5  # seconds
ASTEROID_SPEED_MIN = 2
ASTEROID_SPEED_MAX = 4
ASTEROID_COUNT = 15

FONT = pygame.font.SysFont("Arial", 32)
CLOCK = pygame.time.Clock()

class Ship:
    def __init__(self):
        self.image = SHIP_IMG
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.last_shot = -RELOAD_TIME  # allow immediate first shot

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        # Keep inside screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def can_fire(self):
        return time.time() - self.last_shot >= RELOAD_TIME

class Asteroid:
    def __init__(self):
        # Spawn on top, left, or right edges only (not bottom)
        edge = random.choice(['top'])#, 'left', 'right'])
        if edge == 'top':
            x = random.randint(0, WIDTH - ASTEROID_SIZE)
            y = -ASTEROID_SIZE
        elif edge == 'left':
            x = -ASTEROID_SIZE
            y = random.randint(0, HEIGHT - ASTEROID_SIZE)
        else:  # right
            x = WIDTH + ASTEROID_SIZE
            y = random.randint(0, HEIGHT - ASTEROID_SIZE)

        self.image = ASTEROID_IMG
        self.rect = self.image.get_rect(topleft=(x, y))

        # Velocity: angle depends on spawn edge, pointing inward/downward
        if edge == 'top':
            angle = random.uniform(math.radians(80), math.radians(100))
        elif edge == 'left':
            angle = random.uniform(math.radians(-10), math.radians(10))
        else:  # right
            angle = random.uniform(math.radians(135), math.radians(145))

        speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Respawn if off screen
        if (self.rect.top > HEIGHT + ASTEROID_SIZE or
            self.rect.left > WIDTH + ASTEROID_SIZE or
            self.rect.right < -ASTEROID_SIZE):
            self.__init__()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.image = BULLET_IMG
        self.rect = self.image.get_rect(center=(x, y))

    def move(self):
        self.rect.y -= BULLET_SPEED

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def draw_explosion(surface, center):
    EXPLOSION_SOUND.play()
    # Simple expanding circle explosion effect
    for radius in range(20, 80, 15):
        pygame.draw.circle(surface, (255, 0, 0), center, radius, 4)
        pygame.display.flip()
        pygame.time.delay(70)

def main():
    ship = Ship()
    asteroids = [Asteroid() for _ in range(ASTEROID_COUNT)]
    bullets = []
    running = True
    explosion = False
    start_time = time.time()
    score = 0

    while running:
        CLOCK.tick(60)
        WIN.fill((0, 0, 0))

        # Survival time score
        if not explosion:
            score = int(time.time() - start_time)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if not explosion:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= SHIP_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += SHIP_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= SHIP_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += SHIP_SPEED
            ship.move(dx, dy)

            # Fire bullet if space pressed and reload complete
            if keys[pygame.K_SPACE] and ship.can_fire():
                bullets.append(Bullet(ship.rect.centerx, ship.rect.top))
                ship.last_shot = time.time()
                CANNON_SOUND.play()

        # Move and draw asteroids
        for asteroid in asteroids:
            asteroid.move()
            asteroid.draw(WIN)

        # Move and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)
            else:
                bullet.draw(WIN)

        # Bullet-asteroid collision
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    asteroids.append(Asteroid())
                    break

        # Draw ship or explosion
        if not explosion:
            ship.draw(WIN)
        else:
            # Show explosion effect once
            draw_explosion(WIN, ship.rect.center)

        # Ship-asteroid collision
        if not explosion:
            for asteroid in asteroids:
                if ship.rect.colliderect(asteroid.rect):
                    explosion = True
                    EXPLOSION_SOUND.play()
                    break

        # Draw reload status
        if not ship.can_fire() and not explosion:
            reload_text = FONT.render("Reloading...", True, (255, 0, 0))
            WIN.blit(reload_text, (10, HEIGHT - 40))

        # Draw score
        score_text = FONT.render(f"Time Survived: {score}s", True, (255, 255, 255))
        WIN.blit(score_text, (10, 10))

        # Game over screen
        if explosion:
            over_text = FONT.render("GAME OVER!", True, (255, 0, 0))
            WIN.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
            restart_text = FONT.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
            WIN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
            pygame.display.flip()

            # Wait for restart or quit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                CLOCK.tick(10)
        pygame.display.flip()

if __name__ == "__main__":
    main()

