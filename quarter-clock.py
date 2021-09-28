import picounicorn
from utime import time, localtime, sleep
import math
import random
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
global hr12mode #24 or 12h clock
global hrdelta #difference in hours from system clock

currentQuarter = 0
brt = 0.8 #start brightness at one level down
hr = currentHour
shift = 0
hr12mode = False
hrdelta = 0

# using these instead of picounicorn's built in functions to be able to access IRQs
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

#TODO: turn all these into one function call, and then use button X to change themes
standard_theme_hue = [323, 330, 340, 350, 0, 17, 28, 40, 60, 98, 150, 170, 180, 190, 198, 225, 215, 242, 242, 270, 290, 305, 312]
standard_theme_sat = [0.81, 0.84, 0.85, 0.9, 0.73, 0.80, 0.68, 0.65, 0.55, 0.85, 0.93, 0.95, 0.40, 0.71, 0.65, 0.40, 0.71, 0.53, 0.89, 0.73, 0.89, 0.89, 0.89]
#another_theme_hue
#another_theme_sat

digits = [None] * 11

# position coordinates from top left of the number
digits[0] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[1] = [
            [2,0],
      [1,1],[2,1],
[0,2],      [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[2] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
[0,4],
[0,5],
[0,6],[1,6],[2,6]
]

digits[3] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digits[4] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[5] = [
[0,0],[1,0],[2,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digits[6] = [
[0,0],[1,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[7] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[8] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digits[9] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

digits[10] = [
[0,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

def Digit(num, offset):
    for i in range(len(num)):
        x = num[i][0]        
        y = num[i][1]
        
        #localhue = ColorShift(hours[hr][0], 10)
        localhue = standard_theme_hue[hr]
        localsat = standard_theme_sat[hr]
        localvalue = VB(255, 50)
        
        #shift position over by an offset number and draw pixels          
        picounicorn.set_pixel(x + offset, y, *Rainbow(localhue, localsat, localvalue))

            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            #draws "black" pixels
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
def Pillar(width, offset, localvalue, height=h, localhue=standard_theme_hue[hr], localsat=standard_theme_sat[hr]):
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x + offset, y, *Rainbow(localhue, localsat, localvalue))

def Rainbow(hue, sat, val):
    #hu is 0-360, sa is 0.0-1.0 and va is 0-255
    global shift
    hue = (hue + shift)%359
    hue = (hue)/360
    sat = sat
    
    #TODO: change all value and VB calls to be 0.0-1.0 range instead of 0-255, then remove this division
    val = val/255
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, sat, val)]
    return (r, g, b)

def TogglePalette():
    print('toggle palette')

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
    # variable brightness
    value = value * brt

    if value < minimum:
        value = minimum
        
    return int(value)

def Pulse():
    global hr
    
    #TODO: maybe replace this with a function, it's used three times kind of
    if hr == 23:
        forwardhue = standard_theme_hue[0]
        forwardsat = standard_theme_sat[0]
    else:
        forwardhue = standard_theme_hue[hr+1]
        forwardsat = standard_theme_sat[hr+1]
    
    
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
        Pillar(1, localOffset, i, localhue=forwardhue, localsat=forwardsat)
        sleep(0.05)
    for i in reversed(range(VB(50,25), VB(210, 120), 25)):
        Pillar(1, localOffset, i, localhue=forwardhue, localsat=forwardsat)
        sleep(0.05)

def DisplayQuarters():
    global currentQuarter
    global hr
    flux = False
    
    #TODO: replace
    if hr == 23:
        forwardhue = standard_theme_hue[0]
        forwardsat = standard_theme_sat[0]
    else:
        forwardhue = standard_theme_hue[hr+1]
        forwardsat = standard_theme_sat[hr+1]
    
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
                    Pillar(2, quarterOffsets[i], desc, localhue=forwardhue, localsat=forwardsat)
                    sleep(0.02)
                for asc in range(VB(34,0), VB(204, 100), 17):  
                    Pillar(2, quarterOffsets[i], asc, localhue=forwardhue, localsat=forwardsat)
                    sleep(0.02)
                    
                Pillar(2, quarterOffsets[i], VB(240, 80), localhue=forwardhue, localsat=forwardsat)
                
            # animate for each quarter change
            if flux == True:
                
                if i > 0:
                    Pillar(2, quarterOffsets[i - 1], VB(240, 80), localhue=forwardhue, localsat=forwardsat)
                    
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[i - 1], 0, off + 1, localhue=forwardhue, localsat=forwardsat)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    Pillar(2, quarterOffsets[i - 1], VB(50, 25), localhue=forwardhue, localsat=forwardsat,)
                    
                     #animate next quarter over
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[i], VB(240, 80), on + 1, localhue=forwardhue, localsat=forwardsat,)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[i], VB(240, 80), localhue=forwardhue, localsat=forwardsat)
                else:
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(h):
                        Pillar(2, quarterOffsets[3], 0, off + 1, localhue=forwardhue, localsat=forwardsat)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    Pillar(2, quarterOffsets[3], VB(50, 25), localhue=forwardhue, localsat=forwardsat)
                    
                    # otherwise, animate the first quarter   
                    print('next quarter on')
                    for on in range(h):
                        Pillar(2, quarterOffsets[0], VB(240, 80), on + 1, localhue=forwardhue, localsat=forwardsat)
                        sleep(0.03)
                    Pillar(2, quarterOffsets[0], VB(240, 80), localhue=forwardhue, localsat=forwardsat)
        
        # for the other 3 faded quarters
        else:
            Pillar(2, quarterOffsets[i], VB(50, 25), localhue=forwardhue, localsat=forwardsat)
        
def DisplayHours():
    # display main digits
    Digit(digits[HourFormat()[0]], 0)
    Digit(digits[HourFormat()[1]], 4)
    
def HourDelta():
    global hrdelta
    hrdelta = hrdelta + 1
    if hrdelta > 23:
        hrdelta = 0
        
def ToggleHR12Mode():
    global hr12mode
    hr12mode = not hr12mode
            
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
    global hrdelta
    
    localhour = hr + hrdelta
    
    #format properly if 12h clock being used
    if hr12mode == True:
        localhour = localhour%12
        if localhour == 0:
            localhour = 12
            
    # resets the hour if it goes above 23 during user time setting
    if localhour > 23:
        localhour = localhour%24
    
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
        youwin = False
        sleep(0.5)
        while not exitLoop:
            for i in range(16):
                
                #TODO: use Rainbow() here?
                hue = (standard_theme_hue[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(i, y, r, g, b)
                sleep(0.01)
                
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    # if you stop the bar in the very center you win
                    if i == 8:
                        youwin = True           
                    exitLoop = True
                    break
                
            for i in range(16):
                
                #TODO: use Rainbow() here?
                hue = (standard_theme_hue[i])/360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 0.8)]
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(15-i, y, r, g, b)
                sleep(0.01)
                
                #TODO: move this and the above to a single for loop of 32 to optimize
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    # if you stop the bar in the very center you win
                    if i == 8:
                        youwin = True
                    exitLoop = True
                    break
                
            sleep(0.5)
        if youwin == True:

            # celebrate, you win! ... an animation
            for f in range(20): #flashing
                
                for a in range(16): #color changes
                    #TODO: use Rainbow() here?
                    hue = (f + (a*random.randint(4,8)))/360
                    sat = random.randint(0,100)/100
                    val = random.randint(0,10)/10
                    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, sat, val)]
                    for x in range(w):
                        for y in range(h):
                            picounicorn.set_pixel(a, random.randint(0,6), r, g, b)
                    sleep(0.005)
                sleep(0.04)
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
                ToggleHR12Mode()
                
                ClearDisplay()
                
                # animation to show new hour format 
                if hr12:
                    for f in range (6):
                        # draw blank first
                        Pillar(12, 0, 0)
                        sleep(0.1)
                        Digit(digits[1], 0)
                        Digit(digits[2], 4)
                        Digit(digits[10], 8)
                        sleep(0.2)
                        
                else:
                    for f in range (6):
                        # draw blank first
                        Pillar(12, 0, 0)
                        sleep(0.1)
                        Digit(digits[2], 0)
                        Digit(digits[4], 4)
                        Digit(digits[10], 8)
                        sleep(0.2)
                        
                Reset()
            
            # otherwise, button changes brightness down by 1 level, of 5, then loops around
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
        #shift = ColorShift(shift, 20)
        Reset()

def callback_button_y(pin):
    print('button Y')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        sleep(0.5)
        HourDelta()
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
    
#     for i in range(len(standard_theme_hue)):
#         localhue = standard_theme_hue[i]
#         localsat = standard_theme_sat[i]
#         
#         print(i+1)
#         
#         for x in range(w):
#             for y in range(h):
#                 picounicorn.set_pixel(x, y, *Rainbow(localhue, localsat, 255))
#         sleep(0.2)

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
            
            hr = hr + 1
            
            HourTransition()
            DisplayQuarters()
        
        DisplayHours()

        gc.collect()
    else:
        pass

#cool color fading chill animation to use for later
# for r in range(2): #do it twice
#     for f in range(10): #flashing
#         
#         #ClearDisplay()
#         for a in range(16): #color changes
#             #TODO: use Rainbow() here?
#             hue = (hours[f] + (a*2))/360
#             r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, a/15, 0.8)]
#             for x in range(w):
#                 for y in range(h):
#                     picounicorn.set_pixel(a, y, r, g, b)
#             sleep(0.1)
        sleep(0.2)