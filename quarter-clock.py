import picounicorn
from utime import time, localtime, sleep
import math
import gc
import rv3028_rtc
from machine import Pin

picounicorn.init()

w = picounicorn.get_width()
h = picounicorn.get_height()

# initalize the RV3028 RTC unit
i2c=machine.I2C(1,sda=Pin(26), scl=Pin(27), freq=100000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

currentSecond = rtc.get_seconds()
currentMinute = rtc.get_minutes()
currentHour = rtc.get_hours()

pulse = True
quarterOffsets = [8,10,12,14]

global currentQuarter
global brt #brightness
global hr #hour
global shift #color shift
global hr12 #24 or 12h clock

currentQuarter = 0
brt = 0.8 #start brightness at one level down
hr = currentHour
shift = 0
hr12 = False

# using these instead of picounicorn's built in functions to be able to access IRQs
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

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
hh = 30 #for custom "h" letter

# make a dictionary for digits 0 - 9, to map to the coordinates of pixels to draw each digit
digits = {}

# make a dictionary of hours, used to set specific colors to specific hours
hours = {}

# expressed in hsv Hue degrees
# did this because i'm a control freak and using even 15 degree increments programatically felt unbalanced toward green
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

digits[hh] = [
[0,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

def Digit(num, offset, erase=False):
    for i in range(len(num)):
        x = num[i][0]        
        y = num[i][1]
        
        localhue = ColorShift(hours[hr], 10)
        localbrightness = VB(255, 50)
        
        if erase:
            localbrightness = 0
        
        #shift position over by an offset number and draw pixels          
        picounicorn.set_pixel(x + offset, y, *Rainbow(localhue, localbrightness))

            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            #draws "black" pixels
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
def Pillar(width, offset, localbrightness, height=h, localhue=hours[hr], hueshift=0):
    localhue = localhue + hueshift
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x + offset, y, *Rainbow(localhue, localbrightness))

def Rainbow(localhue, localvalue):
    global shift
    localhue = (localhue + shift)%359
    localhue = (localhue)/360
    r, g, b = [int(c * 255) for c in hsv_to_rgb(localhue, 1.0, localvalue/255)]
    return (r, g, b)

def ColorShift(color, delta=10):
    adj = color + delta
    return adj

def Brightness(default=False):
    global brt
    
    if default == True or brt < 0.4:
        brt = round(1.0, 1)
    else:
        brt = brt - round(0.2, 1)

    Reset()
    sleep(0.1)

def VB(value, minimum=0):
    value = value * brt

    if value < minimum:
        value = minimum
        
    return int(value)

def Pulse():
    global hr
    
    #TODO: maybe replace this with a function, it's used three times kind of
    if hr == 23:
        forwardhue = hours[0]
    else:
        forwardhue = hours[hr+1]
    
    
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
        
    for i in range(VB(50,25), VB(210, 120), 25):
        Pillar(1, localOffset, i, localhue=forwardhue, hueshift=20)
        sleep(0.05)
    for i in reversed(range(VB(50,25), VB(210, 120), 25)):
        Pillar(1, localOffset, i, localhue=forwardhue, hueshift=20)
        sleep(0.05)

def DisplayQuarters():
    global currentQuarter
    global hr
    flux = False
    
    #TODO: replace
    if hr == 23:
        forwardhue = hours[0]
    else:
        forwardhue = hours[hr+1]
    
    # check which quarter we are in
    if currentMinute <= 13 or currentMinute == 59:
        print("first quarter")
        currentQuarter = 0
    elif currentMinute >= 14 and currentMinute <= 28:
        print("second quarter")
        currentQuarter = 1
    elif currentMinute >= 29 and currentMinute <= 43:
        print("third quarter")
        currentQuarter = 2
    elif currentMinute >= 44 and currentMinute <= 58:
        print("fourth quarter")
        currentQuarter = 3
        
    if currentMinute == 14 or currentMinute == 29 or currentMinute == 44 or currentMinute == 59:
        flux = True
    
    # draw each of the 4 quarters
    for i in range(4):
        
        # for the current quarter
        if i == currentQuarter:
            
            if flux == False:
                # animation for blink/fade each minute
                print('minute blink')
                for desc in reversed(range(VB(34,0), VB(204, 100), 17)):  
                    Pillar(2, quarterOffsets[i], desc, localhue=forwardhue, hueshift=20)
                    sleep(0.02)
                for asc in range(VB(34,0), VB(204, 100), 17):  
                    Pillar(2, quarterOffsets[i], asc, localhue=forwardhue, hueshift=20)
                    sleep(0.02)
                    
                Pillar(2, quarterOffsets[i], VB(240, 80), localhue=forwardhue, hueshift=20)
                
            # animate for each quarter change
            if flux == True:
                
                if i > 0:
                    Pillar(2, quarterOffsets[i - 1], VB(240, 80), localhue=forwardhue, hueshift=20)
                    
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[i - 1], 0, off + 1, localhue=forwardhue, hueshift=20)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    Pillar(2, quarterOffsets[i - 1], VB(50, 25), localhue=forwardhue, hueshift=20)
                    
                     #animate next quarter over
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[i], VB(240, 80), on + 1, localhue=forwardhue, hueshift=20)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[i], VB(240, 80), localhue=forwardhue, hueshift=20)
                else:
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[3], 0, off + 1, localhue=forwardhue, hueshift=20)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    Pillar(2, quarterOffsets[3], VB(50, 25), localhue=forwardhue, hueshift=20)
                    
                    # otherwise, animate the first quarter   
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[0], VB(240, 80), on + 1, localhue=forwardhue, hueshift=20)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[0], VB(240, 80), localhue=forwardhue, hueshift=20)
        
        # for the other 3 faded quarters
        else:
            Pillar(2, quarterOffsets[i], VB(50, 25), localhue=forwardhue, hueshift=20)
        
