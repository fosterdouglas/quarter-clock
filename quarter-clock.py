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
            
def Blink(pos, r=30, g=30, b=30):
    
    #position coordinates from top right of device
    for i in range(len(pos)):
        picounicorn.set_pixel(pos[1],pos[0],r, g, b)
        
def SetBlinkRow():
    if currentSecond <= 6:
        return 6
    if currentSecond > 6 and currentSecond <= 13:
        return 9
    if currentSecond > 13 and currentSecond <= 20:
        return 12
    if currentSecond > 20 and currentSecond <= 27:
        return 15
    if currentSecond > 27 and currentSecond <= 34:
        return 6
    if currentSecond > 34 and currentSecond <= 41:
        return 9
    if currentSecond > 41 and currentSecond <= 48:
        return 12
    if currentSecond > 48 and currentSecond <= 55:
        return 15



while True:
    currentSecond = localtime(time())[5]
    currentMinute = localtime(time())[4]
    currentHour = localtime(time())[3]
    
    SetBlinkRow()
    
    if secondsDelta != currentSecond and currentSecond == 0:
        for x in range(w):
            picounicorn.set_pixel_value(15, x, 0)
            picounicorn.set_pixel_value(12, x, 0)
            picounicorn.set_pixel_value(9, x, 0)
            picounicorn.set_pixel_value(6, x, 0)
    
    if secondsDelta != currentSecond and currentSecond < 56:
        #first 55 seconds
        if currentSecond < 28:
            blinkR = 30
            blinkG = 30
            blinkB = 30
        else:
            blinkR = 0
            blinkG = 0
            blinkB = 0
        Blink([abs((currentSecond % 7) - 6), GetBlinkRow()], blinkR, blinkG, blinkB)
        print(str(currentSecond) + "s")
        
    if secondsDelta != currentSecond and currentSecond >= 56:
        #final 4 seconds
        if currentSecond % 4 == 0:
            for x in range(w):
                picounicorn.set_pixel_value(15, x, 30)
            print(str(currentSecond) + "s")
        if currentSecond % 4 == 1:
            for x in range(w):
                picounicorn.set_pixel_value(12, x, 30)
            print(str(currentSecond) + "s")
        if currentSecond % 4 == 2:
            for x in range(w):
                picounicorn.set_pixel_value(9, x, 30)
            print(str(currentSecond) + "s")
        if currentSecond % 4 == 3:
            for x in range(w):
                picounicorn.set_pixel_value(6, x, 30)
            print(str(currentSecond) + "s")
            
    if minutesDelta != currentMinute:
        print(str(currentMinute) + 'm')
    
    if currentMinute > 15:
        for x in range(w):
            picounicorn.set_pixel(7, x, 0, 170, 170)
            picounicorn.set_pixel(8, x, 0, 170, 170)
    if currentMinute > 29:
        for x in range(w):
            picounicorn.set_pixel(10, x, 0, 170, 170)
            picounicorn.set_pixel(11, x, 0, 170, 170)
    if currentMinute > 44:
        for x in range(w):
            picounicorn.set_pixel(13, x, 0, 170, 170)
            picounicorn.set_pixel(14, x, 0, 170, 170)
    
    if hoursDelta != currentHour:
        ClearDisplay()
        print(str(currentHour) + 'h')
    
    hoursDelta = currentHour
    minutesDelta = currentMinute
    secondsDelta = currentSecond
    
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
    
    