import random
import pygame

# --- CONSTANTS ---
WIDTH, HEIGHT = 1600, 900
BG_COLOR = (22, 14, 38)
BTN_COLOR = (60, 40, 100)
WHITE = (255, 255, 255)

# --- SPRITES ---


class Player(pygame.sprite.Sprite):
    def __init__(self, groups, laser_group, x, y):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.laser_group = laser_group
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 400
        self.health = 3

        # Timers & Cooldowns
        self.can_shoot = True
        self.laser_timer = 0
        self.laser_cooldown = 0.3
        self.has_collided = False
        self.col_timer = 0
        self.blink_timer = 0

    def handle_shooting(self, dt):
        if not self.can_shoot:
            self.laser_timer += dt
            if self.laser_timer >= self.laser_cooldown:
                self.can_shoot = True
                self.laser_timer = 0
        else:
            Laser(
                (self.groups()[0], self.laser_group),
                self.rect.centerx,
                self.rect.top - 10,
            )
            self.can_shoot = False

        if self.has_collided:
            self.col_timer += dt
            self.blink_timer += dt
            if self.blink_timer >= 0.1:
                self.blink_timer = 0
                alpha = self.image.get_alpha()
                self.image.set_alpha(
                    20 if alpha is None or alpha == 255 else 255
                )
            if self.col_timer >= 1:
                self.has_collided = False
                self.col_timer = 0
                self.image.set_alpha(255)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = (keys[pygame.K_d] and self.rect.right < WIDTH - 10) - (
            keys[pygame.K_a] and self.rect.left > 10
        )
        self.direction.y = (keys[pygame.K_s] and self.rect.bottom < HEIGHT - 10) - (
            keys[pygame.K_w] and self.rect.top > 10
        )

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.centerx += self.direction.x * self.speed * dt
        self.rect.centery += self.direction.y * self.speed * dt
        self.handle_shooting(dt)


class Star(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/star.png").convert_alpha()
        self.rect = self.image.get_rect(
            topleft=(
                random.randint(0, WIDTH - self.image.get_width()),
                random.randint(-HEIGHT, HEIGHT),
            )
        )
        self.speed = 300

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.y > HEIGHT:
            self.rect.y = random.randint(-150, -self.rect.height)
            while True:
                self.rect.x = random.randint(0, WIDTH - self.rect.width)
                if not any(
                    self.rect.colliderect(other.rect)
                    for other in self.groups()[0]
                    if isinstance(other, Star) and other != self
                ):
                    break


class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, x, y):
        super().__init__(groups)
        self.original_image = pygame.image.load(
            "images/meteor.png"
        ).convert_alpha()
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = pygame.math.Vector2(
            random.uniform(-0.5, 0.5), 2
        ).normalize()
        self.speed = random.randint(200, 400)
        self.rotation_speed = random.randint(-200, 200)
        self.angle = 0
        self.health = 3

    def update(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

        self.angle += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if (
            self.health <= 0
            or self.rect.top > HEIGHT
            or self.rect.left > WIDTH
            or self.rect.right < 0
        ):
            self.kill()


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, x, y):
        super().__init__(groups)
        self.image = pygame.image.load("images/laser.png").convert_alpha()
        self.rect = self.image.get_rect(bottom=y, centerx=x)
        self.speed = 500

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:
            self.kill()


# --- GAME CLASS ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_started = False
        self.score = 0

        # Assets & UI
        self.font = pygame.font.Font("images/Oxanium-Bold.ttf", 20)
        self.score_font = pygame.font.Font("images/Oxanium-Bold.ttf", 36)
        self.meteor_surf = pygame.image.load(
            "images/meteor.png"
        ).convert_alpha()
        self.init_ui()

        # Groups & Events
        self.all_sprites = pygame.sprite.Group()
        self.laser_group = pygame.sprite.Group()
        self.meteor_group = pygame.sprite.Group()
        self.player = None

        self.METEOR_EVENT = pygame.event.custom_type()
        self.SCORE_EVENT = pygame.event.custom_type()
        pygame.time.set_timer(self.METEOR_EVENT, 400)
        pygame.time.set_timer(self.SCORE_EVENT, 1000)

        self.spawn_stars()

    def init_ui(self):
        btn_text = self.font.render("START GAME", True, WHITE)
        self.btn_surf = pygame.Surface((220, 60))
        self.btn_surf.fill(BTN_COLOR)
        self.btn_surf.blit(btn_text, btn_text.get_rect(center=(110, 30)))
        self.btn_rect = self.btn_surf.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 150)
        )

    def spawn_stars(self):
        for _ in range(20):
            while True:
                star = Star(self.all_sprites)
                if not any(
                    star.rect.colliderect(other.rect)
                    for other in self.all_sprites
                    if isinstance(other, Star) and other != star
                ):
                    break
                star.kill()

    def start_game(self):
        self.game_started = True
        self.score = 0
        for meteor in self.meteor_group:
            meteor.kill()
        self.player = Player(
            self.all_sprites, self.laser_group, WIDTH // 2, HEIGHT // 2
        )

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000
            self.events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_started:
                if (
                    event.button == 1
                    and self.btn_rect.collidepoint(event.pos)
                ):
                    self.start_game()
            elif event.type == self.SCORE_EVENT and self.game_started:
                self.score += 1
            elif event.type == self.METEOR_EVENT and self.game_started:
                x = random.randint(
                    10 + self.meteor_surf.get_width(),
                    WIDTH - self.meteor_surf.get_width() - 10,
                )
                Meteor(
                    (self.all_sprites, self.meteor_group),
                    x,
                    -self.meteor_surf.get_height(),
                )

    def update(self, dt):
        self.all_sprites.update(dt)
        if not self.game_started:
            return

        # Laser collisions
        for meteors in pygame.sprite.groupcollide(
            self.laser_group, self.meteor_group, True, False
        ).values():
            for meteor in meteors:
                meteor.health -= 1

        # Player collisions
        if (
            self.player
            and self.player.alive()
            and not self.player.has_collided
        ):
            if pygame.sprite.spritecollide(
                self.player, self.meteor_group, True, pygame.sprite.collide_mask
            ):
                self.player.health -= 1
                if self.player.health <= 0:
                    self.player.kill()
                    self.game_started = False
                else:
                    self.player.has_collided = True

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.all_sprites.draw(self.screen)

        if not self.game_started:
            self.screen.blit(self.btn_surf, self.btn_rect)
        elif self.player and self.player.alive():
            hp_surf = self.font.render(
                f"Health: {self.player.health}", True, WHITE
            )
            score_surf = self.score_font.render(str(self.score), True, WHITE)
            score_rect = score_surf.get_rect(
                center=(WIDTH // 2, HEIGHT - 90)
            )
            border_rect = score_rect.inflate(40, 20)
            self.screen.blit(hp_surf, (10, 10))
            self.screen.blit(score_surf, score_rect)
            pygame.draw.rect(self.screen, WHITE,
                             border_rect.move(0, -4), 2, 10)

        pygame.display.update()


if __name__ == "__main__":
    Game().run()