def DisplayHours():
    # display main digits
    Digit(digits[HourFormat()[0]], 0)
    Digit(digits[HourFormat()[1]], 4)
            
def HourTransition():
    # animation when changing hours
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
    global hr
    
    # resets the hour if it goes above 23 during user time setting
    # TODO: replace
    if hr > 23:
        hr = 0
    
    localhour = hr
    
    #format properly if 12h clock being used
    if hr12 == True:
        localhour = localhour%12
        if localhour == 0:
            localhour = 12
    
    # formats the two-digit hours into two single-digit numbers
    if localhour < 10:
        firstDigit = 0
        secondDigit = localhour
    else:        
        firstDigit = math.floor(localhour / 10)
        secondDigit = math.floor(localhour % 10)
       
    return [firstDigit, secondDigit]
        

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
    
def callback_button_a(pin):
    print('button A')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        #TODO: try threading Event before giving up on optimizing this
        exitLoop = False
        sleep(0.5)
        while not exitLoop:
            for i in range(16):
                
                #TODO: use Rainbow() here?
                hue = (hours[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(i, y, r, g, b)
                sleep(0.01)
                
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    exitLoop = True
                    break
                
            for i in range(16):
                
                #TODO: use Rainbow() here?
                hue = (hours[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(15-i, y, r, g, b)
                sleep(0.01)
                
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    exitLoop = True
                    break
                
            sleep(0.5)
        Reset()

def callback_button_b(pin):
    print('button B')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        # check if button held
        for t in range (31):
            if picounicorn.is_pressed(picounicorn.BUTTON_B):
               sleep(0.1)
               
               # if held for 3 sec, toggle time between 12/24h
               if t == 30:
                global hr12
                hr12 = not hr12
                
                ClearDisplay()
                
                # animation to show new hour format 
                if hr12:
                    for f in range (6):
                        # draw blank first
                        Pillar(12, 0, 0)
                        sleep(0.1)
                        Digit(digits[1], 0)
                        Digit(digits[2], 4)
                        Digit(digits[hh], 8)
                        sleep(0.2)
                        
                else:
                    for f in range (6):
                        # draw blank first
                        Pillar(12, 0, 0)
                        sleep(0.1)
                        Digit(digits[2], 0)
                        Digit(digits[4], 4)
                        Digit(digits[hh], 8)
                        sleep(0.2)
                        
                Reset()
            
            # otherwise, change brightness
            else:
                Brightness()
                break
            
        
def callback_button_x(pin):
    print('button X')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        global shift
        shift = ColorShift(shift, 20)
        Reset()

def callback_button_y(pin):
    print('button Y')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        global hr
        sleep(0.5)
        hr = hr + 1    
        Reset()
    
# i didn't write this function, but it helps prevent double button presses
def debounce(pin):
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

def Reset():
    ClearDisplay()
    DisplayHours()
    DisplayQuarters()

button_a.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_a)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_b)
button_x.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_x)
button_y.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_y)

Brightness(True)
HourTransition()
Reset()


while True:
    gc.collect()
    #print('Mem free: {} --- Mem allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))

    # runs once per second
    if currentSecond != rtc.get_seconds():
        print(hr, currentMinute, currentSecond)
        
        Pulse()
        currentSecond = rtc.get_seconds()
                
        # check minute        
        if rtc.get_minutes() != currentMinute:
            DisplayQuarters()
            
            currentMinute = rtc.get_minutes()
        
        # check hour  
        if rtc.get_hours() != currentHour:
            currentHour = rtc.get_hours()
            
            #TODO: replace
            hr = hr + 1
            
            HourTransition()
            DisplayQuarters()
        
        DisplayHours()

        gc.collect()
    else:
        pass