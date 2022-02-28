from math import sqrt
import pygame
from game.settings import *
from game.player import Player

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, groups, collision_sprites, offset, target, shooter):
        super().__init__(groups)
        self.image = pygame.Surface((10,10))
        self.image.fill((255,0,0))

        self.config_direction(start_pos-offset, pygame.mouse.get_pos())
        self.rect = self.image.get_rect(center = (start_pos+self.direction*35))

        self.speed = 14
        self.collision_sprites = collision_sprites
        self.target = target
        self.shooter = shooter

    # -- Configure direction vector -- #
    def config_direction(self, p1, p2):
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        size = sqrt(vx**2+vy**2)

        self.direction = pygame.math.Vector2((vx/size,vy/size))

    # -- Change bullet coordinates -- #
    def change_coords(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    # -- Check if bullet is out of bounds -- #
    def out_of_bounds(self):
        window_size = pygame.display.get_window_size()
        
        return (self.rect.x >= window_size[0] + BULLET_LIMIT or self.rect.x <= -BULLET_LIMIT
            or self.rect.y >= window_size[1] + BULLET_LIMIT or self.rect.y <= -BULLET_LIMIT)

    # -- Check for collisions -- #
    def check_collision(self):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if isinstance(sprite, Player):
                    sprite.hp -= 1
                return True
        return False

    # -- Update bullet -- #
    def update(self):
        self.change_coords()
        if self.out_of_bounds() or self.check_collision():
            self.kill()
            self.shooter.can_shoot = True