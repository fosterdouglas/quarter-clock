import picounicorn
from utime import time, localtime, sleep
import math

picounicorn.init()

#everywhere in this program X is refering to the physical X axis of the
#device, not the X axis of the coordinates system. same for Y. everything is
#written to adjust for this, for some semblence of mental coherence

#reversed h/w for vertical orientation
h = picounicorn.get_width()
w = picounicorn.get_height()

blockHeight = 2
numberHeight = 5
blink = False

hoursDelta = 0
minutesDelta = 0
secondsDelta = 0

blue = (0, 140, 140)
green = (40, 200, 20)
white = (140, 140, 140)

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

#position coordinates from top left of the number
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

def Digit(num, digit):
    for i in range(len(num)):
        x = num[i][0]
        
        #stupid, but numbers require reflections because of coordinate system
        if num[i][0] == 2:
            x = x - 2
        if num[i][0] == 0:
            x = x + 2
        
        y = num[i][1]
        
        if digit == 0:
            x = x + 4 #shift position over to the left if its first digit
            
        picounicorn.set_pixel(y,x,200, 200, 200)

            
def ClearDisplay():
    for y in range(h):
        for x in range(w):
            picounicorn.set_pixel(y, x, 0, 0, 0)
            
def Blink(pos, r, g, b):
    
    #position coordinates from top right of device
    for i in range(len(pos)):
        picounicorn.set_pixel(pos[1],pos[0],r, g, b)
        
def GetBlinkRow():
    currentRow = math.floor(currentSecond / 5)
        
    if currentRow % 3 == 0:
        return 7
    if currentRow % 3 == 1:
        return 10
    if currentRow % 3 == 2:
        return 13



while True:
    currentSecond = localtime(time())[5]
    currentMinute = localtime(time())[4]
    currentHour = localtime(time())[3]
    
    #only run one per second
    if secondsDelta != currentSecond:
        
        GetBlinkRow()
        
        if math.floor(currentSecond / 15) % 2 == 0:
            blinkR = 30
            blinkG = 30
            blinkB = 30
        if math.floor(currentSecond / 15) % 2 == 1:
            blinkR = 0
            blinkG = 0
            blinkB = 0

        Blink([abs((currentSecond % (w-2)) - 5), GetBlinkRow()], blinkR, blinkG, blinkB)
        
        print(str(currentSecond) + "s")
                
        if minutesDelta != currentMinute:
            print(str(currentMinute) + 'm')
        
        #display minute "group" lines
        for x in range(w):
            picounicorn.set_pixel(6, x, *blue)
            
            if currentMinute < 15:
                picounicorn.set_pixel(6, abs((currentMinute % w) - 6), *green)
            
            if currentMinute > 14:
                picounicorn.set_pixel(9, x, *blue)
                
                if currentMinute < 29:
                    picounicorn.set_pixel(9, abs(((currentMinute + 1) % w) - 6), *green)
                
            if currentMinute > 29:
                picounicorn.set_pixel(12, x, *blue)
                
                if currentMinute < 44:
                    picounicorn.set_pixel(12, abs(((currentMinute - 1) % w) - 6), *green)
            if currentMinute > 44:
                picounicorn.set_pixel(15, x, *blue)
                
                if currentMinute < 59:
                    picounicorn.set_pixel(15, abs(((currentMinute - 1) % w) - 6), *green)
        
        if hoursDelta != currentHour:
            #clear display for new hour digits
            ClearDisplay()
            print(str(currentHour) + 'h')
        
        hoursDelta = currentHour
        minutesDelta = currentMinute
        secondsDelta = currentSecond
        
        #display main digits
        if currentHour < 10:        
            firstDigit = 0
            secondDigit = currentHour
            Digit(digits[firstDigit], 0)
            Digit(digits[secondDigit], 1)
        else:        
            firstDigit = math.floor(currentHour / 10)
            secondDigit = math.floor(currentHour % 10)
            Digit(digits[firstDigit], 0)
            Digit(digits[secondDigit], 1)
    
    