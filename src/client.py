import pygame, sys
from pygame.locals import *
from game.settings import *
from game.game import Game


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Unbreakable pvp")
    
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    
    game = Game()
    
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Close")
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                game.click_event()
        
        # --- Game logic
        game.run()

        # --- Drawing code 
        screen.fill(BG_COLOR)
        game.draw()

        pygame.display.flip()
        clock.tick(60)
 
if __name__ == "__main__":
    main()