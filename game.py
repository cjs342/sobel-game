import pygame
import numpy as np
from random import random
from math import floor

from sprites import Player
from sprites import Enemy
from sprites import Level
from sprites import Level_01
from sprites import Platform
from sprites import Bullet
from sprites import Coin

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#from image_processing import ImageProcessing

class Game(object):

    def newCoin(self):
        """generates a new coin on a random platform in the level"""

        #place on random platform
        #NOTE: platform is NOT a Platform object, but a length 4 list containing width,height,x,y created in the getPlatforms function
        platform = self.level[floor(len(self.level)*random())]
        coin = Coin(self.SCALE*(platform[2] + platform[0]*random())+self.current_level.world_shift_x,self.SCALE*(platform[3]-10)+self.current_level.world_shift_y)

        return coin

    def newEnemy(self,health,speed):
        """generates a new enemy on a random platform in the level"""
        platform = self.level[floor(len(self.level)*random())]
        #create new a new Enemy until it is sufficiently far from the player
        while True:
            enemy = Enemy(self.SCALE*(platform[2] + platform[0]*random())+self.current_level.world_shift_x,self.SCALE*(platform[3]-10)+self.current_level.world_shift_y,self.current_level,self.player,health,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH))
            enemy.speed = speed
            p_pos = np.array((self.player.rect.x,self.player.rect.y))
            e_pos = np.array((enemy.rect.x,enemy.rect.y))
            #print(p_pos)
            #print(e_pos)
            if np.linalg.norm(p_pos-e_pos) > 100 and abs(p_pos[0]-e_pos[0]) > 50:
                #print(np.linalg.norm(p_pos-e_pos))
                break

        #print(type(enemy.speed),enemy.speed,speed)
        #print(type(enemy))
        return enemy

    def __init__(self,level,mode,first_game,init_pos,world_shift,SCREEN_DIM,DISPLAY_DIM,thresh,SCALE):

        self.SCREEN_HEIGHT,self.SCREEN_WIDTH = SCREEN_DIM
        self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH = DISPLAY_DIM
        self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh = thresh

        self.SCALE = SCALE

        self.score = 0
        self.game_over = False

        self.level = level

        #self.background_image = pygame.image.load('images/desktop1.png').convert()
        self.background_image = pygame.image.load('images/temp.bmp').convert()
        self.background_image = pygame.transform.scale(self.background_image,(self.SCREEN_WIDTH,self.SCREEN_HEIGHT))
        self.background_position = [world_shift[0], world_shift[1]]

        #Create sprite lists
        self.player = Player((self.SCREEN_HEIGHT,self.SCREEN_WIDTH))

        # Create all the levels
        self.level_list = []
        self.level_list.append( Level_01(self.player, self.level,self.SCALE,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH)) )

        # Set the current level
        self.current_level_no = 0
        self.current_level = self.level_list[self.current_level_no]
        #self.current_level.world_shift_x, self.current_level.world_shift_y = world_shift
        self.current_level.shift_world(world_shift[0],world_shift[1])


        self.active_sprite_list = pygame.sprite.Group()
        #print(type(self.active_sprite_list))
        #print(self.active_sprite_list)
        self.player.level = self.current_level

        init_x,init_y = init_pos

        self.player.rect.x = init_x
        self.player.rect.y = init_y #self.SCREEN_HEIGHT - player.rect.height
        self.active_sprite_list.add(self.player)

        self.mode=mode

        # List of each bullet
        self.bullet_list = pygame.sprite.Group()

        #list of each coin
        self.coin_list = pygame.sprite.Group()
        if mode == 1:
            for i in range(10):
                coin = self.newCoin()
                self.active_sprite_list.add(coin)
                self.coin_list.add(coin)

        #set enemy speed according to game mode
        self.enemy_speed = 3
        if self.mode == 1:
            self.enemy_speed = 3
        elif self.mode == 2:
            self.enemy_speed = 1.5

        #list of each enemy
        self.enemy_list = pygame.sprite.Group()

        if not first_game:
        #enemy = Enemy(300,100,current_level,player)
            enemy = self.newEnemy(20,self.enemy_speed)
            self.enemy_list.add(enemy)
            self.active_sprite_list.add(enemy)

        self.first_game_started = not first_game



    def shiftSpriteList(self,sprite_list,shift_x,shift_y):
        """shifts the sprites in sprite_list by an amount (shift_x,shift_y).
        Matches the world shift that occurs in the Level class"""
        for sprite in sprite_list:
            sprite.shift(shift_x,shift_y)

    def process_events(self):
        #print((self.player.rect.x,self.player.rect.y))
        #print(type(self.level))
        p_pos = (self.player.rect.x,self.player.rect.y)
        w_sh = (self.current_level.world_shift_x,self.current_level.world_shift_y)
        #w_sh = (self.level.world_shift_x,self.level.world_shift_y)
        """processes events such as key strokes, mouse clicks, and quit commands"""
        #print(self.mode)
        for event in pygame.event.get():
            #print(event)
            #if event.type == pygame.MOUSEBUTTONDOWN:

            if event.type == pygame.QUIT:
                return True
            #restart the game is game_over is True and the mouse is clicked
            #if event.type == pygame.MOUSEBUTTONDOWN:
            #    if self.game_over:
            #        self.__init__(self.level,0)

            if event.type == pygame.KEYDOWN:
                #start the game with the specified game mode code
                if not self.first_game_started:
                    if event.key == pygame.K_1:
                        #print("game started")
                        #self.first_game_started = True
                        #self.mode = 1
                        self.__init__(self.level,1,False,p_pos,w_sh,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH),(self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH),(self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh),self.SCALE)

                        #enemy = self.newEnemy(20,self.enemy_speed)
                        #self.enemy_list.add(enemy)
                        #self.active_sprite_list.add(enemy)
                    elif event.key == pygame.K_2:
                        #self.first_game_started = True
                        #self.mode = 2
                        self.__init__(self.level,2,False,p_pos,w_sh,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH),(self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH),(self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh),self.SCALE)

                        #enemy = self.newEnemy(20,self.enemy_speed)
                        #self.enemy_list.add(enemy)
                        #self.active_sprite_list.add(enemy)
                reset_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,\
                            pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]

                if self.game_over:
                    if event.key in reset_keys:
                        self.__init__(self.level,0,True,p_pos,w_sh,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH),(self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH),(self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh),self.SCALE)

                    if event.key == pygame.K_1:
                        self.__init__(self.level,1,False,p_pos,w_sh,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH),(self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH),(self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh),self.SCALE)
                    elif event.key == pygame.K_2:
                        self.__init__(self.level,2,False,p_pos,w_sh,(self.SCREEN_HEIGHT,self.SCREEN_WIDTH),(self.DISPLAY_HEIGHT,self.DISPLAY_WIDTH),(self.right_thresh,self.left_thresh,self.up_thresh,self.down_thresh),self.SCALE)

                #navigate the player using the arrow keys or WASD
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.go_left()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.go_right()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.jump()
                #reset the player's position to the initial position. Used for testing.
                if event.key == pygame.K_r:
                    self.player.reset()
                #create bullet if in game mode 2
                if (event.key == pygame.K_z or event.key == pygame.K_COMMA) and self.mode==2:
                    # Fire a bullet if the user clicks the mouse button
                    bullet = Bullet(-10)
                    # Set the bullet so it is where the player is
                    bullet.rect.x = self.player.rect.x
                    bullet.rect.y = self.player.rect.y + 7
                    # Add the bullet to the lists
                    self.active_sprite_list.add(bullet)
                    self.bullet_list.add(bullet)
                if (event.key == pygame.K_x or event.key == pygame.K_PERIOD) and self.mode ==2:
                    # Fire a bullet if the user clicks the mouse button
                    bullet = Bullet(10)
                    # Set the bullet so it is where the player is
                    bullet.rect.x = self.player.rect.x
                    bullet.rect.y = self.player.rect.y + 7
                    # Add the bullet to the lists
                    self.active_sprite_list.add(bullet)
                    self.bullet_list.add(bullet)

            #stop moving once the key is released
            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.player.change_x < 0:
                    self.player.stop()
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.player.change_x > 0:
                    self.player.stop()
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.player.reset_jump()

        return False    #False indicates not done

    def run_logic(self):
        """Main game logic"""
        #print("run logic")
        #print(self.enemy_list)
        if not self.game_over:
            #generate coins if still in start menu and game mode 1 chosen
            if self.mode == 1 and not self.first_game_started:
                for i in range(10):
                    coin = self.newCoin()
                    self.active_sprite_list.add(coin)
                    self.coin_list.add(coin)

                self.first_game_started = True

            # Update the player.
            self.active_sprite_list.update()

            # Update items in the level
            self.current_level.update()

            # Calculate mechanics for each bullet
            for bullet in self.bullet_list:

                # See if it hit a block
                block_hit_list = pygame.sprite.spritecollide(bullet, self.enemy_list, False)  #True means the collided block in block_list will disappear on collision

                # For each block hit, remove the bullet and add to the score
                for block in block_hit_list:
                    self.bullet_list.remove(bullet)
                    self.active_sprite_list.remove(bullet)
                    block.health -= 10
                    if block.health < 0:
                        #print("enemy killed")
                        self.enemy_list.remove(block)
                        self.active_sprite_list.remove(block)

                        enemy1,enemy2 = self.newEnemy(20+self.score,self.enemy_speed),self.newEnemy(20+self.score,self.enemy_speed)

                        self.enemy_list.add(enemy1)
                        self.enemy_list.add(enemy2)
                        self.active_sprite_list.add(enemy1)
                        self.active_sprite_list.add(enemy2)

                        self.score += 1

                        #xpass

                #    score += 1
                #    print(score)

                # Remove the bullet if it flies up off the screen
                if bullet.rect.x < -10 or bullet.rect.x > self.SCREEN_WIDTH+10:
                    self.bullet_list.remove(bullet)
                    self.active_sprite_list.remove(bullet)

            # Calculate coins collected
            new_en = 2 #spawn an enemy every new_en coins collected
            block_hit_list = pygame.sprite.spritecollide(self.player,self.coin_list,True)
            for block in block_hit_list:
                if self.first_game_started:
                    self.score+=1
                #spawn a new coin for each one collected
                coin = self.newCoin()
                self.coin_list.add(coin)
                self.active_sprite_list.add(coin)

                #spawn a new enemy for every new_en-th coin collected
                if self.score % new_en == 0 and self.first_game_started:
                    enemy = self.newEnemy(20,self.enemy_speed)
                    self.enemy_list.add(enemy)
                    self.active_sprite_list.add(enemy)

            # Detect enemy collision
            #print(len(self.enemy_list))
            block_hit_list = pygame.sprite.spritecollide(self.player,self.enemy_list,False)
            for block in block_hit_list:
                #pass
                self.game_over = True

            # If the player gets near the right side, shift the world left (-x)
            if self.player.rect.right >= self.right_thresh and self.current_level.world_shift_x >= self.DISPLAY_WIDTH - self.SCREEN_WIDTH:#self.right_thresh - self.SCREEN_WIDTH:
                diff = self.player.rect.right - self.right_thresh
                self.player.rect.right = self.right_thresh
                self.current_level.shift_world(-diff,0)
                self.background_position[0]-=diff

                self.shiftSpriteList(self.coin_list,-diff,0)
                self.shiftSpriteList(self.bullet_list,-diff,0)
                self.shiftSpriteList(self.enemy_list,-diff,0)

            # If the player gets near the left side, shift the world right (+x)
            if self.player.rect.left <= self.left_thresh and self.current_level.world_shift_x <= 0:
                diff = self.left_thresh - self.player.rect.left
                self.player.rect.left = self.left_thresh
                self.current_level.shift_world(diff,0)
                self.background_position[0]+=diff

                self.shiftSpriteList(self.coin_list,diff,0)
                self.shiftSpriteList(self.bullet_list,diff,0)
                self.shiftSpriteList(self.enemy_list,diff,0)

            # If the player gets near the top, shift the world down (+y)
            if self.player.rect.top <= self.up_thresh and self.current_level.world_shift_y <= 0:
                diff = self.up_thresh - self.player.rect.top
                self.player.rect.top = self.up_thresh
                self.current_level.shift_world(0,diff)
                self.background_position[1]+=diff

                self.shiftSpriteList(self.coin_list,0,diff)
                self.shiftSpriteList(self.bullet_list,0,diff)
                self.shiftSpriteList(self.enemy_list,0,diff)

            # If the player gets near the bottom, shift the world up (-y)
            if self.player.rect.bottom >= self.down_thresh and self.current_level.world_shift_y >= self.DISPLAY_HEIGHT-self.SCREEN_HEIGHT:#self.down_thresh - self.SCREEN_HEIGHT:
                diff = self.player.rect.bottom - self.down_thresh
                self.player.rect.bottom = self.down_thresh
                self.current_level.shift_world(0,-diff)
                self.background_position[1]-=diff

                self.shiftSpriteList(self.coin_list,0,-diff)
                self.shiftSpriteList(self.bullet_list,0,-diff)
                self.shiftSpriteList(self.enemy_list,0,-diff)

    def display_frame(self,screen):
        """draw the current frame to the screen"""

        #game over screen
        if self.game_over:
            font = pygame.font.Font(None,75)
            text1 = font.render("Game Over", True, BLACK)
            center_x1 = (self.DISPLAY_WIDTH // 2) - (text1.get_width() // 2)
            #center_y = self.DISPLAY_HEIGHT // 3

            text2 = font.render("Press 1 for Mode 1", True, BLACK)
            center_x2 = (self.DISPLAY_WIDTH // 2) - (text2.get_width() // 2)

            text3 = font.render("Press 2 for Mode 2", True, BLACK)
            center_x3 = (self.DISPLAY_WIDTH // 2) - (text3.get_width() // 2)

            center_y = (self.DISPLAY_HEIGHT // 2) - ((text1.get_height() + text2.get_height() + text3.get_height()) // 2) - 50

            screen.blit(text1, [center_x1,center_y])#[center_x, center_y])
            screen.blit(text2, [center_x2, center_y + text1.get_height() + 20])
            screen.blit(text3, [center_x3, center_y + text1.get_height() + text2.get_height() +40])

        #normal game screen
        else:
            screen.blit(self.background_image, self.background_position)
            self.current_level.draw(screen)
            self.active_sprite_list.draw(screen)

            font = pygame.font.Font(None, 50)
            output_str = 'Score: ' + str(self.score)
            text = font.render(output_str, True, BLACK)
            screen.blit(text, [50,550])

            font = pygame.font.Font(None,50)
            output_str = 'Enemies: ' + str(len(self.enemy_list))
            text = font.render(output_str, True, BLACK)
            screen.blit(text, [self.DISPLAY_WIDTH - text.get_width() - 50, 550])

        if not self.first_game_started:
            #print("game menu")
            font = pygame.font.Font(None,75)
            text1 = font.render("Sobel Game", True, BLACK)
            center_x1 = (self.DISPLAY_WIDTH // 2) - (text1.get_width() // 2)
            #center_y = self.DISPLAY_HEIGHT // 3

            text2 = font.render("Press 1 for Mode 1", True, BLACK)
            center_x2 = (self.DISPLAY_WIDTH // 2) - (text2.get_width() // 2)

            text3 = font.render("Press 2 for Mode 2", True, BLACK)
            center_x3 = (self.DISPLAY_WIDTH // 2) - (text3.get_width() // 2)

            center_y = (self.DISPLAY_HEIGHT // 2) - ((text1.get_height() + text2.get_height() + text3.get_height()) // 2) - 50

            screen.blit(text1, [center_x1,center_y])#[center_x, center_y])
            screen.blit(text2, [center_x2, center_y + text1.get_height() + 20])
            screen.blit(text3, [center_x3, center_y + text1.get_height() + text2.get_height() +40])

        pygame.display.flip()
