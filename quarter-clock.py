import picounicorn
from machine import Pin
from machine import ADC
from utime import sleep
from utime import localtime
import math
from random import uniform
from random import randrange
from random import randint
import gc
import rv3028_rtc

picounicorn.init()

display_width = picounicorn.get_width()
display_height = picounicorn.get_height()

# initalize the RV3028 RTC unit
i2c=machine.I2C(1,sda=Pin(26), scl=Pin(27), freq=100000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

# read the RV3028
gmt_sec = rtc.get_seconds()
gmt_min = rtc.get_minutes()
gmt_date = rtc.get_date()
gmt_month = rtc.get_month()
local_hr = rtc.get_hours()

light_sensor = machine.ADC(28)

global global_brt #brightness
global hr24_mode #24h display style
global dst_mode #DST enabled or disabled
global hr_delta #difference in hours from system clock
global theme_hue
global theme_sat
global palette_list
global current_palette
global dst_delta
global current_mode
global current_option
global current_visual
global option_list
global next_hue
global next_sat
global configuration_increment
global configuration_step
global configuration_value

global_brt = 0.8 #brightness from 0.4 to 1.0
hr24_mode = True
hr_delta = 0
dst_delta = 0
dst_mode = True
brightness_override = False
quarter_positions = [0, 8, 10, 12, 14] 
current_palette = 0
current_mode = 0
current_option = 0
option_list = ['HUR', 'DST', 'BRT', 'COL', '24H']
visual_list = ['DISCO', 'MATRIX', 'DIAGONAL', 'DOTS']
current_visual = -1
next_hue = 0
next_sat = 0
configuration_increment = 0
configuration_step = 0
configuration_value = 0

diagonal_increment = 0
dots_increment = -1

# Create X,Y map of display's pixel locations
display_coordinates = []
for x in range(display_width):
    for y in range (display_height):
        display_coordinates.append([x, y])

# Button Setup
## (explicit, instead of using picounicorn's built-in functions, to be able to access IRQs)
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# Generate Color Palettes
## Rainbow
rainbow_palette_hue = [323, 330, 340, 350, 0, 10, 15, 26, 38, 60, 98, 150, 170, 180, 190, 198, 225, 215, 242, 242, 270, 290, 305, 312]
rainbow_palette_sat = [0.81, 0.84, 0.85, 0.9, 0.83, 0.89 , 0.68, 0.9, 0.65, 0.55, 0.85, 0.93, 0.95, 0.40, 0.71, 0.65, 0.40, 0.71, 0.53, 0.89, 0.73, 0.89, 0.89, 0.89]

## Chill
chill_palette_hue = []
chill_palette_sat = [1 for k in range(24)]
for i in range(240, 256, 4): #first 17 colors
    chill_palette_hue += [i]
for i in range(256, 184, -12): #last 6 colors, loop back through same values to return to same starting point
    chill_palette_hue += [i]
for i in range(184, 240, 4): #first 17 colors
    chill_palette_hue += [i]

## Fire & Ice
fire_ice_palette_hue = [359, 353, 347, 341, 335, 323, 317, 300, 287, 281, 275, 269, 263, 239, 233, 227, 239, 269, 281, 305, 320, 330, 340, 350]
fire_ice_palette_sat = [1 for k in range(24)]
        
theme_hue = rainbow_palette_hue
theme_sat = rainbow_palette_sat

# Arrays To Draw Numbers
digit_list = [None] * 11
digit_list[0] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digit_list[1] = [
            [2,0],
      [1,1],[2,1],
[0,2],      [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digit_list[2] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
[0,4],
[0,5],
[0,6],[1,6],[2,6]
]

digit_list[3] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digit_list[4] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

digit_list[5] = [
[0,0],[1,0],[2,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],[2,6]
]

digit_list[6] = [
[0,0],[1,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digit_list[7] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
            [2,3],
            [2,4],
            [2,5],
            [2,6]
]

digit_list[8] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

digit_list[9] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

# Arrays To Draw Needed Symbols
symbol_list = [None] * 7

# Carat Up
symbol_list[0] = [
      [1,0],
[0,1],      [2,1],
]

# Carat Down
symbol_list[1] = [
[0,5],      [2,5],
      [1,6],
]

# Carat Right
symbol_list[2] = [
      [1,4],
           [2,5],
      [1,6],
]

# Carat Left
symbol_list[3] = [
      [2,0],
[1,1],
      [2,2],
]

# Question Mark
symbol_list[4] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
            [2,2],
      [1,3],
      [1,4],

      [1,6]
]

# Rect
symbol_list[5] = [
      [1,4],[2,4],
      [1,5],[2,5],
      [1,6],[2,6]
]

# Carat Right Alt
symbol_list[6] = [
      [1,0],
           [2,1],
      [1,2],
]

# Arrays To Draw Needed Letters (and numbers as strings)
letter_list = [None] * 32

letter_list[1] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

#B
letter_list[2] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

#C
letter_list[3] = [
[0,0],[1,0],[2,0],
[0,1],      
[0,2],      
[0,3],      
[0,4],      
[0,5],     
[0,6],[1,6],[2,6]
]

#D
letter_list[4] = [
[0,0],[1,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],
]

#E
letter_list[5] = [
[0,0],[1,0],[2,0],
[0,1],      
[0,2],      
[0,3],[1,3],[2,3],
[0,4],      
[0,5],      
[0,6],[1,6],[2,6]
]

#F
letter_list[6] = [
[0,0],[1,0],[2,0],
[0,1],      
[0,2],      
[0,3],[1,3],[2,3],
[0,4],      
[0,5],     
[0,6],
]

#H
letter_list[8] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

#I
letter_list[9] = [
[0,0],     
[0,1],     
[0,2],     
[0,3],
[0,4],      
[0,5],     
[0,6],      
]

#K
letter_list[11] = [
[0,0],      [2,0], 
[0,1],[1,1],      
[0,2],
[0,3],
[0,4],
[0,5],[1,5],
[0,6],      [2,6],
]

#L
letter_list[12] = [
[0,0],
[0,1],      
[0,2],      
[0,3],     
[0,4],      
[0,5],      
[0,6],[1,6],[2,6]
]

#M
letter_list[13] = [
[0,0],                  [4,0],
      [1,1],      [3,1],
[0,2],      [2,2],      [4,2],
[0,3],                  [4,3],
[0,4],                  [4,4],
[0,5],                  [4,5],
[0,6],                  [4,6]
]   

#N
letter_list[14] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

#O
letter_list[15] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

#R
letter_list[18] = [
[0,0],[1,0],[2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

#S
letter_list[19] = [
      [1,0],[2,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
[0,6],[1,6],
]

#T
letter_list[20] = [
[0,0],[1,0],[2,0],
      [1,1],
      [1,2],
      [1,3],
      [1,4],
      [1,5],
      [1,6]
]

#U
letter_list[21] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],      [2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],[1,6],[2,6]
]

letter_list[25] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
      [1,3],
      [1,4],
      [1,5],
      [1,6]
]

# 2 (for string use)
letter_list[29] = [
[0,0],[1,0],[2,0],
            [2,1],
            [2,2],
[0,3],[1,3],[2,3],
[0,4],
[0,5],
[0,6],[1,6],[2,6]
]

# 4 (for string use)
letter_list[31] = [
[0,0],      [2,0],
[0,1],      [2,1],
[0,2],      [2,2],
[0,3],[1,3],[2,3],
            [2,4],
            [2,5],
            [2,6]
]

# To Check And Adjust Brightness Based On Ambient Light
def ambient_light_adapt():
    global global_brt
    
    # Read Ambient Light Sensor
    ambient_light = light_sensor.read_u16()
    ambient_light = round(ambient_light, -3)
    
    # Adjust Global Brightness
    if not brightness_override:
        brt = global_brt
        if ambient_light > 30000 and global_brt != 1.0:
            print('max: ' + str(ambient_light))
            global_brt = 1.0
        elif ambient_light > 20000 and ambient_light <= 30000 and global_brt != 0.8:
            print('high: ' + str(ambient_light))
            global_brt = 0.8
        elif ambient_light > 1000 and ambient_light <= 20000 and global_brt != 0.6:
            print('low: ' + str(ambient_light))
            global_brt = 0.6
        elif ambient_light <= 1000 and global_brt != 0.4:
            print('min: ' + str(ambient_light))
            global_brt = 0.4

        # If Brightness Did Change, Reset
        if global_brt != brt:
            soft_reset()

def get_palette_pos(val):
    if val > 23:
        val = val%24
        return val
    else:
        return val
    
def incr_palette():
    global theme_hue
    global theme_sat
    global current_palette

    # Increment To Next Palette
    current_palette = (current_palette + 1) % 3

    if current_palette == 0:
        theme_hue = rainbow_palette_hue
        theme_sat = rainbow_palette_sat
    elif current_palette == 1:
        theme_hue = chill_palette_hue
        theme_sat = chill_palette_sat
    elif current_palette == 2:
        theme_hue = fire_ice_palette_hue
        theme_sat = fire_ice_palette_sat
    
    print('Changed palette to: ' + str(current_palette))

# To showcase the palette color range
def showcase_palette():
    for i in range(len(theme_hue)):
        
        clear_display()

        draw_character(digit_list[format_hour(i)[0]], 0, local_hue=theme_hue[i], local_sat=theme_sat[i])
        draw_character(digit_list[format_hour(i)[1]], 4, local_hue=theme_hue[i], local_sat=theme_sat[i])
        
        for x in range(8, display_width):
            for y in range(display_height):
                picounicorn.set_pixel(x, y, *convert_color(theme_hue[get_palette_pos(i+1)], theme_sat[get_palette_pos(i+1)], global_brt*255))
        sleep(0.25)
    
def format_hour(hour):
    # function to adjust global time to local time, considering user adjusted hours
    formatted_hour = hour + hr_delta
    
    # apply DST adjustment if enabled
    if dst_mode:
        formatted_hour = formatted_hour + dst_delta
        
    # resets the hour if it goes above 23 during user time setting
    if formatted_hour > 23:
        formatted_hour = formatted_hour%24
    
    # split the hour into two spearate digits
    first_digit, second_digit = split_digit(formatted_hour)
    
    #format properly if 24h clock is not being used
    if hr24_mode == False:
        local_hour = formatted_hour%12
        if local_hour == 0:
            local_hour = 12
        first_digit, second_digit = split_digit(local_hour)
       
    return [first_digit, second_digit, formatted_hour]

# To Adjust Brightness Of Anything Drawn 
def variable_brightness(maximum, minimum=0):
    maximum = maximum * global_brt

    if maximum < minimum:
        maximum = minimum
        
    return int(maximum)

# To Format A Double-Digit Hour Into Two Individual Digits
def split_digit(digit):
    if digit < 10:
        first_digit = 0
        second_digit = digit
    else:        
        first_digit = math.floor(digit / 10)
        second_digit = math.floor(digit % 10)
    return first_digit, second_digit

# To Draw A Character    
def draw_character(char, offset, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])], local_val=variable_brightness(255, 50)):
    for i in range(len(char)):
        x = char[i][0]        
        y = char[i][1]
        
        r, g, b = convert_color(local_hue, local_sat, local_val)        
        picounicorn.set_pixel(x + offset, y, r, g, b)

