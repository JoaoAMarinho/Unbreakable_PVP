import pygame
from enum import Enum
from game.bullet import Bullet, Bullet_View
from network import Network
from game.settings import *
from game.player import Player
from game.tile import Tile
from support import import_csv_layout, import_cut_graphics

class GameState(Enum):
    NOT_READY = 1
    READY = 2
    WIN = 3
    LOSE = 4

class Game:
    def __init__(self, map_data):
        self.network = Network()
        self.menu_drawer = MenuDrawer()
        self.state = GameState.NOT_READY
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.opponent_bullets = CameraGroup()
        
        # map setup
        self.setup_map(map_data)

    def setup_map(self, map_data):
        
        # players setup
        players_layout = import_csv_layout(map_data['players']) 
        self.create_tile_group(players_layout, 'players')

        # terrain setup
        terrain_layout = import_csv_layout(map_data['terrain'])
        self.create_tile_group(terrain_layout, 'terrain')
    
    def create_tile_group(self, layout, type):

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val == '-1': 
                    continue
                
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if type == 'terrain':
                    terrain_tile_list = import_cut_graphics('./graphics/terrain/terrain_tiles.png')
                    tile_surface = terrain_tile_list[int(val)]
                    Tile((x,y), tile_surface, [self.visible_sprites, self.collision_sprites])

                if type == 'players':
                    if self.network.get_player_info() == int(val):
                        self.player = Player((x,y), [self.visible_sprites, self.active_sprites], val, self.collision_sprites)
                        self.network.send((self.player.get_stats(), []))
                    else:
                        self.opponent = Player((x,y), [self.visible_sprites, self.collision_sprites], val, self.collision_sprites)
    
    def run(self):
        if self.state == GameState.NOT_READY:
            if self.network.send("connected"):
                self.state = GameState.READY
            return
        elif self.state == GameState.READY:
            self.active_sprites.update()
            if self.player.out_of_bounds(): self.visible_sprites.reset_camera()
            self.send_game_info()
            self.check_is_over()
        
    def draw(self):
        if self.state == GameState.NOT_READY:
            self.menu_drawer.draw_wait_menu()
        elif self.state == GameState.READY:
            self.visible_sprites.custom_draw(self.player)
            self.opponent_bullets.custom_draw(self.player)
            self.menu_drawer.draw_scores(self.player.points, self.opponent.points)
        elif self.state == GameState.WIN:
            self.menu_drawer.draw_win_menu()
        elif self.state == GameState.LOSE:
            self.menu_drawer.draw_lose_menu()
        else:
            # -- draw other menus
            pass
    
    def check_is_over(self):
        if self.player.has_won():
            self.state = GameState.WIN
            return True
        if self.opponent.has_won():
            self.state = GameState.LOSE
            return True

        return False
    
    def send_game_info(self):
        self.opponent_bullets.empty()

        (opponent_stats, bullets_info) = self.network.send((self.player.get_stats(), self.player.get_bullets_info()))
        self.opponent.update_stats(opponent_stats)

        for info in bullets_info:
            Bullet_View(self.opponent_bullets, info)

    def click_event(self):
        if self.state == GameState.NOT_READY: return
        
        if self.state == GameState.READY: 
            self.shoot()
        
    def shoot(self):
        if not self.player.can_shoot:
            return
        self.player.shoot(Bullet(self.player.rect.center, [self.visible_sprites, self.active_sprites], self.collision_sprites, self.visible_sprites.offset, self.opponent, self.player))


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2(100,300)

        # camera rectangle
        cam_left = CAMERA_BORDERS['left']
        cam_top = CAMERA_BORDERS['top']
        cam_width = SCREEN_WIDTH - (cam_left + CAMERA_BORDERS['right'])
        cam_height = SCREEN_HEIGHT - (cam_top + CAMERA_BORDERS['bottom'])

        self.camera_rect = pygame.Rect(cam_left,cam_top,cam_width,cam_height)
    
    def reset_camera(self):
        cam_left = CAMERA_BORDERS['left']
        cam_top = CAMERA_BORDERS['top']
        cam_width = SCREEN_WIDTH - (cam_left + CAMERA_BORDERS['right'])
        cam_height = SCREEN_HEIGHT - (cam_top + CAMERA_BORDERS['bottom'])

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

class MenuDrawer():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

    def draw_wait_menu(self):
        font = pygame.font.Font('./assets/Katracy.ttf', 40)
        text = font.render("WAITING FOR A MATCH!", True, (99, 181, 181))
        self.display_surface.blit(text, (SCREEN_WIDTH/2-text.get_size()[0]/2, SCREEN_HEIGHT/2))

    def draw_win_menu(self):
        font = pygame.font.Font('./assets/Katracy.ttf', 40)
        text = font.render("YOU WON! :)", True, (99, 181, 181))
        self.display_surface.blit(text, (SCREEN_WIDTH/2-text.get_size()[0]/2, SCREEN_HEIGHT/2))
    
    def draw_lose_menu(self):
        font = pygame.font.Font('./assets/Katracy.ttf', 40)
        text = font.render("YOU LOST! :(", True, (99, 181, 181))
        self.display_surface.blit(text, (SCREEN_WIDTH/2-text.get_size()[0]/2, SCREEN_HEIGHT/2))
    
    def draw_scores(self, s1, s2):
        font = pygame.font.Font('./assets/Katracy.ttf', 30)
        my_points = font.render("My Points: {}".format(s1), True, (99, 181, 181))
        opponent_points = font.render("Opponent Points: {}".format(s2), True, (99, 181, 181))
        self.display_surface.blit(my_points, (SCREEN_WIDTH/12, SCREEN_HEIGHT/9))
        self.display_surface.blit(opponent_points, (SCREEN_WIDTH*11/12-opponent_points.get_size()[0], SCREEN_HEIGHT/9))


    