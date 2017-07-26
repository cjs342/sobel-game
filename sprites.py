import pygame

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player
        controls. """

    def __init__(self,SCREEN_DIM):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        self.SCREEN_HEIGHT,self.SCREEN_WIDTH = SCREEN_DIM

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
        if self.rect.y >= self.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = self.SCREEN_HEIGHT - self.rect.height

        #decrement j_count to zero to time jump duration
        if self.j_count > 0:
            self.j_count-=1

    def jump(self):
        """ Called when user hits 'jump' button. """
        #impose limit on how long jump can last
        self.j_count=40

        # move down a bit and see if there is a platform below us.
        # Move down 3 pixels to alleviate 'hack' in up/down detection
        self.rect.y += 3
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 3

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= self.SCREEN_HEIGHT:
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

    def __init__(self,init_x,init_y,level,player,health,SCREEN_DIM):
        # Call the parent's constructor
        super().__init__()

        self.SCREEN_HEIGHT,self.SCREEN_WIDTH = SCREEN_DIM

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

        self.health = health
        self.speed = None

    def update(self):
        """Move the enemy"""

        #Gravity
        self.calc_grav()
        #print(self.jumping)

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
            self.j_count = 0

        if self.change_y == 0:
            self.change_y = 1
        elif self.j_count == 0:
            self.change_y += .25

        # See if we are on the ground.
        if self.rect.y >= self.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = self.SCREEN_HEIGHT - self.rect.height

        #decrement j_count to zero to time jump duration
        if self.j_count > 0:
            self.j_count-=1

    def chase(self):
        v=self.speed #enemy velocity
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
        self.rect.y += 3
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 3

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= self.SCREEN_HEIGHT:
            if self.change_y == 0 or self.change_y == 1:  #initial velocity
                self.change_y = -7 #adjust this to change jump height

    def shift(self,shift_x,shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y

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

class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player, level, SCALE,SCREEN_DIM):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.SCREEN_HEIGHT,self.SCREEN_WIDTH = SCREEN_DIM
        self.SCALE = SCALE

        # add platforms to the level
        for platform in level:
            block = Platform(self.SCALE*platform[0], platform[1])
            block.rect.x = self.SCALE*platform[2]
            block.rect.y = self.SCALE*platform[3]
            block.player = self.player
            self.platform_list.add(block)

        #add a block at the bottom of the level
        block = Platform(self.SCREEN_WIDTH,self.SCREEN_HEIGHT)
        block.rect.x = 0
        block.rect.y = self.SCREEN_HEIGHT
        block.player = self.player
        self.platform_list.add(block)
