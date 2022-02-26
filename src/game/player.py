import pygame
from game.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, type):
        super().__init__(groups)
        self.info = PlayerInfo(pos)
        self.vel = 8
        
        self.image = pygame.Surface((TILE_SIZE // 2,TILE_SIZE))
        self.image.fill(PLAYER_COLOR if type == "P" else ENEMY_COLOR)
        self.rect = self.image.get_rect(topleft=self.info.pos)

    def change_pos(self):
        self.rect.x = self.info.pos.x
        self.rect.y = self.info.pos.y

    def get_info(self):
        return self.info

    def update(self):
        info = self.info
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            info.pos.x -= self.vel

        if keys[pygame.K_RIGHT]:
            info.pos.x += self.vel

        if keys[pygame.K_UP]:
            info.pos.y -= self.vel

        if keys[pygame.K_DOWN]:
            info.pos.y += self.vel
        
        self.change_pos()

class PlayerInfo:
    def __init__(self, pos):
        super().__init__()
        self.pos = pygame.Vector2(pos)