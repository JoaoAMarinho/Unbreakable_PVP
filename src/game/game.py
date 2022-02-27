import pygame
from network import Network
from game.settings import *
from game.player import Player
from game.tile import Tile

class Game:
    def __init__(self):
        self.network = Network()
        self.ready = False

        # sprite groups
        self.visible_sprites = CameraGroup()
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
                    Tile((x,y), [self.visible_sprites, self.collision_sprites])
                if col == 'P' or col == 'O':
                    if self.network.get_player_info() == col:
                        self.player = Player((x,y), [self.visible_sprites, self.active_sprites], col, self.collision_sprites)
                        self.network.send((self.player.get_position(), self.player.status, self.player.facing_right))
                    else:
                        self.opponent = Player((x,y), [self.visible_sprites, self.collision_sprites], col, self.collision_sprites)
    
    def run(self):
        if not self.ready:
            self.ready = self.network.send("connected")
            return

        self.parse_server_info()
        self.active_sprites.update()
        
    def draw(self):
        if self.ready:
            self.visible_sprites.custom_draw(self.player)
        else:
            # -- draw menu screen (waiting)
            pass

    def parse_server_info(self):
        response = self.network.send((self.player.get_position(), self.player.status, self.player.facing_right))
        self.opponent.position = response[0]
        self.opponent.status = response[1]
        self.opponent.facing_right = response[2]
        self.opponent.change_coords()
        self.opponent.animate()


class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2(100,300)

		# camera rectangle
		cam_left = CAMERA_BORDERS['left']
		cam_top = CAMERA_BORDERS['top']
		cam_width = self.display_surface.get_size()[0] - (cam_left + CAMERA_BORDERS['right'])
		cam_height = self.display_surface.get_size()[1] - (cam_top + CAMERA_BORDERS['bottom'])

		self.camera_rect = pygame.Rect(cam_left,cam_top,cam_width,cam_height)

	def custom_draw(self,player):

		# update camera position
		if player.rect.left < self.camera_rect.left:
			self.camera_rect.left = player.rect.left
		if player.rect.right > self.camera_rect.right:
			self.camera_rect.right = player.rect.right
		if player.rect.top < self.camera_rect.top:
			self.camera_rect.top = player.rect.top
		if player.rect.bottom > self.camera_rect.bottom:
			self.camera_rect.bottom = player.rect.bottom

		# camera offset 
		self.offset = pygame.math.Vector2(
			self.camera_rect.left - CAMERA_BORDERS['left'],
			self.camera_rect.top - CAMERA_BORDERS['top'])

		for sprite in self.sprites():
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)