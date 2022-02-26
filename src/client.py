import pygame, sys
from network import Network
from pygame.locals import *
from game.settings import *
from game.player import Player


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Unbreakable pvp")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    #pygame.mouse.set_visible(False)
    
    n = Network()
    player = Player(n.get_player_info())
    player2 = Player(n.send(player.get_info()))

    player_group = pygame.sprite.Group()
    player_group.add(player)
    player_group.add(player2)
    
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Close")
                pygame.quit()
                sys.exit(0)
        
        player2.info = n.send(player.get_info())
        
        # --- Game logic
        player_group.update()
        player.move()

        # --- Drawing code 
        screen.fill(BG_COLOR)
        # game.draw(screen)
        player_group.draw(screen)

        pygame.display.flip()
        clock.tick(60)
 
if __name__ == "__main__":
    main()