# To Draw A String
def draw_string(string, offset=0, colored=True):

    string = string.upper()
    string_map = []
    for char in string:
        if ord(char) > 47 and ord(char) < 58:
            delta = 21 # to map string values 0-9 to array values 27-36
        else:
            delta = 64 # To map string values A-Z to array values 1-26

        string_map.append(ord(char) - delta) 

    i = 0
    for pos in string_map:
        if colored == True:
            draw_character(letter_list[pos], (i*4)+offset)
        else:
            # Option To Override Color To White, For Contrast/Distinction Uses
            draw_character(letter_list[pos], (i*4)+offset, local_hue=0, local_sat=0, local_val=255)
        i = i + 1

# To draw the carats used in Configuration mode
def draw_carats():
    draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
    draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
    draw_character(symbol_list[2], 13, local_hue=330, local_sat=1, local_val=150)

# To Draw An Empty Display
def clear_display(width=display_width, height=display_height):
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x, y, 0, 0, 0)

# To Draw Light Points And Lines To The Display           
def draw(width, height, offset_x, offset_y, local_val, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])]):
    # TODO: Update parameter "local_val" to new position at end and give default value
    r, g, b = convert_color(local_hue, local_sat, local_val)
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x + offset_x, y + offset_y, r, g, b)

