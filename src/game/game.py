import pygame
from enum import Enum
from game.bullet import Bullet, Bullet_View
from network import Network
from game.settings import *
from game.player import Player
from game.tile import Tile

class GameState(Enum):
    NOT_READY = 1
    READY = 2
    PLAYING = 3
    WIN = 4
    LOSE = 5

class Game:
    def __init__(self):
        self.network = Network()
        self.state = GameState.NOT_READY
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.visible_sprites = CameraGroup()
        self.active_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.opponent_bullets = CameraGroup()
        
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
                        self.network.send((self.player.get_stats(), []))
                    else:
                        self.opponent = Player((x,y), [self.visible_sprites, self.collision_sprites], col, self.collision_sprites)
    
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
            self.draw_wait_menu()
        elif self.state == GameState.READY:
            self.visible_sprites.custom_draw(self.player)
            self.opponent_bullets.custom_draw(self.player)
        elif self.state == GameState.WIN:
            self.draw_win_menu()
        elif self.state == GameState.LOSE:
            self.draw_lose_menu()
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