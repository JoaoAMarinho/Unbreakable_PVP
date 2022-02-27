import pygame
from game.settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, type, collision_sprites):
        super().__init__(groups)
        self.import_player_assets()
        
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
        self.hp = 3
        self.status = 'idle'
        self.facing_right = True

    def import_player_assets(self):
        assets_path = "./assets/player/"
        self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': [], 'attack': []}
        
        for animation in self.animations.keys():
            full_path = assets_path + animation
            self.animations[animation] = import_folder(full_path)

    def get_position(self):
        return self.position

    # -- Get player animation status -- #
    def get_status(self):
        if self.direction.y < 0:
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
    
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            self.image = pygame.transform.flip(image, True, False)
        
        if self.on_floor:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        else:
            self.rect = self.image.get_rect(center = self.rect.center)

    def update(self):
        self.input()
        self.change_horizontal_coords()
        self.horizontal_collisions()
        self.apply_gravity()
        self.vertical_collisions()
        self.update_final_position()
        self.get_status()
        self.animate()