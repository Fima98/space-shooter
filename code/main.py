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
    def __init__(self, groups, x, y):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 400
        self.health = 3

        #
        self.has_collided = False
        self.col_timer = 0
        self.blink_timer = 0

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.laser_cooldown = 0.3

    def laser_timer(self, dt):
        if not self.can_shoot:
            self.laser_shoot_time += dt
            if self.laser_shoot_time >= self.laser_cooldown:
                self.can_shoot = True
                self.laser_shoot_time = 0

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

        # SHOOTING
        self.laser_timer(dt)
        if self.can_shoot:
            Laser((self.groups()[0], laser_group),
                  self.rect.centerx, self.rect.top - 10)
            self.can_shoot = False

        if self.has_collided:
            self.col_timer += dt
            self.blink_timer += dt

            if self.blink_timer >= 0.1:
                self.blink_timer = 0
                self.image.set_alpha(
                    20 if self.image.get_alpha() == 255 else 255)

            if self.col_timer >= 1:
                self.has_collided = False
                self.col_timer = 0
                self.image.set_alpha(255)


class Star(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
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
    def __init__(self, groups, x, y):
        super().__init__(groups)
        self.original_image = pygame.image.load(
            "images/meteor.png").convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=(x, y))
        self.direction = pygame.math.Vector2(
            random.uniform(-0.5, 0.5), 2).normalize()
        self.speed = random.randint(200, 400)
        self.rotation_speed = random.randint(-200, 200)
        self.angle = 0
        self.health = 3

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

        old_center = self.rect.center

        self.angle += self.rotation_speed * dt
        self.image = pygame.transform.rotate(
            self.original_image, self.angle)

        self.rect = self.image.get_frect(center=old_center)

        if self.health <= 0:
            self.kill()
        if self.rect.top > h or self.rect.left > w or self.rect.right < 0:
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, x, y):
        super().__init__(groups)
        self.image = pygame.image.load("images/laser.png").convert_alpha()
        self.rect = self.image.get_frect(bottom=y, centerx=x)
        self.speed = 500

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()


# --- GROUPS ---
all_sprites = pygame.sprite.Group()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
for _ in range(20):
    while True:
        star = Star(all_sprites)
        if not any(star.rect.colliderect(other.rect) for other in all_sprites if isinstance(other, Star) and other != star):
            break
        star.kill()
player = Player(all_sprites, w // 2, h // 2)
meteor_surface = pygame.image.load("images/meteor.png").convert_alpha()
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 400)


# --- MAIN GAME LOOP ---
while running:
    dt = clock.tick(60) / 1000

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            random_x = random.randint(
                10 + int(meteor_surface.get_width()), w - int(meteor_surface.get_width()) - 10)
            Meteor((all_sprites, meteor_group), random_x, -
                   int(meteor_surface.get_height()))

    # --- UPDATE ---
    all_sprites.update(dt)
    collision_dict = pygame.sprite.groupcollide(
        laser_group, meteor_group, True, False)
    for meteors in collision_dict.values():
        for meteor in meteors:
            meteor.health -= 1
    if pygame.sprite.spritecollide(player, meteor_group, True):
        player.health -= 1
        if player.health <= 0:
            player.kill()
        else:
            player.has_collided = True

    # --- DRAWING ---
    if player.health > 0:
        display_surface.fill("black")
        all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()
