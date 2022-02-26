import pygame
from network import Network
from game.settings import *
from game.player import Player
from game.tile import Tile

class Game:
    def __init__(self):
        self.network = Network()
        self.ready = False
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.visible_sprites = pygame.sprite.Group()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        
        # arena setup
        self.setup_arena(ARENA_1)

    def setup_arena(self, arena):
        for row_index,row in enumerate(arena):
            for col_index,col in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if col == 'X':
                    Tile((x,y), [self.visible_sprites])
                if col == 'P' or col == 'O':
                    if self.network.get_player_info() == col:
                        self.player = Player((x,y), [self.visible_sprites, self.active_sprites], col)
                        self.network.send(self.player.get_info())
                    else:
                        self.opponent = Player((x,y), [self.visible_sprites], col)
        
    def run(self):
        if self.ready:
            self.receive_server_info()
            self.active_sprites.update()
            return
        
        self.ready = self.network.send("connected")

    def draw(self):
        if self.ready:
            self.visible_sprites.draw(self.display_surface)
        else:
            # -- draw menu screen (waiting)
            pass

    def receive_server_info(self):
        self.opponent.info = self.network.send(self.player.get_info())
        self.opponent.change_pos()