# To visually blink a string
def blink_string(string):
    for i in range(3):
        clear_display()
        draw_string(string)
        sleep(0.2)
        clear_display()
        sleep(0.1)
    sleep(0.1)

# To visually blink the current time
def blink_time():
    for i in range(3):
        clear_display()
        draw_character(digit_list[format_hour(local_hr)[0]], 0, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])], local_val=variable_brightness(255, 100))
        draw_character(digit_list[format_hour(local_hr)[1]], 4, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])], local_val=variable_brightness(255, 100))
        update_next_hue()
        sleep(0.2)
        clear_display()
        sleep(0.1)
    sleep(0.1)

def convert_color(hue, sat, val):
    # Incoming values: hue is 0-360, sat is 0.0-1.0 and val is 0-255
    hue = (hue)%359
    hue = (hue)/360
    sat = sat
    
    #TODO: change all value and VB calls to be 0.0-1.0 range instead of 0-255, then remove this division
    val = val/255
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, sat, val)]
    return (r, g, b)

# To increment brightness by some amount
def change_brightness(delta):
    # Delta value should be a small value, like 0.1/-0.1
    global global_brt
    global brightness_override

    brightness_override = True
    global_brt = round(global_brt, 1) + (round(delta, 1))

    if global_brt > round(1.0, 1):
        global_brt = round(0.4, 1)
    
    if global_brt < round(0.4, 1):
        global_brt = round(1.0, 1)
        
    print('Change brightness to : ' + str(global_brt))    

