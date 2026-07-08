import pygame
import random

# --- INITIALIZATION ---
pygame.init()
w, h = 1600, 900
display_surface = pygame.display.set_mode((w, h))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
running = True

# --- SPRITE CLASSES ---


class Player(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 400

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 10:
            self.direction.x -= 1
        if keys[pygame.K_d] and self.rect.right < w - 10:
            self.direction.x += 1
        if keys[pygame.K_w] and self.rect.top > 10:
            self.direction.y -= 1
        if keys[pygame.K_s] and self.rect.bottom < h - 10:
            self.direction.y += 1

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        self.direction.update(0, 0)


class Star(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load("images/star.png").convert_alpha()
        self.rect = self.image.get_frect(
            topleft=(random.randint(0, w - int(self.image.get_width())),
                     random.randint(-h, h))
        )
        self.speed = 300

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.y > h:
            self.rect.y = random.randint(-150, -int(self.rect.height))

            while True:
                self.rect.x = random.randint(0, w - int(self.rect.width))
                overlap = any(
                    self.rect.colliderect(other.rect)
                    for other in self.groups()[0]
                    if isinstance(other, Star) and other != self
                )
                if not overlap:
                    break


class Meteor(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.image.load("images/meteor.png").convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))


class Laser(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.image.load("images/laser.png").convert_alpha()
        self.rect = self.image.get_frect(bottom=y, centerx=x)
        self.speed = 500

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()


# --- GROUPS & OBJECT CREATION ---
all_sprites = pygame.sprite.Group()

# Spawn stars
for _ in range(20):
    while True:
        star = Star(all_sprites)
        if not any(star.rect.colliderect(other.rect) for other in all_sprites if isinstance(other, Star) and other != star):
            break
        star.kill()
player = Player(all_sprites, w // 2, h // 2)


laser_cooldown = 0.3
laser_timer = 0

# --- MAIN GAME LOOP ---
while running:
    dt = clock.tick(60) / 1000
    laser_timer += dt

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- AUTOMATIC SHOOTING ---
    if laser_timer >= laser_cooldown:
        Laser(all_sprites, player.rect.centerx, player.rect.top - 10)
        laser_timer = 0

    # --- UPDATE ---
    all_sprites.update(dt)

    # --- DRAWING ---
    display_surface.fill("black")
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()
