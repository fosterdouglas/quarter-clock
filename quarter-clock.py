import picounicorn
from utime import time, localtime, sleep
import math
import rv3028_rtc

picounicorn.init()

w = picounicorn.get_width()
h = picounicorn.get_height()

#initalize the RV3028 RTC unit
sda=machine.Pin(26)
scl=machine.Pin(27)
i2c=machine.I2C(1,sda=sda, scl=scl, freq=400000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

#one-time setup to give RV3028 the correct time
#date_time = (localtime()[0],localtime()[1],localtime()[2],localtime()[3],localtime()[4],localtime()[5],"mon")
#rtc.set_rtc_date_time(date_time)
#print("time calibrated?")

blink = False

currentSecond = rtc.get_seconds()
currentMinute =  rtc.get_minutes()
currentHour = rtc.get_hours()

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
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[one] = [
            [2,0],
      [1,1],[2,1],
[0,2],      [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[two] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
[0,4],
[0,5],
[0,6],[1,6],[2,6]
]

digits[three] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digits[four] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[five] = [
[0,0],[1,0],[2,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digits[six] = [
[0,0],[1,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[seven] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[eight] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[nine] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

def Digit(num, offset):
    for i in range(len(num)):
        x = num[i][0]        
        y = num[i][1]
        
        #shift position over by an offset number
        x = x + offset
            
        picounicorn.set_pixel(x,y,200, 200, 200)

            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
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


#on startup, clear any past display memory
ClearDisplay()

while True:
    sleep(0.001)
    #print(rtc.get_seconds(), rtc.get_minutes(), rtc.get_hours())
    #only run one per second
    if currentSecond != rtc.get_seconds():
        ClearDisplay() 
        
        print(currentSecond, currentMinute, currentHour)
        
#         GetBlinkRow()
#         
#         if math.floor(currentSecond / 15) % 2 == 0:
#             blinkR = 30
#             blinkG = 30
#             blinkB = 30
#         if math.floor(currentSecond / 15) % 2 == 1:
#             blinkR = 0
#             blinkG = 0
#             blinkB = 0
# 
#         Blink([abs((currentSecond % (h-2)) - 5), GetBlinkRow()], blinkR, blinkG, blinkB)
        
        print(str(currentSecond) + "s")
        
        currentSecond = rtc.get_seconds()
                
        if rtc.get_minutes() != currentMinute:
            print(str(currentMinute) + 'm')
            
            currentMinute = rtc.get_minutes()
        
        #display minute "group" lines
#         for x in range(w):
#             picounicorn.set_pixel(x, 6, *blue)
#             
#             if currentMinute < 15:
#                 picounicorn.set_pixel(abs((currentMinute % w) - 6), 6, *green)
#             
#             if currentMinute > 14:
#                 picounicorn.set_pixel(x, 9, *blue)
#                 
#                 if currentMinute < 29:
#                     picounicorn.set_pixel(abs(((currentMinute + 1) % w) - 6), 9, *green)
#                 
#             if currentMinute > 29:
#                 picounicorn.set_pixel(x, 12, *blue)
#                 
#                 if currentMinute < 44:
#                     picounicorn.set_pixel(abs(((currentMinute - 1) % w) - 6), 12, *green)
#             if currentMinute > 44:
#                 picounicorn.set_pixel(x, 15, *blue)
#                 
#                 if currentMinute < 59:
#                     picounicorn.set_pixel(abs(((currentMinute - 1) % w) - 6), 15, *green)
        
        if rtc.get_hours() != currentHour:
            #clear display for new hour digits
            ClearDisplay()
            print(str(currentHour) + 'h')
            
            currentHour = rtc.get_hours()

            
        #just to test
        thirdDigit = math.floor(currentSecond / 10)
        forthDigit = math.floor(currentSecond % 10)
        Digit(digits[thirdDigit], 9)
        Digit(digits[forthDigit], 13)
        
        #display main digits
        if currentHour < 10:        
            firstDigit = 0
            secondDigit = currentHour
            Digit(digits[firstDigit], 0)
            Digit(digits[secondDigit], 4)
                 
        else:        
            firstDigit = math.floor(currentHour / 10)
            secondDigit = math.floor(currentHour % 10)
            Digit(digits[firstDigit], 0)
            Digit(digits[secondDigit], 4)
    
    