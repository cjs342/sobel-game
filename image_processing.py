import numpy as np
from PIL import ImageGrab
import os

from sprites import Player
from sprites import Enemy
from sprites import Level
from sprites import Level_01
from sprites import Platform
from sprites import Bullet
from sprites import Coin


class ImageProcessing(object):
    """Class containing the image processing functions used to generate the level"""

    def getImage(self):
        """read an image, crop it, and return it along with its dimensions
        in the future, this method will take a screenshot and read that image in"""

        #delete existing temp.bmp so a new screenshot can be taken
        try:
            if os.path.isfile('images/temp.bmp'):
                os.unlink('images/temp.bmp')
        except Exception as e:
            print(e)

        #take a screenshot and save it
        img_png = ImageGrab.grab()
        img = np.asarray(img_png)
        img_png.save('images/temp.bmp')
        rows,cols,color = img.shape

        return img_png,img,rows,cols

    #Image processing functions will be moved to own class in future
    def rgb2gray(self,rgb):
        """converts an RGB image to grayscale using the luma coding formula:
        Y = 0.299R + 0.587G + 0.114B"""
        return np.dot(rgb[...,:3], [0.299,0.587,0.114])

    #Image processing functions will be moved to own class in future
    def sobel(self,img):
        """apply the Sobel filter to detect edges (grayscale only)"""
        if len(img.shape)>2:
            raise ValueError('arg must be 2 dimensional (grayscale)')
            return
        #get img dimensions
        rows,cols = img.shape

        c=4 #Sobel coefficient

        #create new blank image of same size
        sb = np.zeros((rows,cols))
        horiz = np.zeros((rows,cols))

        plat = 100  #length of pixel run that we will call a platform
        gap = 10     #only evaluate every gap-th column cell to save time. must be divisible by plat and > 0

        #perform sobel edge detection in y direction (detect horizontal edges) and highlight horizontal edges
        for i in range(1,rows-1):
            count = 0
            for j in range(1,cols-1):
                if j%gap == 0:
                    #pass the image through the sobel filter
                    sx = 0#(img[i-1][j+1] + c*img[i][j+1] + img[i+1][j+1]) - (img[i-1][j-1] + c*img[i][j-1] + img[i+1][j-1])
                    sy = (img[i-1][j-1] + c*img[i-1][j] + img[i-1][j+1]) - (img[i+1][j-1] + c*img[i+1][j] + img[i+1][j+1])
                    m = (sx**2 + sy**2)**(1/2)

                    sb[i][j]=m/6

                    """Below code merges sobel() and (old) grayHorizontal()"""
                    #once index clears the filter, look for consecutive pixels
                    if j>2:
                        k=j-max(2,gap) #new column index so horizontal doesn't overlap with sobel
                        #detect same value adjacent pixels
                        if sb[i][k]==sb[i][k-gap] and sb[i][k]>0.1:
                            count+=1
                        #if adjacent pixels are different value, reset count
                        else:
                            count = 0
                        #once plat consecutive same value pixels are detected, color the platform-tracking image white
                        if count == plat/gap:
                            count = 0
                            horiz[i][k-plat+1:k+1] = [1]*plat

        return horiz

    """grayHorizontal() merged into sobel(). Saves about ~1 second (on my machine) of processing time."""
    #Image processing functions will be moved to own class in future
    def grayHorizontal(self,img):
        """colors the horizontal lines in an image white and blacks the rest
        input 2-D array"""
        rows,cols=img.shape
        img_horiz=np.zeros(img.shape)

        for i in range(rows):
            for j in range(cols-100):

                x=img[i][j]
                x_next=img[i][j+1]
                count=1
                #count the number of identical adjacent pixels
                while x>0.1 and x==x_next and count<100:
                    count+=1
                    x=x_next
                    x_next = img[i][j+count]
                #color line white if same color detected for 100 pixels
                if count==100:
                    for k in range(100):
                        img_horiz[i][j+k]=1
                    j+=100

        return img_horiz

    def getPlatforms(self,img):
        """returns a list of platforms (defined by width, height, x, y) given a b/w image
        platforms are created wherever whitespace is detected. used with the output of grayHorizontal method"""
        rows,cols = img.shape
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

        print("# of platforms: %d" % len(platforms))
        return platforms
