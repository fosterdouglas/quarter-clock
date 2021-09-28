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
currentDate = rtc.get_date()
currentMonth = rtc.get_month()

pulse = True
quarterOffsets = [0, 8, 10, 12, 14]

#TODO: reduce as many of these as possible
global currentQuarter
global brt #brightness
#global hr #hour
global hr12mode #24 or 12h clock
global hrdelta #difference in hours from system clock
global theme_hue
global theme_sat
global palette_list
global current_palette
global dst

currentQuarter = 0
brt = 0.8 #start brightness at one level down
hr = currentHour
hr12mode = False
hrdelta = 0
dst = 0

# using these instead of picounicorn's built in functions to be able to access IRQs
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# set up palettes
#TODO: do we actually need both of these?
palette_list = ['standard', 'chill']
current_palette = 0

standard_palette_hue = [323, 330, 340, 350, 0, 10, 15, 26, 38, 60, 98, 150, 170, 180, 190, 198, 225, 215, 242, 242, 270, 290, 305, 312]
standard_palette_sat = [0.81, 0.84, 0.85, 0.9, 0.83, 0.89 , 0.68, 0.9, 0.65, 0.55, 0.85, 0.93, 0.95, 0.40, 0.71, 0.65, 0.40, 0.71, 0.53, 0.89, 0.73, 0.89, 0.89, 0.89]

chill_palette_hue = []
chill_palette_sat = [1 for k in range(24)]
#TODO: make the chill palette's colors more dilberately?
for i in range(160, 256, 4):
    chill_palette_hue += [i]
        
theme_hue = standard_palette_hue
theme_sat = standard_palette_sat

# position coordinates from top left of the number
digits = [None] * 11
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

def get_palette_pos(val):
    if val > 23:
        val = val%24
        return val
    else:
        return val
    
def set_palette(name):
    global theme_hue
    global theme_sat
    
    if name == 'standard':
        theme_hue = standard_palette_hue
        theme_sat = standard_palette_sat
    elif name == 'chill':
        theme_hue = chill_palette_hue
        theme_sat = chill_palette_sat
    
    print('Change palette to: ' + str(name))
    
def set_current_quarter(val):
    global currentQuarter
    
    currentQuarter = val
    
def HourFormat(hour):
    # function to adjust global time to local time, considering user adjusted hours and DST
    localhour = hour + hrdelta + dst
    
    #format properly if 12h clock being used
    if hr12mode == True:
        localhour = localhour%12
        if localhour == 0:
            localhour = 12
            
    # resets the hour if it goes above 23 during user time setting
    if localhour > 23:
        localhour = localhour%24
    
    firstDigit, secondDigit = split_digit(localhour)
       
    return [firstDigit, secondDigit, localhour]

def split_digit(digit):
    if digit < 10:
        firstDigit = 0
        secondDigit = digit
    else:        
        firstDigit = math.floor(digit / 10)
        secondDigit = math.floor(digit % 10)
    return firstDigit, secondDigit

        
def Digit(num, offset, localhue=theme_hue[get_palette_pos(HourFormat(hr)[2])], localsat=theme_sat[get_palette_pos(HourFormat(hr)[2])]):
    for i in range(len(num)):
        x = num[i][0]        
        y = num[i][1]
        
        localvalue = VB(255, 50)
        r, g, b = Rainbow(localhue, localsat, localvalue)        
        picounicorn.set_pixel(x + offset, y, r, g, b)
            
def ClearDisplay():
    for x in range(w):
        for y in range(h):
            #draws "black" pixels
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
def Pillar(width, offset, localvalue, height=h, localhue=theme_hue[get_palette_pos(HourFormat(hr)[2])], localsat=theme_sat[get_palette_pos(HourFormat(hr)[2])]):
    r, g, b = Rainbow(localhue, localsat, localvalue)
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x + offset, y, r, g, b)

