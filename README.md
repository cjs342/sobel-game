# Sobel Game

Arcade game that takes an image and creates platforms from the horizontal edges.

## Background

This project was developed as a purely for fun exercise in Python programming. Before this project, much of my programming experience had been limited to basic scripting and data manipulation. Sobel Game was my first attempt at a somewhat complex application with many moving parts spread across a handful of files.

The name "Sobel Game" is taken from the [Sobel edge-detection filter](https://en.wikipedia.org/wiki/Sobel_operator) used to create the playable map: 
  
Much of the backbone of the code was taken from Dr. Paul Craven's [website](http://programarcadegames.com/index.php), used primarily to supplement his introduction to programming course as Simpson College.

## Descriptions and Development

### main.py

This file initializes globals, contains the function that runs the game (main()), and executes it. Running this file will start a new game instance.

Earlier in the project's life, ALL of the running logic and class definitions below were contained in this file. This sufficed when the project was limited in scope to a simple side-scroller, (template code taken from [Dr. Craven](http://programarcadegames.com/python_examples/f.php?file=platform_scroller.py)) but as more features were added and the game grew more complex, it was clear that everything needed to be reorganized.

### image_processing.py

This file contains the four functions that process an image to generate the level. They are: getImage(), rgb2gray(), sobel(), and getPlatforms().

#### getImage()

Takes a screenshot, saves a temporary files, and reads it in.

#### rgb2gray()

Converts an rgb image to grayscale.

#### sobel()

Passes a grayscale image through the Sobel edge-detection filter. As the image is traversed, looks for consecutive runs of 100 same-colored pixels after Sobel filtering and colors them white. These will become the platforms for the level.

The variable *plat* stores the length of the run of identical pixels that will be detected and turned into a platform. By tuning the variable *gap*, image processing can be altered to only evaluate every *gap-th* pixel, saving a significant amount of time. The following table for *plat* = 100 compares runtimes and number of platforms detected on a sample screenshot. In practice, even a lower number of detected platforms is more than enough to create a playable level.

| *gap* | sobel() processing time (s) | # platforms detected|
|-------|-----------------------------|---------------------|
| 1     | 8.68                        | 207                 |
| 2     | 4.26                        | 186                 |
| 4     | 2.25                        | 175                 |
| 5     | 1.83                        | 175                 |
| 10    | 0.94                        | 149                 |
| 20    | 0.56                        | 147                 |
| 25    | 0.49                        | 152                 |
| 50    | 0.31                        | 117                 |
| 100   | 0.22                        | 85                  |

Combined with the now defunct grayHorizontal() function, saving an array traversal.

#### getPlatforms()

Creates platforms on all white pixels in the image.

#### grayHorizontal() (NO LONGER USED)

Colors the horizontal lines (those at least 100 pixels of the same color) white, and the rest black. The horizontal lines in the Sobel image correspond to the detected edges in the screenshot, so this function highlights them further.

### game.py

This file contains the class definition for Game, which contains the logic that runs the game. Whenever main.py is run for the first time, or whenever a new game is started within the instance, a Game object of the appropriate game mode is created. 

Game objects can be initialized with one of three modes: 
  * In Mode 1, the player must collect coins while avoiding enemies. Every 2nd coin collected spawns a new enemy.
  * In Mode 2, the player must shoot and destroy enemies while avoiding contact. Each enemiy destroyed spawns two in its place.
  * Mode 0 is the "menu mode." This allows the player to navigate the map without starting one of the two main game modes.
  
The Game class relies on three main functions: process_events(), run_logic(), and display_frame()

#### process_events()

Interprets keystrokes based on current game mode and calls the various sprite class functions (located in sprites.py). Returns a Boolean flag to main() indicating whether or not the game instance is done.

#### run_logic()

Runs the main game logic including generating new sprites, detecting collisions and calling the apprpriate sprite class functions, and shifting the frame when the player gets close to an edge.

#### display_frame()

Displays the appropriate frame depending on game over/started status.

### sprites.py

This file contains the class definitions for the various sprites used to represent game objects. The sprite class defintions contained here include:
  * Player. Represents the player.
  * Enemy. Represents enemies that chase the player. Has a different speed depending on the game mode. 
  * Coin. Represents collectable coins in Mode 1 that the player can collect to increase the score.
  * Bullet. Represents a projectile that the player can use to fight off enemies in Mode 2. Sprite collision for the Coin and Bullet classes was inspired by [this](http://programarcadegames.com/python_examples/f.php?file=bullets.py) section of Dr. Craven's website.
  * Platform. Represents a surface that the player will not fall through under normal conditions.
  * Level/Level_01. Contains the platform locations for the level.
