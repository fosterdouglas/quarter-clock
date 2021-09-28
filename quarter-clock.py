import picounicorn
from utime import time, localtime, sleep
import math
import threading
import rv3028_rtc

picounicorn.init()

w = picounicorn.get_width()
h = picounicorn.get_height()

# initalize the RV3028 RTC unit
sda=machine.Pin(26)
scl=machine.Pin(27)
i2c=machine.I2C(1,sda=sda, scl=scl, freq=400000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

# one-time setup to give RV3028 the correct time
#date_time = (localtime()[0],localtime()[1],localtime()[2],localtime()[3],localtime()[4],localtime()[5],"sun")
#rtc.set_rtc_date_time(date_time)
#print("time calibrated?")

currentSecond = rtc.get_seconds()
currentMinute = rtc.get_minutes()
currentHour = rtc.get_hours()

pulse = True
quarterOffsets = [8,10,12,14]
global currentQuarter
global brt

# numbers, used in various dictionaries
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
ten = 10
eleven = 11
twelve = 12
thirteen = 13
fourteen = 14
fifteen = 15
sixteen = 16
seventeen = 17
eighteen = 18
nineteen = 19
twenty = 20
twentyone = 21
twentytwo = 22
twentythree = 23

# make a dictionary for digits 0 - 9, to map to the coordinates of pixels to draw each digit
digits = {}

# make a dictionary of hours, used to set specific colors to specific hours
hours = {}

# expressed in hsv Hue degrees
# did this because i'm a control freak and using 15 degree increments programatically felt unbalanced toward green
# could put these values in an array, but easier to edit and see when individually assigned like this
hours[zero] = 310
hours[one] = 320
hours[two] = 330
hours[three] = 340
hours[four] = 350
hours[five] = 0 
hours[six] = 15 
hours[seven] = 20
hours[eight] = 30
hours[nine] = 35
hours[ten] = 40
hours[eleven] = 50
hours[twelve] = 60
hours[thirteen] = 90
hours[fourteen] = 150
hours[fifteen] = 170
hours[sixteen] = 190
hours[seventeen] = 200
hours[eighteen] = 215
hours[nineteen] = 225
hours[twenty] = 265
hours[twentyone] = 285
hours[twentytwo] = 300
hours[twentythree] = 305

# position coordinates from top left of the number
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
        
        #shift position over by an offset number and draw pixels          
        picounicorn.set_pixel(x + offset, y, *Rainbow(hours[currentHour], VB(255, 50)))

            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            #draws "black" pixels
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
def Pillar(width, offset, brightness, height=h, rainbow=True):
    for x in range(width):
        for y in range(height):
            #shift position over by an offset number and draw pixels
            if rainbow == True:
                picounicorn.set_pixel(x + offset, y, *Rainbow(hours[currentHour], brightness))
            else:
                picounicorn.set_pixel(x + offset, y, brightness, brightness, brightness)

def Rainbow(hue, value):
    hue = (hue)/360
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, value/255)]
    return (r, g, b)

def Brightness(default=False):
    global brt
    
    if default == True or brt < 0.4:
        brt = round(1.0, 1)
    else:
        brt = brt - round(0.2, 1)

    Reset()
    print("Brightness = " + str(brt))
    sleep(0.1)

def VB(value, minimum=0):
    value = value * brt

    if value < minimum:
        value = minimum
        
    return int(value)

def Pulse():
    if currentSecond != rtc.get_seconds():
        
        #TODO: continue working on this to optimize
        if currentQuarter == 0:
            localOffset = (currentSecond%6)+quarterOffsets[1]
        elif currentQuarter == 1:
            temp = (currentSecond%6)
            if temp == 0 or temp == 1:
                localOffset = (currentSecond%6)+quarterOffsets[0]
            else:
                localOffset = (currentSecond%6)+quarterOffsets[1] #this
        elif currentQuarter == 2:
            temp = (currentSecond%6)
            if temp == 4 or temp == 5:
                localOffset = (currentSecond%6)-4+quarterOffsets[3]
            else:
                localOffset = (currentSecond%6)+quarterOffsets[0]
        elif currentQuarter == 3:
            localOffset = (currentSecond%6)+quarterOffsets[0]
            
        for i in range(VB(90,30), VB(210, 120), 30):
            Pillar(1, localOffset, i)
            sleep(0.05)
        for i in reversed(range(VB(90,30), VB(210, 120), 30)):
            Pillar(1, localOffset, i)
            sleep(0.05)