def Rainbow(hue, sat, val):
    # incoming values: hue is 0-360, sat is 0.0-1.0 and val is 0-255
    hue = (hue)%359
    hue = (hue)/360
    sat = sat
    
    #TODO: change all value and VB calls to be 0.0-1.0 range instead of 0-255, then remove this division
    val = val/255
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, sat, val)]
    return (r, g, b)

def Brightness(default=False):
    # function for changing the brightness by 1 level
    global brt
    
    if default == True or brt < 0.4:
        brt = 1.0
    else:
        brt = brt - 0.2
        
    print('Change brightness to : ' + str(brt))    

    Reset()
    sleep(0.1)

def VB(value, minimum=0):
    # function to handle variable brightness across anything drawn
    value = value * brt

    if value < minimum:
        value = minimum
        
    return int(value)

def Pulse():
    forwardhue = theme_hue[get_palette_pos(HourFormat(hr)[2]+1)]
    forwardsat = theme_sat[get_palette_pos(HourFormat(hr)[2]+1)]
    
    if currentQuarter == 1:
        localOffset = (currentSecond%6)+quarterOffsets[2]
    elif currentQuarter == 2:
        temp = (currentSecond%6)
        if temp == 0 or temp == 1:
            localOffset = (currentSecond%6)+quarterOffsets[1]
        else:
            localOffset = (currentSecond%6)+quarterOffsets[2]
    elif currentQuarter == 3:
        temp = (currentSecond%6)
        if temp == 4 or temp == 5:
            localOffset = (currentSecond%6)-4+quarterOffsets[4]
        else:
            localOffset = (currentSecond%6)+quarterOffsets[1]
    elif currentQuarter == 4:
        localOffset = (currentSecond%6)+quarterOffsets[1]
        
    for i in range(VB(50,25), VB(210, 120), 25):
        Pillar(1, localOffset, i, localhue=forwardhue, localsat=forwardsat)
        sleep(0.05)
    for i in reversed(range(VB(50,25), VB(210, 120), 25)):
        Pillar(1, localOffset, i, localhue=forwardhue, localsat=forwardsat)
        sleep(0.05)

def DisplayQuarters():
    flux = False
    
    # set the quarters hue to the upcoming hour's hue, for some visual contrast
    forwardhue = theme_hue[get_palette_pos(HourFormat(hr)[2]+1)]
    forwardsat = theme_sat[get_palette_pos(HourFormat(hr)[2]+1)]
    
    # check which quarter we are in
    if currentMinute <= 13 or currentMinute == 59:
        set_current_quarter(1)
    elif currentMinute >= 14 and currentMinute <= 28:
        set_current_quarter(2)
    elif currentMinute >= 29 and currentMinute <= 43:
        set_current_quarter(3)
    elif currentMinute >= 44 and currentMinute <= 58:
        set_current_quarter(4)
        
    if currentMinute == 14 or currentMinute == 29 or currentMinute == 44 or currentMinute == 59:
        flux = True
    
    # draw each of the 4 quarters
    for i in range(1,5):
        
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
    # function to display the main digits
    Digit(digits[HourFormat(hr)[0]], 0, localhue=theme_hue[get_palette_pos(HourFormat(hr)[2])], localsat=theme_sat[get_palette_pos(HourFormat(hr)[2])])
    Digit(digits[HourFormat(hr)[1]], 4, localhue=theme_hue[get_palette_pos(HourFormat(hr)[2])], localsat=theme_sat[get_palette_pos(HourFormat(hr)[2])])
    
def HourDelta(delta=1):
    # function for changing the hour by a set amount
    global hrdelta
    hrdelta = hrdelta + delta
    if hrdelta > 23:
        hrdelta = 0
        
def ToggleHR12Mode():
    # function for toggling 12-hour clock on or off
    global hr12mode
    hr12mode = not hr12mode
    print('Toggle 12/24h mode')

