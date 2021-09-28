import picounicorn
from utime import time, localtime, sleep
import math

picounicorn.init()

w = picounicorn.get_width()
h = picounicorn.get_height()

blockWidth = 2
numberHeight = 5
blink = False

hoursDelta = 0
secondsDelta = 0

#make a dictionary of numbers
digits = {}
zero = 0
one = 1
two = 2
three = 3
four = 4
five = 5
six = 6
seven = 7
eight = 8
nine = 9

digits[zero] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],[1,4],[2,4]
]

digits[one] = [
      [1,0],
[0,1],[1,1],
      [1,2],
      [1,3],
[0,4],[1,4],[2,4]
]

digits[two] = [
[0,0],[1,0],[2,0],
            [2,1],
[0,2],[1,2],[2,2],
[0,3],
[0,4],[1,4],[2,4]
]

digits[three] = [
[0,0],[1,0],[2,0],
            [2,1],
      [1,2],[2,2],
            [2,3],
[0,4],[1,4],[2,4]
]

digits[four] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],[1,2],[2,2],
            [2,3],
            [2,4]
]

digits[five] = [
[0,0],[1,0],[2,0],
[0,1],
[0,2],[1,2],[2,2],
            [2,3],
[0,4],[1,4],[2,4]
]

digits[six] = [
[0,0],
[0,1],
[0,2],[1,2],[2,2],
[0,3],      [2,3],
[0,4],[1,4],[2,4]
]

digits[seven] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
            [2,3],
            [2,4]
]

digits[eight] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],[1,2],[2,2],
[0,3],      [2,3],
[0,4],[1,4],[2,4]
]

digits[nine] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],[1,2],[2,2],
            [2,3],
            [2,4]
]

def PixelNumber(num, digit):
    for i in range(len(num)):
        y = num[i][0]
        
        #stupid, but numbers require reflections because of coordinate system
        if num[i][0] == 2:
            y = y - 2
        if num[i][0] == 0:
            y = y + 2
        
        x = num[i][1]
        
        if digit == 0:
            y = y + 4 #shift position over to the left if its first digit
            
        picounicorn.set_pixel(x,y,0, 150, 150)
        
def QuarterBlock(pos):
    offset = [5, 8, 11, 14]
    
    for x in range(blockWidth):
        for y in range(h):
            picounicorn.set_pixel_value(x + offset[pos],y,80)
            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            picounicorn.set_pixel(x, y, 0, 0, 0)


while True:
    
    if hoursDelta != localtime(time())[3]:
        ClearDisplay()
    
    hoursDelta = localtime(time())[3]
    
    if localtime(time())[3] < 10:        
        firstDigit = 0
        secondDigit = localtime(time())[3]
        PixelNumber(digits[firstDigit], 0)
        PixelNumber(digits[secondDigit], 1)
    else:        
        firstDigit = math.floor(localtime(time())[3] / 10)
        secondDigit = math.floor(localtime(time())[3] % 10)
        PixelNumber(digits[firstDigit], 0)
        PixelNumber(digits[secondDigit], 1)
        
    QuarterBlock(0)
    QuarterBlock(1)
    QuarterBlock(2)
    QuarterBlock(3)
    
    if secondsDelta != localtime(time())[5]:

        if blink == False:
            for x in range(numberHeight):
                picounicorn.set_pixel_value(x,3,30) #blinking divider on
            blink = True
        else:
            for x in range(numberHeight):
                picounicorn.set_pixel_value(x,3,6) #blinking divider off
            blink = False
            
    secondsDelta = localtime(time())[5]
    
    
    