# To animate the seconds indicator
def seconds_pulse():
    local_offset_x = ((gmt_sec%4)*2)+8

    draw(8, 1, 8, 3, variable_brightness(50,25), local_hue=next_hue, local_sat=next_sat)
        
    for i in range(variable_brightness(50,25), variable_brightness(210, 80), 25):
        draw(2, 1, local_offset_x, 3, i, local_hue=next_hue, local_sat=next_sat)
        sleep(0.05)
    for i in reversed(range(variable_brightness(50,25), variable_brightness(210, 80), 25)):
        draw(2, 1, local_offset_x, 3, i, local_hue=next_hue, local_sat=next_sat)
        sleep(0.05)

# To draw quarter sections
def draw_quarters():

    if gmt_min <= 14:
        draw(2, 3, 8, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
    elif gmt_min >= 15 and gmt_min <= 29:
        draw(2, 3, 8, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 10, 0, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
    elif gmt_min >= 30 and gmt_min <= 44:
        draw(2, 3, 8, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 10, 0, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 12, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
    elif gmt_min >= 45:
        draw(2, 3, 8, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 10, 0, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 12, 4, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)
        draw(2, 3, 14, 0, variable_brightness(140, 40), local_hue=next_hue, local_sat=next_sat)             
        
#  To display the hour digits        
def display_hours():
    draw_character(digit_list[format_hour(local_hr)[0]], 0, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])], local_val=variable_brightness(255, 100))
    draw_character(digit_list[format_hour(local_hr)[1]], 4, local_hue=theme_hue[get_palette_pos(format_hour(local_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(local_hr)[2])], local_val=variable_brightness(255, 100))

# To change the hour by some amount, measured by the change from the global time    
def incr_hour(delta=1):
    global local_hr

    current_time = rtc.get_hours()
    new_time = current_time + delta
    if new_time > 23:
        new_time = 0
    rtc.set_hours(new_time)
    local_hr = rtc.get_hours()

# To move through the configuration steps
def incr_configuration_step():
    global configuration_step

    configuration_step += 1
    draw_character(symbol_list[2], 13, local_hue=140, local_sat=0.9, local_val=200)
    sleep(0.3)

def change_configuration_value(maximum, minimum=0, delta=1, offset=0):
    global configuration_value   
                
    configuration_value = configuration_value + delta

    if configuration_value > maximum:
        configuration_value = (0 + minimum)
    
    if configuration_value < (0 + minimum):
        configuration_value = maximum

    first_digit, second_digit = split_digit(configuration_value)

    for i in range(2):
        draw_character(digit_list[first_digit], offset, local_hue=140, local_sat=0.9, local_val=200)
        draw_character(digit_list[second_digit], offset+4, local_hue=140, local_sat=0.9, local_val=200)

        if configuration_step == 1:
            draw_character(digit_list[2], 0, local_hue=140, local_sat=0.9, local_val=200)
            draw_character(digit_list[0], 4, local_hue=140, local_sat=0.9, local_val=200)
        sleep(0.1)
        clear_display()
        sleep(0.05)

# To toggle 24-hour clock      
def toggle_24hour_mode():
    global hr24_mode

    hr24_mode = not hr24_mode
    print('Toggle 24h mode')
    
def toggle_dst_mode():
    global dst_mode
    dst_mode = not dst_mode

def toggle_brightness_mode():
    global brightness_override
    brightness_override = not brightness_override

# To determine if it's the date and time to change the clock automatically
def check_dst():
    global dst_delta
    
    # (if it's nov - mar )
    if gmt_month >= 11 or gmt_month <= 3:
        
        # (if it is exactly nov and is the 7th or later)
        if gmt_month == 11 and gmt_date >= 7:
            dst_delta = 0

        # (if it is exactly mar and is the 14th or earlier)
        elif gmt_month == 3 and gmt_date <= 14:
            dst_delta = 0

        # (if it is the other months between nov and mar)
        elif gmt_month != 3 or gmt_month != 11:
            dst_delta = 0
        print('DST is not happening')

    else:

        # (if it is the rest of the year)
        dst_delta = 1
        print('DST is happening')   

# Animation when changing hours                            
def hour_transition():
    for i in range(display_width/2):
        fade = variable_brightness(30, 0) + (i*variable_brightness(20, 10))
        draw(1, 7, (math.ceil(display_width/2)) + i, 0, fade)
        draw(1, 7, (math.floor(display_width/2)-1) - i, 0, fade)
        sleep(1/display_width)
    for i in range(display_width/2):
        fade = max(0, (variable_brightness(255, 100) - (i*variable_brightness(40, 20))))
        draw(1, 7, (math.ceil(display_width/2)) + i, 0, fade)
        draw(1, 7, (math.floor(display_width/2)-1) - i, 0, fade)
        sleep(1/display_width)
    for i in range(display_width/2):
        fade = max(0, (variable_brightness(255, 100) - (i*variable_brightness(40, 20))))
        draw(1, 7, (math.ceil(display_width/2)) + i, 0, fade)
        draw(1, 7, (math.floor(display_width/2)-1) - i, 0, fade)
        draw(1, 7, (math.ceil(display_width/2)+1) + (i-1), 0, 0)
        draw(1, 7, (math.floor(display_width/2)-1) - (i), 0, 0)
        sleep(1/display_width)

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

# To Cycle Through Modes  
def cycle_current_mode():
    global current_mode
    current_mode = (current_mode + 1) % 2
    clear_display()

    print('Mode: ' + str(current_mode))

# To set a specific mode  
def set_current_mode(mode_number):
    global current_mode

    current_mode = mode_number
    print('Mode: ' + str(current_mode))

    clear_display()  

# To cycle through options  
def cycle_current_option(val):
    global current_option

    current_option = (current_option + val) % len(option_list)

    if current_option == -1:
        current_option = len(option_list)

    print('Option: ' + option_list[current_option])  

# To cycle through visuals  
def cycle_current_visual(val, reset=False):
    global current_visual

    current_visual = (current_visual + val) % len(visual_list)

    if reset == True:
        current_visual = -1

    print('Visual: ' + visual_list[current_visual])  

# To Update Next Hue (Used For Visual Contrast)
def update_next_hue():
    global next_hue
    global next_sat
    
    next_hue = theme_hue[get_palette_pos(format_hour(local_hr)[2]+1)]
    next_sat = theme_sat[get_palette_pos(format_hour(local_hr)[2]+1)]

# A -- Visualizations  
def callback_button_a(pin):
    print('Visualizations')

    d = check_debounce(pin)
    if d == None:
        return
    elif not d:
        # Quarter-Clock Mode
        if current_mode == 0:

            if current_visual == 3:
                cycle_current_visual(1, reset=True)
            else:
                cycle_current_visual(1)

            clear_display()

        # Configuration Mode
        elif current_mode == 100:
            # Year
            if configuration_step == 1:
                draw_character(symbol_list[0], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=99, delta=1, offset=8)

            # Month
            if configuration_step == 2:
                draw_character(symbol_list[0], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=12, minimum=1, delta=1)

            # Day
            if configuration_step == 3:
                draw_character(symbol_list[0], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=31, minimum=1, delta=1)

            # Hours
            if configuration_step == 5:
                draw_character(symbol_list[0], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=23, delta=1)

            # Minutes
            if configuration_step == 6:
                draw_character(symbol_list[0], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[1], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=59, delta=1)

# B -- Options
def callback_button_b(pin):
    print('Options')

    d = check_debounce(pin)
    if d == None:
        return
    elif not d:
        if current_visual < 0 and current_mode != 100:
            cycle_current_mode()

        if current_mode == 100:
            # Year
            if configuration_step == 1:
                draw_character(symbol_list[1], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=99, delta=-1, offset=8)

            # Month
            if configuration_step == 2:
                draw_character(symbol_list[1], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=12, minimum=1, delta=-1)

            # Day
            if configuration_step == 3:
                draw_character(symbol_list[1], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=31, minimum=1, delta=-1)

            # Hours
            if configuration_step == 5:
                draw_character(symbol_list[1], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=23, delta=-1)

            # Minutes
            if configuration_step == 6:
                draw_character(symbol_list[1], 0, local_hue=140, local_sat=0.9, local_val=200)
                draw_character(symbol_list[0], 0, local_hue=330, local_sat=1, local_val=150)
                sleep(0.3)

                clear_display()
                change_configuration_value(maximum=59, delta=-1)
            
# X -- Brightness / Switch Option      
def callback_button_x(pin):
    print('Brightness / Switch Option')

    d = check_debounce(pin)
    if d == None:
        return
    elif not d:

        # To check if the button is held for 10 seconds
        while picounicorn.is_pressed(picounicorn.BUTTON_X):
            global configuration_increment
            global configuration_step
            configuration_increment += 1
            sleep(0.1)

            if configuration_increment > 100:
                set_current_mode(100)
                print('Configuration Mode')
                break

        # Quarter-Clock Mode
        if current_mode == 0:
            change_brightness(0.1)
            soft_reset()
        
        # Options Mode
        elif current_mode == 1:
            clear_display(width=12, height=7)

            # Draw over the carat with white temporarily
            draw_character(symbol_list[6], 12, local_hue=0, local_sat=0, local_val=255)
            sleep(0.25)
            clear_display(width=12, height=7)

            cycle_current_option(1)

            #Redraw option name
            draw_string(option_list[current_option], colored=False)

        elif current_mode == 100:
            # Restart the resetting process
            if configuration_step == 7:
                configuration_step = 0

# Y -- Color Theme / Edit Option
def callback_button_y(pin):
    print('Color Theme / Edit Option')

    d = check_debounce(pin)
    if d == None:
        return
    elif not d:
        # Quarter-Clock Mode
        if current_mode == 0:
            incr_palette()

            if current_visual == 3:
                sleep(0.3)
                clear_display()
        
        # Options Mode
        elif current_mode == 1:
            clear_display(width=12, height=7)

            # Draw over the carat with white temporarily
            draw_character(symbol_list[5], 12, local_hue=0, local_sat=0, local_val=255)
            sleep(0.25)
            clear_display(width=12, height=7)

            # Hour (Option 0)
            if current_option == 0:
                incr_hour()
                blink_time()

            # Daylight Savings Time (Option 1)
            elif current_option == 1:
                toggle_dst_mode()
                check_dst()

                if dst_mode == True: 
                    blink_string("AUTO")
                else:
                    blink_string("OFF")

                display_hours()
                draw_string("DST")

            # Auto-Brightness (Option 2)
            elif current_option == 2:

                toggle_brightness_mode()

                if brightness_override == True: 
                    blink_string("OFF")
                else:
                    blink_string("AUTO")

                draw_string("BRT")

            # Color Theme (Option 3)
            elif current_option == 3:
                incr_palette()
                showcase_palette()

            # 24H Display Style (Option 4)
            elif current_option == 4:
                toggle_24hour_mode()
                
                clear_display()
                if hr24_mode == True:
                    blink_string("ON")
                else:
                    blink_string("OFF")

                draw_string("DST")
            
            clear_display()

            #Redraw option name
            draw_string(option_list[current_option], colored=False)

        elif current_mode == 100:
            incr_configuration_step()

# Prevent button presses from debouncing    
def check_debounce(pin):
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

# Facimile of random.shuffle()
def random_shuffle(seq):
    l = len(seq)
    for i in range(l):
        j = randrange(l)
        seq[i], seq[j] = seq[j], seq[i]

# To Soft Reset
def soft_reset():
    clear_display()
    check_dst()
    display_hours()
    draw_quarters()

# Interrupt Request Setup
button_a.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_a)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_b)
button_x.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_x)
button_y.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_y)