def dst_adjust():
    # function to determine if it's the date and time to change the clock automatically
    
    global dst
    
    #TODO: test this properly
    if currentMonth >= 11 or currentMonth <= 3:
        if currentMonth == 11 and currentDate >= 7:
            dst = 0
        elif currentMonth == 3 and currentDate <= 14:
            dst = 0      
        else:
            dst = 1
    else:
        dst = 1
                            
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
        exitLoop = False
        youwin = False
        sleep(0.5)
        while not exitLoop:
            print('Toggle disco mode')
            for i in range(32):
                if i < 16:
                    pos = i
                    hue = theme_hue[i]
                else:
                    pos = 31 - i
                    hue = theme_hue[i - 16]
 
                r, g, b = Rainbow(hue, 1.0, 220)
                
                for x in range(w):
                    for y in range(h):
                        picounicorn.set_pixel(pos, y, r, g, b)
                sleep(0.01)
                
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    # if you stop the bar in the very center you win
                    if i == 8:
                        youwin = True           
                    exitLoop = True
                    break
                sleep(1/1028)
            sleep(0.5)
                
        if youwin == True:

            # celebrate, you win! ... an animation
            for i in range(24): 
                for pos in range(16):

                    hue = random.randint(0,360)
                    sat = random.randint(70,100)/100
                    val = random.randint(50,255)
                    r, g, b = Rainbow(hue, sat, val)
                    for x in range(w):
                        for y in range(h):
                            picounicorn.set_pixel(pos, random.randint(0,6), r, g, b)
                sleep(0.05)
        Reset()

def callback_button_b(pin):
    print('Button B')
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
                if hr12mode:
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
            
            # if button is not held, changes brightness down by 0.2, then loops around to 1.0 brightness
            else:
                Brightness()
                break
            
        
def callback_button_x(pin):
    print('Button X')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        global current_palette
        current_palette = (current_palette + 1) % len(palette_list)
        set_palette(palette_list[current_palette])
        
        # change to new palette, then display palette color range
        for i in range(len(theme_hue)):
            
            ClearDisplay()
            if hr12mode:
                firstDigit, secondDigit = split_digit((i%12)+1)
            else:
                firstDigit, secondDigit = split_digit(i)

            Digit(digits[firstDigit], 0, localhue=theme_hue[i], localsat=theme_sat[i])
            Digit(digits[secondDigit], 4, localhue=theme_hue[i], localsat=theme_sat[i])
            
            for x in range(8, w):
                for y in range(h):
                    picounicorn.set_pixel(x, y, *Rainbow(theme_hue[get_palette_pos(i+1)], theme_sat[get_palette_pos(i+1)], brt*255))
            sleep(0.6)
        
        Reset()
        Reset()
        #TODO: something here to stop the nexttick Pulse from being the wrong color

def callback_button_y(pin):
    print('Button Y')
    d = debounce(pin)

    if d == None:
        return
    elif not d:
        sleep(0.5)
        HourDelta()
        Reset()
    
def debounce(pin):
    # function to help prevent button presses from debouncing
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

def Reset():
    # function to do a soft reset
    ClearDisplay()
    DisplayHours()
    DisplayQuarters()

# interrupt requests
button_a.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_a)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_b)
button_x.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_x)
button_y.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_y)

# one-time setup
Brightness(True)
dst_adjust()
HourTransition()
Reset()

while True:
    gc.collect()
    #print('Mem free: {} --- Mem allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))

    # runs once per second
    if currentSecond != rtc.get_seconds():
        print(HourFormat(hr)[2], currentMinute, currentSecond)
        
        Pulse()
        currentSecond = rtc.get_seconds()
                
        # check minute        
        if rtc.get_minutes() != currentMinute:
            DisplayQuarters()
            
            currentMinute = rtc.get_minutes()
        
        # check hour  
        if rtc.get_hours() != currentHour:
            currentHour = rtc.get_hours()
            
            dst_adjust()
            
            #TODO: is this the right thing to do here...
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