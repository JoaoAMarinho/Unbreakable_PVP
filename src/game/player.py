import pygame
from game.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, type, collision_sprites):
        super().__init__(groups)
        
        # player sprites
        self.image = pygame.Surface((TILE_SIZE // 2,TILE_SIZE))
        self.image.fill(PLAYER_COLOR if type == "P" else ENEMY_COLOR)
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
        self.hp = 3


    def get_position(self):
        return self.position

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
            self.direction.x = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_floor:
            self.direction.y = -self.jump_speed

    def horizontal_collisions(self):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.direction.x < 0:
                    self.rect.left = sprite.rect.right
                if self.direction.x > 0:
                    self.rect.right = sprite.rect.left

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
    
    def update(self):
        self.input()
        self.change_horizontal_coords()
        self.horizontal_collisions()
        self.apply_gravity()
        self.vertical_collisions()
        self.update_final_position()