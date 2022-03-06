from math import pi, sqrt, acos
import pygame
from game.settings import *
from game.player import Player
from support import import_folder


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, groups, collision_sprites, offset, target, shooter):
        super().__init__(groups)
        self.import_bullet_assets()

        self.config_direction(start_pos-offset, pygame.mouse.get_pos())

        # bullet animation
        self.status = 'move'
        self.frame_index = 0
        self.animation_speed = 0.25

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = (start_pos+self.direction*35))

        self.speed = 14
        self.collision_sprites = collision_sprites
        self.target = target
        self.shooter = shooter
        self.hit = False

    # -- Configure direction vector -- #
    def config_direction(self, p1, p2):
        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        size = sqrt(vx**2+vy**2)

        self.direction = pygame.math.Vector2((vx/size,vy/size))
        
        self.angle = acos(self.direction.x) * 180 / pi
        if p2[1] > p1[1]: self.angle = -self.angle

    # -- Import animation assests -- #
    def import_bullet_assets(self):
        assets_path = "./assets/bullet/"
        self.animations = {'move': [], 'hit': []}
        
        for animation in self.animations.keys():
            full_path = assets_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_info(self):
        return (self.rect.center, self.status, self.frame_index, self.angle)

    # -- Change bullet coordinates -- #
    def change_coords(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    # -- Check if bullet is out of bounds -- #
    def out_of_bounds(self):
        x_limit = self.shooter.position[0] + SCREEN_WIDTH/3 + BULLET_LIMIT
        return (self.rect.x >= x_limit or self.rect.x <= -BULLET_LIMIT
            or self.rect.y >= SCREEN_HEIGHT + BULLET_LIMIT or self.rect.y <= -BULLET_LIMIT)

    # -- Check for collisions -- #
    def check_collision(self):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if isinstance(sprite, Player):
                    self.shooter.points += 1
                return True
        return False

    # -- Animate bullet sprite -- #
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.hit: self.shooter.reset_shoot(self)

        image = animation[int(self.frame_index)]
        self.image = pygame.transform.rotate(image, self.angle)
        
    # -- Update bullet -- #
    def update(self):
        self.animate()
        if self.hit: return
        self.change_coords()
        if self.out_of_bounds():
            self.shooter.reset_shoot(self)
        elif self.check_collision():
            self.status = 'hit'
            self.hit = True

class Bullet_View(pygame.sprite.Sprite):
    def __init__(self, groups, info):
        super().__init__(groups)
        self.import_bullet_assets()

        (position, status, frame_index, angle) = info

        image = self.animations[status][int(frame_index)]
        self.image = pygame.transform.rotate(image, angle)
        self.rect = self.image.get_rect(center = position)
    
    def import_bullet_assets(self):
        assets_path = "./assets/bullet/"
        self.animations = {'move': [], 'hit': []}
        
        for animation in self.animations.keys():
            full_path = assets_path + animation
            self.animations[animation] = import_folder(full_path)