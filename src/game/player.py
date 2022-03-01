from turtle import position
import pygame
from game.settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, type, collision_sprites):
        super().__init__(groups)
        self.import_player_assets()
        self.start_pos = pos
        self.bullets = []
        
        # player sprites
        self.frame_index = 0
        self.animation_speed = 0.1
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # player movement
        self.direction = pygame.math.Vector2()
        self.speed = 7
        self.gravity = 0.8
        self.jump_speed = 16
        self.on_floor = False

        self.collision_sprites = collision_sprites

        # player stats
        self.position = pygame.Vector2(pos)
        self.points = 0
        self.status = 'idle'
        self.facing_right = True

        # player attack
        self.shooting = False
        self.can_shoot = True

    def import_player_assets(self):
        assets_path = "./assets/player/"
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': []}
        
        for animation in self.animations.keys():
            full_path = assets_path + animation
            self.animations[animation] = import_folder(full_path)

    # -- Return values to send to server -- #
    def get_stats(self):
        return (self.position, self.points, self.status, self.facing_right)

    # -- Update values received from server -- #
    def update_stats(self, stats):
        (position, points, status, facing_right) = stats
        self.position = position
        self.points = points
        self.status = status
        self.facing_right = facing_right

        self.change_coords()
        self.animate()

    def get_bullets_info(self):
        bullets_info = []
        for bullet in self.bullets:
            bullets_info.append(bullet.get_info())
        return bullets_info

    # -- Get player animation status -- #
    def get_status(self):
        if self.shooting:
            self.status = 'attack'
        elif self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    # -- Change the position with the final rect coordinates -- #
    def update_final_position(self):
        self.position = self.rect.topleft
    
    # -- Change the rect coordinates with the position received from server -- #
    def change_coords(self):
        self.rect.topleft = self.position

    # -- Update the x coordinates -- #
    def change_horizontal_coords(self):
        self.rect.x += self.direction.x * self.speed

    # -- Update the y coordinates -- #
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y
    
    # -- Receive keyboard input -- #
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.facing_right = False
            self.direction.x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            self.direction.x = 1
        else:
            self.direction.x = 0

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_floor:
            self.direction.y = -self.jump_speed

    # -- Check for horizontal collisions -- #
    def horizontal_collisions(self):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left

    # -- Check for vertical collisions -- #
    def vertical_collisions(self):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.direction.y = 0
                if self.direction.y > 0:
                   self.rect.bottom = sprite.rect.top
                   self.direction.y = 0
                   self.on_floor = True

        if self.on_floor and self.direction.y != 0:
            self.on_floor = False
    
    def out_of_bounds(self):
        if self.rect.y < SCREEN_HEIGHT + 150: return False

        self.points -= 1
        self.rect.topleft = self.start_pos
        self.update_final_position()
        return True

    # -- Animate player sprite -- #
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.shooting: self.shooting = False

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)

    def update(self):
        self.input()
        self.change_horizontal_coords()
        self.horizontal_collisions()
        self.apply_gravity()
        self.vertical_collisions()
        self.update_final_position()
        self.get_status()
        self.animate()
    
    def shoot(self, bullet):
        self.bullets.append(bullet)
        self.can_shoot = False
        self.shooting = True
    
    def reset_shoot(self, bullet):
        self.can_shoot = True
        self.bullets.remove(bullet)
        bullet.kill()
    
    def has_won(self):
        return self.points >= 3