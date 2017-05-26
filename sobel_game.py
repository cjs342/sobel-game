"""
The template for this program and basic game functionality comes from the
"Program Arcade Games" series by Prof. Craven at Simpson College

Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/

More advanced game mechanics and image manipulation by Cameron Schultz

"""

import pygame
import numpy as np
import scipy as sp
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from random import random
from math import floor


def getImage():
    """read an image, crop it, and return it along with its dimensions
    in the future, this method will take a screenshot and read that image in"""
    img = mpimg.imread('images/desktop1.png')
    rows,cols,color = img.shape

    return img,rows,cols

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#scaling factor
SCALE = 2

# Screen dimensions
#get the images dimensions
img,SCREEN_HEIGHT,SCREEN_WIDTH = getImage()

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

class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player
        controls. """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        width = 18
        height = 27
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

        #set timer for jumping down
        self.j_count = 0

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move up/down
        if self.change_y != 0:
            self.rect.y += self.change_y
        key = pygame.key.get_pressed()
        #Detect collisions if UP/DOWN keys not pressed and we aren't moving up
        if not (key[pygame.K_DOWN] or key[pygame.K_s]) and not (key[pygame.K_UP] or key[pygame.K_w]) and self.change_y>=0:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            for block in block_hit_list:
                # Reset our position based on the top/bottom of the object.
                if self.change_y >= 0:
                    self.rect.bottom = block.rect.top

                # Stop our vertical movement if hitting a platform from the top
                if self.change_y >= 0:
                    self.change_y = 0

        # Move left/right
        if self.change_x != 0:
            self.rect.x += self.change_x

        #Detect collisions if UP/DOWN keys not pressed and we aren't moving up
        """
        if not key[pygame.K_DOWN] and not key[pygame.K_UP] and self.change_y>=0:
            block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            for block in block_hit_list:
                # If we are moving right,
                # set our right side to the left side of the item we hit
                if self.change_x > 0:
                    self.rect.right = block.rect.left
                elif self.change_x < 0:
                    # Otherwise if we are moving left, do the opposite.
                    self.rect.left = block.rect.right
         """
    def calc_grav(self):
        """ Calculate effect of gravity. """
        key=pygame.key.get_pressed()
        #start moving down if at the top of arc
        if self.change_y == 0:
            self.change_y = 1
        #if DOWN pressed, accelerate downward
        elif (key[pygame.K_DOWN] or key[pygame.K_s]):
            self.change_y = 10
        #if not jumping, accelerate with gravity
        elif not (key[pygame.K_UP] or key[pygame.K_w]) or self.j_count == 0:
            self.change_y += .25

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

        #decrement j_count to zero to time jump duration
        if self.j_count > 0:
            self.j_count-=1

    def jump(self):
        """ Called when user hits 'jump' button. """
        #impose limit on how long jump can last
        self.j_count=40

        # move down a bit and see if there is a platform below us.
        # Move down 3 pixels to alleviate 'hack' in up/down detection
        #FIX THIS
        self.rect.y += 3
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 3

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            if self.change_y == 0:  #initial velocity
                self.change_y = -7 #adjust this to change jump height

    def reset_jump(self):
        self.j_count = 0

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

    def reset(self):
        """Called when user hits the 'R' key """
        self.rect.x = init_x
        self.rect.y = init_y

class Enemy(pygame.sprite.Sprite):
    """"Represents an enemy"""

    def __init__(self,init_x,init_y,level,player):
        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        width = 18
        height = 27
        self.image = pygame.Surface([width, height])
        self.image.fill(BLUE)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        self.rect.x = init_x
        self.rect.y = init_y

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        self.level = level
        self.player = player

        self.j_count = 0
        self.jumping = False

    def update(self):
        """Move the enemy"""

        #Gravity
        self.calc_grav()
        print(self.jumping)

        #Chase direction
        self.chase()

        #move left/right
        if self.change_x != 0:
            self.rect.x += self.change_x

        #move up/down
        if self.change_y != 0:
            self.rect.y += self.change_y

        #detect vertical collisions (platforms)
        block_hit_list = pygame.sprite.spritecollide(self,self.level.platform_list, False)
        #if the enemy is touching a platform, it cannot be jumping
        if len(block_hit_list) > 0 and self.change_y >= 0:
            self.jumping = False

        diff_y = self.rect.y - self.player.rect.y   #difference in y position (pos = player higher)
        #detect collisions only if player is not below enemy (i.e. enemy drops down)
        if diff_y >= 0:
            for block in block_hit_list:
                # Reset our position based on the top/bottom of the object.
                    if self.change_y >= 0:
                        self.rect.bottom = block.rect.top

                    # Stop our vertical movement if hitting a platform from the top
                    if self.change_y >= 0:
                        self.change_y = 0

    def calc_grav(self):
        """ Calculate effect of gravity. """
        diff_y = self.player.rect.y - self.rect.y #difference in position
        #if close to player vertically, end jump
        if abs(diff_y) < 10:
            #self.jumping = False
            self.j_count = 0

        if self.change_y == 0:
            self.change_y = 1
        #elif not self.jumping or self.j_count == 0: #abs(diff_y) < 10 or self.j_count == 0:
        elif self.j_count == 0:
            self.change_y += .25

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

        #decrement j_count to zero to time jump duration
        if self.j_count > 0:
            self.j_count-=1

    def chase(self):
        v=3 #enemy velocity
        diff_x = self.player.rect.x - self.rect.x   #difference in x position (pos = palyer to right)
        diff_y = self.rect.y - self.player.rect.y   #difference in y position (pos = player higher)

        #only move l/r if not jumping
        if not self.jumping:
            if diff_x>= v:
                self.change_x = v
            #set speed equal to difference in position to avoid graphical jumping
            elif diff_x > 0:
                self.change_x = diff_x
            elif diff_x <= -v:
                self.change_x = -v
            elif diff_x < 0:
                self.change_x = diff_x
            else:
                self.change_x = 0

        #determine whether or not to jump
        if diff_y > 10 and not self.jumping:#self.j_count==0:
            self.jump()



    def jump(self):
        """ Called when chase() decides to jump.
        Sets the launch velocity for the jump and resets the jump duration.
        Calculation for jump duration is done in calc_grav()"""
        #impose limit on how long jump can last
        self.j_count=40
        self.jumping = True

        # move down a bit and see if there is a platform below us.
        # Move down 3 pixels to alleviate 'hack' in up/down detection
        #FIX THIS

        self.rect.y += 3
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 3

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            if self.change_y == 0 or self.change_y == 1:  #initial velocity
                self.change_y = -7 #adjust this to change jump height


    def shift(self,shift_x,shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y



class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()

class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet . """
    def __init__(self,v):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = pygame.Surface([10, 4])
        self.image.fill(BLACK)
        self.v = v

        self.rect = self.image.get_rect()

    def update(self):
        """ Move the bullet. """
        self.rect.x += self.v

    def shift(self,shift_x,shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y

class Coin(pygame.sprite.Sprite):
    """This class represents a collectible coin"""
    def __init__(self,x,y):
        #Call the parent class (Sprite) constructor
        super().__init__()

        self.image = pygame.Surface([10,10])
        self.image.fill(YELLOW)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shift(self,shift_x,shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y


class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        # Background image
        self.background = None

        self.world_shift_x=0
        self.world_shift_y=0

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)

    def shift_world(self, shift_x, shift_y):
        self.world_shift_x += shift_x
        self.world_shift_y += shift_y

        for platform in self.platform_list:
            platform.rect.x += shift_x
            platform.rect.y += shift_y


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player, level):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        # add platforms to the level
        for platform in level:
            block = Platform(SCALE*platform[0], platform[1])
            block.rect.x = SCALE*platform[2]
            block.rect.y = SCALE*platform[3]
            block.player = self.player
            self.platform_list.add(block)

        #add a block at the bottom of the level
        block = Platform(SCREEN_WIDTH,SCREEN_HEIGHT)
        block.rect.x = 0
        block.rect.y = SCREEN_HEIGHT
        block.player = self.player
        self.platform_list.add(block)


def rgb2gray(rgb):
    """converts an RGB image to grayscale using the luma coding formula:
    Y = 0.299R + 0.587G + 0.114B"""
    return np.dot(rgb[...,:3], [0.299,0.587,0.114])


def sobel(img):
    """apply the Sobel filter to detect edges (grayscale only)"""
    if len(img.shape)>2:
        raise ValueError('arg must be 2 dimensional (grayscale)')
        return
    #get img dimensions
    rows,cols = img.shape

    c=4 #Sobel coefficient

    #create new blank image of same size
    sb = np.zeros((rows,cols))

    #iterate over img, one pixel in from edge
    for i in range(1,rows-1):
        for j in range(1,cols-1):
            sx = 0#(img[i-1][j+1] + c*img[i][j+1] + img[i+1][j+1]) - (img[i-1][j-1] + c*img[i][j-1] + img[i+1][j-1])
            sy = (img[i-1][j-1] + c*img[i-1][j] + img[i-1][j+1]) - (img[i+1][j-1] + c*img[i+1][j] + img[i+1][j+1])
            m = (sx**2 + sy**2)**(1/2)

            sb[i][j]=m/6

    return sb


def grayHorizontal(img):
    """colors the horizontal lines in an image white and blacks the rest
    input 2-D array"""
    rows,cols=img.shape
    img_horiz=np.zeros(img.shape)
    for row in range(rows):
        for i in range(cols-100):
            x=img[row][i]
            x_1=img[row][i+1]
            count=1
            while x>0.1 and x==x_1 and count<100:
                count+=1
                x=x_1
                x_1 = img[row][i+count]
            #color line white if same color detected for 100 pixels
            if count==100:
                i+=1
                for j in range(100):
                    img_horiz[row][i+j]=1

    return img_horiz

def getPlatforms(img):
    """returns a list of platforms (defined by width, height, x, y) given a b/w image
    platforms are created wherever whitespace is detected. used with the output of grayHorizontal method"""
    rows,cols = img.shape
    #print(rows,cols)
    platforms = []
    for r in range(rows):
        for c in range(cols):
            #detect a white pixel
            if img[r][c] == 1:
                img[r][c] = 0   #each time a white pixel is visited, set it to black so it is not double counted
                rp = r+1
                cp=c+1
                #get height by counting the subsequent rows (same col) that are also white
                while rp < rows and img[rp][c] == 1:
                    img[rp][c] = 0
                    rp+=1
                #get widtch by counting the subsequent cols (same row) that are also white
                while cp < cols and img[r][cp] == 1:
                    img[r][cp] = 0
                    cp+=1
                #color all the remaining white pixels in the platform white using the width and height
                for i in range(1,rp-r):
                    for j in range(1,cp-c):
                        img[r+i][c+j] = 0

                #width, height, x, y
                platforms.append([cp-c,rp-r,c,r])

    return platforms

def shiftSpriteList(sprite_list,shift_x,shift_y):
    for sprite in sprite_list:
        sprite.shift(shift_x,shift_y)

def newCoin(level, current_level):
    """generates n new coins randomly distributed across platforms in level"""
    #create n Coins
    #for i in range(n):
        #place on random platform
    #NOTE: platform is NOT a Platform object, but a length 4 list containing width,height,x,y created in the getPlatforms function
    platform = level[floor(len(level)*random())]
    coin = Coin(SCALE*(platform[2] + platform[0]*random())+current_level.world_shift_x,SCALE*(platform[3]-10)+current_level.world_shift_y)

    return coin

def newEnemy(level,current_level,player):
    platform = level[floor(len(level)*random())]
    enemy = Enemy(SCALE*(platform[2] + platform[0]*random())+current_level.world_shift_x,SCALE*(platform[3]-10)+current_level.world_shift_y,current_level,player)

    return enemy

def main():
    """Image Reading and processing"""
    #image is read before global variables are declared since they depend on the image

    #convert to grayscale
    img_gray = rgb2gray(img)

    #pass through the sobel filter
    img_sb = sobel(img_gray)

    #highlight horizontal platforms
    img_horiz = grayHorizontal(img_sb)

    #get level platforms
    level = getPlatforms(img_horiz)

    """ Main Program """
    pygame.init()

    # Set the height and width of the screen
    size = [DISPLAY_WIDTH,DISPLAY_HEIGHT]#[SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Platformer Jumper")

    #set background image and position
    background_image = pygame.image.load('images/desktop1.png').convert()
    background_image = pygame.transform.scale(background_image,(SCREEN_WIDTH,SCREEN_HEIGHT))
    background_position = [0, 0]

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append( Level_01(player, level) )

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]


    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = init_x
    player.rect.y = init_y #SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    # List of each bullet
    bullet_list = pygame.sprite.Group()

    #list of each coin
    coin_list = pygame.sprite.Group()
    for i in range(10):
        coin = newCoin(level, current_level)
        active_sprite_list.add(coin)
        coin_list.add(coin)

    #list of each enemy
    enemy_list = pygame.sprite.Group()
    #enemy = Enemy(300,100,current_level,player)
    enemy = newEnemy(level,current_level,player)
    enemy_list.add(enemy)
    active_sprite_list.add(enemy)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Score. increments for each Coin collected
    score = 0

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.go_left()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.go_right()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.jump()
                if event.key == pygame.K_r:
                    player.reset()
                if event.key == pygame.K_z or event.key == pygame.K_COMMA:
                    # Fire a bullet if the user clicks the mouse button
                    bullet = Bullet(-10)
                    # Set the bullet so it is where the player is
                    bullet.rect.x = player.rect.x
                    bullet.rect.y = player.rect.y
                    # Add the bullet to the lists
                    active_sprite_list.add(bullet)
                    bullet_list.add(bullet)
                if event.key == pygame.K_x or event.key == pygame.K_PERIOD:
                    # Fire a bullet if the user clicks the mouse button
                    bullet = Bullet(10)
                    # Set the bullet so it is where the player is
                    bullet.rect.x = player.rect.x
                    bullet.rect.y = player.rect.y
                    # Add the bullet to the lists
                    active_sprite_list.add(bullet)
                    bullet_list.add(bullet)

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and player.change_x < 0:
                    player.stop()
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and player.change_x > 0:
                    player.stop()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.reset_jump()

        #copy the background image to screen
        screen.blit(background_image, background_position)

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # Calculate mechanics for each bullet
        for bullet in bullet_list:

            # See if it hit a block
            #block_hit_list = pygame.sprite.spritecollide(bullet, block_list, True)  #True means the collided block in block_list will disappear on collision

            # For each block hit, remove the bullet and add to the score
            #for block in block_hit_list:
            #    bullet_list.remove(bullet)
            #    all_sprites_list.remove(bullet)
            #    score += 1
            #    print(score)

            # Remove the bullet if it flies up off the screen
            if bullet.rect.x < -10 or bullet.rect.x > SCREEN_WIDTH+10:
                bullet_list.remove(bullet)
                active_sprite_list.remove(bullet)

        # Calculate coins collected
        new_en = 2 #spawn an enemy every new_en coins collected
        block_hit_list = pygame.sprite.spritecollide(player,coin_list,True)
        for block in block_hit_list:
            #spawn a new coin for each one collected
            coin = newCoin(level,current_level)
            coin_list.add(coin)
            active_sprite_list.add(coin)

            #spawn a new enemy for every new_en-th coin collected
            if score % new_en == 0:
                enemy = newEnemy(level,current_level,player)
                enemy_list.add(enemy)
                active_sprite_list.add(enemy)

            score+=1

        # Detect enemy collision
        block_hit_list = pygame.sprite.spritecollide(player,enemy_list,False)
        for block in block_hit_list:
            pass
            #done = True
            #score-=1

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= right_thresh and current_level.world_shift_x >= DISPLAY_WIDTH - SCREEN_WIDTH:#right_thresh - SCREEN_WIDTH:
            diff = player.rect.right - right_thresh
            player.rect.right = right_thresh
            current_level.shift_world(-diff,0)
            background_position[0]-=diff

            shiftSpriteList(coin_list,-diff,0)
            shiftSpriteList(bullet_list,-diff,0)
            shiftSpriteList(enemy_list,-diff,0)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= left_thresh and current_level.world_shift_x <= 0:
            diff = left_thresh - player.rect.left
            player.rect.left = left_thresh
            current_level.shift_world(diff,0)
            background_position[0]+=diff

            shiftSpriteList(coin_list,diff,0)
            shiftSpriteList(bullet_list,diff,0)
            shiftSpriteList(enemy_list,diff,0)

        # If the player gets near the top, shift the world down (+y)
        if player.rect.top <= up_thresh and current_level.world_shift_y <= 0:
            diff = up_thresh - player.rect.top
            player.rect.top = up_thresh
            current_level.shift_world(0,diff)
            background_position[1]+=diff

            shiftSpriteList(coin_list,0,diff)
            shiftSpriteList(bullet_list,0,diff)
            shiftSpriteList(enemy_list,0,diff)

        # If the player gets near the bottom, shift the world up (-y)
        if player.rect.bottom >= down_thresh and current_level.world_shift_y >= DISPLAY_HEIGHT-SCREEN_HEIGHT:#down_thresh - SCREEN_HEIGHT:
            diff = player.rect.bottom - down_thresh
            player.rect.bottom = down_thresh
            current_level.shift_world(0,-diff)
            background_position[1]-=diff

            shiftSpriteList(coin_list,0,-diff)
            shiftSpriteList(bullet_list,0,-diff)
            shiftSpriteList(enemy_list,0,-diff)


        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        #debugging
        font = pygame.font.Font(None, 50)
        output_str = 'Score: ' + str(score)
        text = font.render(output_str, True, BLACK)
        screen.blit(text, [50,550])

        if done:
            font = pygame.font.Font(None,100)
            output_str = 'GAME OVER'
            text = font.render(output_str, True, BLACK)
            screen.blit(text, [200,200])

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()


    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()