def DisplayQuarters():
    global currentQuarter
    flux = False
    
    # check which quarter we are in
    if currentMinute <= 13:
        print("first quarter")
        currentQuarter = 0
    elif currentMinute >= 14 and currentMinute <= 28:
        print("second quarter")
        currentQuarter = 1
    elif currentMinute >= 29 and currentMinute <= 43:
        print("third quarter")
        currentQuarter = 2
    #TODO: this still isnt quite working when it hits 59 i think
    elif currentMinute >= 44:
        print("fourth quarter")
        currentQuarter = 3
        
    if currentMinute == 14 or currentMinute == 29 or currentMinute == 44 or currentMinute == 59:
        flux = True
    
    # this is dumb, but it works for now
    # TODO: change the above "quarter" vars to 0,1,2,3
    # and use that in arrays below to simplify stuff
    for i in range(4):

        # for the current quarter
        if i == currentQuarter:
            
            if flux == False:
                # animation for blink/fade each minute
                print('minute blink')
                for desc in reversed(range(VB(34,0), VB(204, 100), 17)):  
                    Pillar(2, quarterOffsets[i], desc)
                    sleep(0.02)
                for asc in range(VB(34,0), VB(204, 100), 17):  
                    Pillar(2, quarterOffsets[i], asc)
                    sleep(0.02)
                    
                Pillar(2, quarterOffsets[i], VB(240, 80))
                
            # animate for each quarter change
            if flux == True:
                
                if i > 0:
                    Pillar(2, quarterOffsets[i - 1], VB(240, 80))
                    
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[i - 1], 0, off + 1)
                        sleep(0.03)
                    # replace the emptiness with fade quarter
                    Pillar(2, quarterOffsets[i - 1], VB(60, 30))
                    
                     #animate next quarter over
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[i], VB(240, 80), on + 1)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[i], VB(240, 80))
                else:
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[3], 0, off + 1)
                        sleep(0.03)
                    # replace the emptiness with fade quarter
                    Pillar(2, quarterOffsets[3], VB(60, 30))
                    
                    # otherwise, animate the first quarter   
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[0], VB(240, 80), on + 1)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[0], VB(240, 80))
        
        # for the other 3 quarters
        else:
            Pillar(2, quarterOffsets[i], VB(60, 30))
        
def DisplayHours():
    # display main digits
    Digit(digits[HourFormat()[0]], 0)
    Digit(digits[HourFormat()[1]], 4)
            
def HourTransition():    
    for i in range(w/2):
        fade = VB(30, 0) + (i*VB(20, 10))
        Pillar(1, (math.ceil(w/2)) + i, fade)
        Pillar(1, (math.floor(w/2)-1) - i, fade)
        sleep(1/w)
    for i in range(w/2):
        fade = max(0, (VB(255, 100) - (i*VB(40, 20))))
        Pillar(1, (math.ceil(w/2)) + i, fade)
        Pillar(1, (math.floor(w/2)-1) - i, fade)
        sleep(1/w)
    for i in range(w/2):
        fade = max(0, (VB(255, 100) - (i*VB(40, 20))))
        Pillar(1, (math.ceil(w/2)) + i, fade)
        Pillar(1, (math.floor(w/2)-1) - i, fade)
        Pillar(1, (math.ceil(w/2)+1) + (i-1), 0)
        Pillar(1, (math.floor(w/2)-1) - (i), 0)
        sleep(1/w)

def HourFormat():
    if currentHour < 10:
        firstDigit = 0
        secondDigit = currentHour
    else:        
        firstDigit = math.floor(currentHour / 10)
        secondDigit = math.floor(currentHour % 10)
       
    return [firstDigit, secondDigit]

def ButtonToggle(handler, button):
    if handler != button:
        if button == True:
            button = False
        else:
            button = True
        sleep(0.1)
        return button
    

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

def Reset():
    ClearDisplay()

    DisplayHours()
    DisplayQuarters()

def Setup():
    # on startup, clear any past display memory
    ClearDisplay()
    
    HourTransition()
    DisplayHours()
    DisplayQuarters()

Brightness(True)
Setup()



while True:
    #sleep(0.1) is this breaking the RTC consistency?
    
    #button "handlers" kind of
    #buttonA = False
    buttonA = False
    buttonA = ButtonToggle(picounicorn.is_pressed(picounicorn.BUTTON_A), buttonA)
    
    
    buttonB = False
    buttonBHandler = picounicorn.is_pressed(picounicorn.BUTTON_B)

    # only run once per second
    if currentSecond != rtc.get_seconds():
        
        Pulse()
        
        print(currentHour, currentMinute, currentSecond)
        
        currentSecond = rtc.get_seconds()
        #print(str(currentSecond) + "s")
                
        # check minute        
        if rtc.get_minutes() != currentMinute:
            DisplayQuarters()
            
            currentMinute = rtc.get_minutes()
            print(str(currentMinute) + 'm')
        
        # check hour  
        if rtc.get_hours() != currentHour:
            currentHour = rtc.get_hours()
            print(str(currentHour) + 'h')
            
            HourTransition()
        
        DisplayHours()

    # disco mode, TODO: turn this into a function by making a "button handler" with Break  
    if buttonA == True:
        buttonA = ButtonToggle(picounicorn.is_pressed(picounicorn.BUTTON_A), buttonA)
        while buttonA == False:
            sleep(0.5)
            exitloop = picounicorn.is_pressed(picounicorn.BUTTON_A)
            
            for i in range(16):
                hue = (hours[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(i, y, r, g, b)
                sleep(0.01)
                
            for i in range(16):
                hue = (hours[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(15-i, y, r, g, b)
                sleep(0.01)
            if exitloop == True:
                ClearDisplay()
                HourTransition()
                DisplayHours()
                DisplayQuarters()
                break
    
    while buttonB == True:
        Brightness()
        sleep(0.1)
        break
    
    