# Initial Setup
update_next_hue()
check_dst()
hour_transition()
soft_reset()

while True:
    gc.collect()
    #print('Mem free: {} --- Mem allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))

    # Quarter-Clock (Mode 0)
    while current_mode == 0:
        # If Second Has Changed
        if gmt_sec != rtc.get_seconds():
            gmt_sec = rtc.get_seconds()
            seconds_pulse()
            ambient_light_adapt()
                    
            # If Minute Has Changed        
            if rtc.get_minutes() != gmt_min:
                gmt_min = rtc.get_minutes()
            
            # If Hour Has Changed  
            if rtc.get_hours() != local_hr:
                local_hr = rtc.get_hours()
                
                check_dst()
                hour_transition()

            print(format_hour(local_hr)[2], gmt_min, gmt_sec)

            draw_quarters()
            display_hours()

            gc.collect()
        else:
            pass
        update_next_hue()

        # Visuals
        while current_visual > -1:
            clear_display()

            # To keep track of when the visual changes, for resetting purposes
            vis_delta = current_visual

            # Disco (Vis 0)
            while current_visual == 0:
                for i in range(32):

                    # Left Side Colors
                    if i < 16:
                        pos = i
                        hue = theme_hue[i]

                    # Reversed For Right Side Colors
                    else:
                        pos = 31 - i
                        hue = theme_hue[i - 16]
                        
                    r, g, b = convert_color(hue, 1.0, variable_brightness(220, 150))
                    
                    for x in range(display_width):
                        for y in range(display_height):
                            picounicorn.set_pixel(pos, y, r, g, b)
                    sleep(1/34)
                sleep(0.5)

            if vis_delta != current_visual:
                clear_display()
                vis_delta = current_visual

            # Matrix (Vis 1)
            while current_visual == 1:
                odds = [1,3,5,7,9,11,13,15]

                for i in range(110):

                    hue = theme_hue[(i*10)%23]
                    sat = uniform(0.8, 1.0)
                    val = variable_brightness(200, 160)

                    r,g,b = convert_color(hue, sat, val)

                    for x in range(display_width):
                        for y in range(display_height):
                            picounicorn.set_pixel(((i*10)%16), ((i*10)%7), r, g, b)
                            picounicorn.set_pixel(odds[i%8], y, 0, 0, 0)

            if vis_delta != current_visual:
                clear_display()
                vis_delta = current_visual

            # Diag (Vis 2)
            while current_visual == 2:
                diagonal_increment += 1
                
                if diagonal_increment > 100000:
                    diagonal_increment = 0

                hue = theme_hue[diagonal_increment%23]
                sat = uniform(0.8, 1.0)
                val = variable_brightness(200, 160)

                r,g,b = convert_color(hue, sat, val)

                for x in range(display_width):
                    for y in range(display_height):

                        picounicorn.set_pixel(((diagonal_increment)%16), ((diagonal_increment)%7), r, g, b)
            
            if vis_delta != current_visual:
                clear_display()
                diagonal_increment = 0
                vis_delta = current_visual

            # Dots (Vis 3)
            while current_visual == 3:

                # Create array            
                if dots_increment == -1:
                    shuf_up = display_coordinates
                    shuf_down = display_coordinates

                    # Randomize the order of on/off 
                    random_shuffle(shuf_up)
                    random_shuffle(shuf_down)

                    dots_coordinates = shuf_up + shuf_down

                dots_increment += 1

                if dots_increment == len(dots_coordinates):
                    dots_increment = -1
                    print('Reset Counter')    

                hue = theme_hue[dots_increment%23]

                # Lights on
                if dots_increment < len(dots_coordinates)/2:
                    sat = uniform(0.6, 1.0)
                    val = randint(variable_brightness(30,15), variable_brightness(250, 200))

                    # Fade/ramp the light up
                    for i in reversed(range(1,10)):
                        r,g,b = convert_color(hue, sat, (1/i)*val)
                        picounicorn.set_pixel(dots_coordinates[dots_increment][0], dots_coordinates[dots_increment][1], r, g, b)
                        sleep(0.03)

                # Lights off
                else:
                    sat = uniform(0.4, 0.6)
                    val = randint(variable_brightness(20,10), variable_brightness(60,40))

                    r,g,b = convert_color(hue, sat, val)
                    picounicorn.set_pixel(dots_coordinates[dots_increment][0], dots_coordinates[dots_increment][1], r, g, b)
                    sleep(0.03)

                sleep(randint(1,3)/12)

            if vis_delta != current_visual:
                clear_display()
                dots_increment = -1
                vis_delta = current_visual
    
    clear_display()

    # Options (Mode 1)
    while current_mode == 1:
        draw_character(symbol_list[6], 12, local_hue=140, local_sat=0.9, local_val=200)
        draw_character(symbol_list[5], 12, local_hue=330, local_sat=1, local_val=150)
        draw_string(option_list[current_option], colored=False)
        sleep(0.7)

    clear_display()

    # Configuration (Mode 100)
    while current_mode == 100:
        global configuration_step
        global configuration_value

        blink_string("RSET")
        clear_display()
        draw_carats()
        clear_display(width=14)
        configuration_step = 0
        configuration_value = 99

        letter_list[5] = [
        [0,0],[1,0],
        [0,1],      
        [0,2],      
        [0,3],[1,3],
        [0,4],      
        [0,5],      
        [0,6],[1,6],
        ]

        # Step 0 - DATE
        while configuration_step == 0:
            draw_string("DATE", colored=False)
            sleep(0.1)

        clear_display()

        # Step 1 (set year)
        while configuration_step == 1:
            draw_carats()

            draw_string("YR", offset=3, colored=False)
            sleep(0.1)

        reset_year = configuration_value
        configuration_value = 12
        clear_display()

        letter_list[5] = [
        [0,0],[1,0],[2,0],
        [0,1],      
        [0,2],      
        [0,3],[1,3],[2,3],
        [0,4],      
        [0,5],      
        [0,6],[1,6],[2,6]
        ]

        # Step 2 (set month)
        while configuration_step == 2:
            draw_carats()

            draw_string("M", offset=3, colored=False)
            draw_string("O", offset=9, colored=False)
            sleep(0.1)

        reset_month = configuration_value
        configuration_value = 31
        clear_display()

        # Step 3 (set day)
        while configuration_step == 3:
            draw_carats()

            draw_string("DAY", offset=3, colored=False)
            sleep(0.1)

        reset_day = configuration_value
        configuration_value = 23
        clear_display()
        draw_carats()
        clear_display(width=14)

        # Step 4 - TIME
        while configuration_step == 4:
            draw_string("TM", colored=False)
            draw_string("E", offset=10, colored=False)
            sleep(0.1)

        clear_display()

        # Step 5 (set hour)
        while configuration_step == 5:
            draw_carats()
            
            draw_string("HUR", offset=3, colored=False)
            sleep(0.1)

        reset_hour = configuration_value
        configuration_value = 59
        clear_display()

        # Step 6 (set min)
        while configuration_step == 6:
            draw_carats()

            draw_string("M", offset=3, colored=False)
            draw_string("I", offset=9, colored=False)
            draw_string("N", offset=11, colored=False)
            sleep(0.1)

        reset_minute = configuration_value
        reset_second = 0
        configuration_value = 0
        clear_display()
        draw_carats()
        clear_display(width=14)

        # Step 7 (confirm)
        while configuration_step == 7:
            draw_string("OK", colored=False)
            draw_character(symbol_list[4], 8, local_hue=0, local_sat=0, local_val=255)
            draw_character(symbol_list[2], 13, local_hue=140, local_sat=0.9, local_val=200)
            draw_character(symbol_list[3], 13, local_hue=10, local_sat=1, local_val=150)
            sleep(0.1)
        
        # Write new date/time
        if configuration_step == 8:
            date_time = (2000+reset_year, reset_month, reset_day, reset_hour, reset_minute, reset_second)
            rtc.set_rtc_date_time(date_time)
            print(date_time)
            blink_string("SET")

            set_current_mode(0)
