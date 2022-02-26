import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, info):
        super().__init__()
        self.info = info
        self.image = pygame.Surface([self.info.width, self.info.height])
        self.image.fill(self.info.color)
        self.rect = self.image.get_rect(topleft=self.info.pos)

    def update(self):
        self.rect.x = self.info.pos.x
        self.rect.y = self.info.pos.y

    def get_info(self):
        return self.info

    def move(self):
        info = self.info
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            info.pos.x -= info.vel

        if keys[pygame.K_RIGHT]:
            info.pos.x += info.vel

        if keys[pygame.K_UP]:
            info.pos.y -= info.vel

        if keys[pygame.K_DOWN]:
            info.pos.y += info.vel
        
        self.update()

class PlayerInfo:
    def __init__(self, width, height, pos, color):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.vel = 8
        self.pos = pygame.Vector2(pos)