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

#from game import Game

class ImageProcessing(object):

    def getImage(self):
        """read an image, crop it, and return it along with its dimensions
        in the future, this method will take a screenshot and read that image in"""
        try:
            if os.path.isfile('images/temp.bmp'):
                os.unlink('images/temp.bmp')
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
        img_png = ImageGrab.grab()
        img = np.asarray(img_png)
        img_png.save('images/temp.bmp')
        #print(type(img))
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

        #iterate over img, one pixel in from edge
        for i in range(1,rows-1):
            for j in range(1,cols-1):
                sx = 0#(img[i-1][j+1] + c*img[i][j+1] + img[i+1][j+1]) - (img[i-1][j-1] + c*img[i][j-1] + img[i+1][j-1])
                sy = (img[i-1][j-1] + c*img[i-1][j] + img[i-1][j+1]) - (img[i+1][j-1] + c*img[i+1][j] + img[i+1][j+1])
                m = (sx**2 + sy**2)**(1/2)

                sb[i][j]=m/6

        return sb

    #Image processing functions will be moved to own class in future
    def grayHorizontal(self,img):
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

    #Image processing functions will be moved to own class in future
    def getPlatforms(self,img):
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
