import pygame
import random

pygame.init()
w, h = 800, 600
display_surface = pygame.display.set_mode((w, h))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()

player_surf = pygame.image.load("images/player.png").convert_alpha()
player_rect = player_surf.get_frect(center=(w // 2, h // 2))
player_direction = pygame.math.Vector2(0, 0)
player_speed = 300

star_surf = pygame.image.load("images/star.png").convert_alpha()
star_rects = [star_surf.get_frect(topleft=(random.randint(
    0, w - int(star_surf.get_width())), random.randint(0, h + int(star_surf.get_height()) * 2))) for _ in range(20)]

meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
meteor_rect = meteor_surf.get_frect(center=(w // 2, h // 2))

laser_surf = pygame.image.load("images/laser.png").convert_alpha()
lasers = []
laser_speed = 500
laser_cooldown = 0.3
laser_timer = 0

while running:
    dt = clock.tick(60) / 1000
    laser_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] and player_rect.left > 10:
        player_direction.x -= 1
    if keys[pygame.K_d] and player_rect.right < w - 10:
        player_direction.x += 1
    if keys[pygame.K_w] and player_rect.top > 10:
        player_direction.y -= 1
    if keys[pygame.K_s] and player_rect.bottom < h - 10:
        player_direction.y += 1

    if player_direction.length() > 0:
        player_direction = player_direction.normalize()
    player_rect.x += player_direction.x * player_speed * dt
    player_rect.y += player_direction.y * player_speed * dt

    display_surface.fill("black")

    for rect in star_rects:
        rect.y += 300 * dt
        if rect.y > h + rect.height:
            rect.y = -rect.height
            rect.x = random.randint(0, w - int(rect.width))
        display_surface.blit(star_surf, rect)

    display_surface.blit(player_surf, player_rect)
    display_surface.blit(meteor_surf, meteor_rect)

    if laser_timer >= laser_cooldown:
        laser_rect = laser_surf.get_frect(
            bottom=(player_rect.top - 10), centerx=player_rect.centerx)
        lasers.append(laser_rect)
        laser_timer = 0

    for laser in lasers:
        laser.y -= laser_speed * dt
        display_surface.blit(laser_surf, laser)
        if laser.bottom < 0:
            lasers.remove(laser)

    pygame.display.update()
    player_direction.update(0, 0)


pygame.quit()
