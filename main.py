import pygame

from sprites import Player
from sprites import Enemy
from sprites import Level
from sprites import Level_01
from sprites import Platform
from sprites import Bullet
from sprites import Coin

from game import Game
from image_processing import ImageProcessing



# Global constants
#scaling factor
SCALE = 2

im_pr = ImageProcessing()

# Screen dimensions
#get the images dimensions
img_png,img,SCREEN_HEIGHT,SCREEN_WIDTH = im_pr.getImage()

#scaled dimensions of the image
SCREEN_HEIGHT = SCALE*SCREEN_HEIGHT
SCREEN_WIDTH = SCALE*SCREEN_WIDTH

#dimensions of the display window
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 600

#starting player position & world shift thresholds
init_x = 300
init_y = 300

right_thresh = DISPLAY_WIDTH-200
left_thresh = 200
up_thresh = 200
down_thresh = DISPLAY_HEIGHT-150

def main():
    """Image Reading and processing. Will move to separate class in future"""
    #convert to grayscale
    img_gray = im_pr.rgb2gray(img)

    #pass through the sobel filter
    img_sb = im_pr.sobel(img_gray)

    #highlight horizontal platforms
    #img_horiz = im_pr.grayHorizontal(img_sb)

    #get level platforms
    level = im_pr.getPlatforms(img_sb)

    """ Main Program """
    pygame.init()

    # Set the height and width of the screen
    size = [DISPLAY_WIDTH,DISPLAY_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Sobel Game")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    #iniitialize the Game class
    game = Game(level,0,True,(init_x,init_y),(0,0),(SCREEN_HEIGHT,SCREEN_WIDTH),(DISPLAY_HEIGHT,DISPLAY_WIDTH),(right_thresh,left_thresh,up_thresh,down_thresh),SCALE)   #'True' in 3rd field lets a 'blank game' run - i.e. home screen

    # -------- Main Program Loop -----------
    while not done:

        #process events
        done = game.process_events()
        #execute game logic (detect collisions, shift world, etc.)

        game.run_logic()
        #draw the current frame
        game.display_frame(screen)

        # Limit to 60 frames per second
        clock.tick(60)

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()
