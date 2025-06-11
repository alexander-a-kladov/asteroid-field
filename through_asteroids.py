#!/usr/bin/python3

import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Survival")

# Colors
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Game constants
SHIP_SIZE = 50
ASTEROID_SIZE = 40
BULLET_SIZE = 8
ASTEROID_SPEED = 3
SHIP_SPEED = 6
BULLET_SPEED = 10
ASTEROID_COUNT = 7
RELOAD_TIME = 5  # seconds

FONT = pygame.font.SysFont("Arial", 32)
CLOCK = pygame.time.Clock()

class Ship:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - SHIP_SIZE//2, HEIGHT//2 - SHIP_SIZE//2, SHIP_SIZE, SHIP_SIZE)
        self.last_shot = -RELOAD_TIME  # allow instant first shot

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        # Stay within bounds
        self.rect.x = max(0, min(WIDTH - SHIP_SIZE, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - SHIP_SIZE, self.rect.y))

    def draw(self, win):
        pygame.draw.polygon(win, YELLOW, [
            (self.rect.centerx, self.rect.top),
            (self.rect.right, self.rect.bottom),
            (self.rect.left, self.rect.bottom)
        ])

    def can_fire(self):
        return time.time() - self.last_shot >= RELOAD_TIME

class Asteroid:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(0, WIDTH - ASTEROID_SIZE),
            random.randint(-HEIGHT, -ASTEROID_SIZE),
            ASTEROID_SIZE, ASTEROID_SIZE
        )
        self.speed = random.randint(ASTEROID_SPEED, ASTEROID_SPEED + 2)

    def move(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - ASTEROID_SIZE)
            self.rect.y = random.randint(-HEIGHT, -ASTEROID_SIZE)
            self.speed = random.randint(ASTEROID_SPEED, ASTEROID_SPEED + 2)

    def draw(self, win):
        pygame.draw.circle(win, GRAY, self.rect.center, ASTEROID_SIZE//2)

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - BULLET_SIZE//2, y - BULLET_SIZE, BULLET_SIZE, BULLET_SIZE)

    def move(self):
        self.rect.y -= BULLET_SPEED

    def draw(self, win):
        pygame.draw.rect(win, RED, self.rect)

def draw_explosion(win, center):
    for r in range(20, 80, 15):
        pygame.draw.circle(win, RED, center, r, 4)
    pygame.display.flip()
    pygame.time.delay(700)

def main():
    ship = Ship()
    asteroids = [Asteroid() for _ in range(ASTEROID_COUNT)]
    bullets = []
    running = True
    start_time = time.time()
    score = 0
    explosion = False

    while running:
        CLOCK.tick(60)
        WIN.fill(BLACK)

        # Score (survival time)
        if not explosion:
            score = int(time.time() - start_time)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Ship movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= SHIP_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += SHIP_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= SHIP_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += SHIP_SPEED
        ship.move(dx, dy)

        # Firing bullets
        if keys[pygame.K_SPACE] and ship.can_fire() and not explosion:
            bullets.append(Bullet(ship.rect.centerx, ship.rect.top))
            ship.last_shot = time.time()

        # Move and draw asteroids
        for asteroid in asteroids:
            asteroid.move()
            asteroid.draw(WIN)

        # Move and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(WIN)
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        # Collision: Bullets with asteroids
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    asteroids.append(Asteroid())
                    break

        # Draw ship
        if not explosion:
            ship.draw(WIN)

        # Collision: Ship with asteroids
        if not explosion:
            for asteroid in asteroids:
                if ship.rect.colliderect(asteroid.rect):
                    explosion = True
                    draw_explosion(WIN, ship.rect.center)
                    break

        # Draw reload status
        if not ship.can_fire():
            reload_text = FONT.render(f"Reloading...", True, RED)
            WIN.blit(reload_text, (10, HEIGHT - 40))

        # Draw score
        score_text = FONT.render(f"Time Survived: {score}s", True, WHITE)
        WIN.blit(score_text, (10, 10))

        # Game over message
        if explosion:
            over_text = FONT.render("GAME OVER!", True, RED)
            WIN.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
            restart_text = FONT.render("Press R to Restart or Q to Quit", True, WHITE)
            WIN.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

            pygame.display.flip()
            # Handle restart/quit
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            main()
                        if event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                CLOCK.tick(10)
        pygame.display.flip()

if __name__ == "__main__":
    main()

