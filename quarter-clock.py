import picounicorn
from utime import sleep
import math
import random
import gc
import rv3028_rtc
from machine import Pin
from machine import ADC

picounicorn.init()

display_width = picounicorn.get_width()
display_height = picounicorn.get_height()

# initalize the RV3028 RTC unit
i2c=machine.I2C(1,sda=Pin(26), scl=Pin(27), freq=100000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

gmt_sec = rtc.get_seconds()
gmt_min = rtc.get_minutes()
gmt_hr = rtc.get_hours()
gmt_date = rtc.get_date()
gmt_month = rtc.get_month()

light_sensor = machine.ADC(28)

global current_quarter
global global_brt #brightness
global hr12_mode #24 or 12h clock
global dst_mode #DST enabled or disabled
global hr_delta #difference in hours from system clock
global theme_hue
global theme_sat
global palette_list
global current_palette
global dst #value to 

current_quarter = 0
global_brt = 0.8 #brightness from 0.0 to 1.0
hr12_mode = False
hr_delta = 0
dst = 0
dst_mode = True
brightness_override = False
pulse = True
quarter_positions = [0, 8, 10, 12, 14]

# using these instead of picounicorn's built in functions to be able to access IRQs
button_a = Pin(12, Pin.IN, Pin.PULL_UP)
button_b = Pin(13, Pin.IN, Pin.PULL_UP)
button_x = Pin(14, Pin.IN, Pin.PULL_UP)
button_y = Pin(15, Pin.IN, Pin.PULL_UP)

# set up palettes
#TODO: do we actually need both of these?
palette_list = ['rainbow', 'chill', 'fire_ice']
current_palette = 0

rainbow_palette_hue = [323, 330, 340, 350, 0, 10, 15, 26, 38, 60, 98, 150, 170, 180, 190, 198, 225, 215, 242, 242, 270, 290, 305, 312]
rainbow_palette_sat = [0.81, 0.84, 0.85, 0.9, 0.83, 0.89 , 0.68, 0.9, 0.65, 0.55, 0.85, 0.93, 0.95, 0.40, 0.71, 0.65, 0.40, 0.71, 0.53, 0.89, 0.73, 0.89, 0.89, 0.89]

chill_palette_hue = []
chill_palette_sat = [1 for k in range(24)]
#TODO: make the chill palette's colors more dilberately?
for i in range(240, 256, 4): #first 17 colors
    chill_palette_hue += [i]
for i in range(256, 184, -12): #last 6 colors, loop back through same values to return to same starting point
    chill_palette_hue += [i]
for i in range(184, 240, 4): #first 17 colors
    chill_palette_hue += [i]

    
fire_ice_palette_hue = [359, 353, 347, 341, 335, 323, 317, 300, 287, 281, 275, 269, 263, 239, 233, 227, 239, 269, 281, 305, 320, 330, 340, 350]
fire_ice_palette_sat = [1 for k in range(24)]
        
theme_hue = rainbow_palette_hue
theme_sat = rainbow_palette_sat

# position coordinates from top left of the number
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

digit_list[10] = [
[0,0],
[0,1],
[0,2],
[0,3],[1,3],[2,3],
[0,4],      [2,4],
[0,5],      [2,5],
[0,6],      [2,6]
]

def ambient_light_check():
    global global_brt
    
    ambient_light = light_sensor.read_u16()
    # print(ambient_light)
    
    if not brightness_override:
        if ambient_light > 30000 and global_brt != 1.0:
            global_brt = 1.0
            soft_reset()
        elif ambient_light >= 1500 and ambient_light <= 30000 and global_brt != 0.8:
            global_brt = 0.8
            soft_reset()
        elif ambient_light < 1500 and global_brt != 0.4:
            global_brt = 0.4
            soft_reset()

def get_palette_pos(val):
    if val > 23:
        val = val%24
        return val
    else:
        return val
    
def set_palette(name):
    global theme_hue
    global theme_sat
    
    if name == 'rainbow':
        theme_hue = rainbow_palette_hue
        theme_sat = rainbow_palette_sat
    elif name == 'chill':
        theme_hue = chill_palette_hue
        theme_sat = chill_palette_sat
    elif name == 'fire_ice':
        theme_hue = fire_ice_palette_hue
        theme_sat = fire_ice_palette_sat
    
    print('Change palette to: ' + str(name))
    
def set_current_quarter(val):
    global current_quarter
    current_quarter = val
    
def format_hour(hour):
    # function to adjust global time to local time, considering user adjusted hours
    formatted_hour = hour + hr_delta
    
    # apply DST adjustment if enabled
    if dst_mode:
        formatted_hour = formatted_hour + dst
        
    # resets the hour if it goes above 23 during user time setting
    if formatted_hour > 23:
        formatted_hour = formatted_hour%24
    
    # split the hour into two spearate digits
    first_digit, second_digit = split_digit(formatted_hour)
    
    #format properly if 12h clock being used
    if hr12_mode == True:
        local_hour = formatted_hour%12
        if local_hour == 0:
            local_hour = 12
        first_digit, second_digit = split_digit(local_hour)
       
    return [first_digit, second_digit, formatted_hour]

def split_digit(digit):
    if digit < 10:
        first_digit = 0
        second_digit = digit
    else:        
        first_digit = math.floor(digit / 10)
        second_digit = math.floor(digit % 10)
    return first_digit, second_digit

        
def draw_digit(num, offset, local_hue=theme_hue[get_palette_pos(format_hour(gmt_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(gmt_hr)[2])]):
    for i in range(len(num)):
        x = num[i][0]        
        y = num[i][1]
        
        local_val = variable_brightness(255, 50)
        r, g, b = convert_color(local_hue, local_sat, local_val)        
        picounicorn.set_pixel(x + offset, y, r, g, b)
            
def clear_display():
    for x in range(display_width):
        for y in range(display_height):
            #draws "black" pixels
            picounicorn.set_pixel(x, y, 0, 0, 0)
            
def draw_display_pillar(width, offset, local_val, height=display_height, local_hue=theme_hue[get_palette_pos(format_hour(gmt_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(gmt_hr)[2])]):
    r, g, b = convert_color(local_hue, local_sat, local_val)
    for x in range(width):
        for y in range(height):
            picounicorn.set_pixel(x + offset, y, r, g, b)

def convert_color(hue, sat, val):
    # incoming values: hue is 0-360, sat is 0.0-1.0 and val is 0-255
    hue = (hue)%359
    hue = (hue)/360
    sat = sat
    
    #TODO: change all value and VB calls to be 0.0-1.0 range instead of 0-255, then remove this division
    val = val/255
    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, sat, val)]
    return (r, g, b)

def set_brightness(default=False):
    # function for changing the brightness by 1 level
    global global_brt
    
    if default == True or global_brt < 0.4:
        global_brt = 1.0
    else:
        global_brt = global_brt - 0.2
        
    print('Change brightness to : ' + str(global_brt))    

    soft_reset()
    sleep(0.1)

def variable_brightness(value, minimum=0):
    # function to handle variable brightness across anything drawn
    value = value * global_brt

    if value < minimum:
        value = minimum
        
    return int(value)

def seconds_pulse():
    forward_hue = theme_hue[get_palette_pos(format_hour(gmt_hr)[2]+1)]
    forward_sat = theme_sat[get_palette_pos(format_hour(gmt_hr)[2]+1)]
    
    if current_quarter == 1:
        localOffset = (gmt_sec%6)+quarter_positions[2]
    elif current_quarter == 2:
        temp = (gmt_sec%6)
        if temp == 0 or temp == 1:
            localOffset = (gmt_sec%6)+quarter_positions[1]
        else:
            localOffset = (gmt_sec%6)+quarter_positions[2]
    elif current_quarter == 3:
        temp = (gmt_sec%6)
        if temp == 4 or temp == 5:
            localOffset = (gmt_sec%6)-4+quarter_positions[4]
        else:
            localOffset = (gmt_sec%6)+quarter_positions[1]
    elif current_quarter == 4:
        localOffset = (gmt_sec%6)+quarter_positions[1]
        
    for i in range(variable_brightness(50,25), variable_brightness(210, 120), 25):
        draw_display_pillar(1, localOffset, i, local_hue=forward_hue, local_sat=forward_sat)
        sleep(0.05)
    for i in reversed(range(variable_brightness(50,25), variable_brightness(210, 120), 25)):
        draw_display_pillar(1, localOffset, i, local_hue=forward_hue, local_sat=forward_sat)
        sleep(0.05)

def display_quarters():
    in_flux = False
    
    # set the quarters hue to the upcoming hour's hue, for some visual contrast
    forward_hue = theme_hue[get_palette_pos(format_hour(gmt_hr)[2]+1)]
    forward_sat = theme_sat[get_palette_pos(format_hour(gmt_hr)[2]+1)]
    
    # check which quarter we are in
    if gmt_min <= 13 or gmt_min == 59:
        set_current_quarter(1)
    elif gmt_min >= 14 and gmt_min <= 28:
        set_current_quarter(2)
    elif gmt_min >= 29 and gmt_min <= 43:
        set_current_quarter(3)
    elif gmt_min >= 44 and gmt_min <= 58:
        set_current_quarter(4)
        
    if gmt_min == 14 or gmt_min == 29 or gmt_min == 44 or gmt_min == 59:
        in_flux = True
    
    # draw each of the 4 quarters
    for i in range(1,5):
        
        # for the current quarter
        if i == current_quarter:
            
            if in_flux == False:
                # animation for blink/fade each minute
                print('minute blink')
                for desc in reversed(range(variable_brightness(34,0), variable_brightness(204, 100), 17)):  
                    draw_display_pillar(2, quarter_positions[i], desc, local_hue=forward_hue, local_sat=forward_sat)
                    sleep(0.02)
                for asc in range(variable_brightness(34,0), variable_brightness(204, 100), 17):  
                    draw_display_pillar(2, quarter_positions[i], asc, local_hue=forward_hue, local_sat=forward_sat)
                    sleep(0.02)
                    
                draw_display_pillar(2, quarter_positions[i], variable_brightness(240, 80), local_hue=forward_hue, local_sat=forward_sat)
                
            # animate for each quarter change
            if in_flux == True:
                
                if i > 0:
                    draw_display_pillar(2, quarter_positions[i - 1], variable_brightness(240, 80), local_hue=forward_hue, local_sat=forward_sat)
                    
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(display_height):
                        draw_display_pillar(2, quarter_positions[i - 1], 0, off + 1, local_hue=forward_hue, local_sat=forward_sat)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    draw_display_pillar(2, quarter_positions[i - 1], variable_brightness(50, 25), local_hue=forward_hue, local_sat=forward_sat,)
                    
                     #animate next quarter over
                    print('next quarter on')
                    for on in range(display_height):
                        draw_display_pillar(2, quarter_positions[i], variable_brightness(240, 80), on + 1, local_hue=forward_hue, local_sat=forward_sat,)
                        sleep(0.03)
                    draw_display_pillar(2, quarter_positions[i], variable_brightness(240, 80), local_hue=forward_hue, local_sat=forward_sat)
                else:
                    # animate off previous quarter
                    print('previous quarter off')
                    for off in range(display_height):
                        draw_display_pillar(2, quarter_positions[3], 0, off + 1, local_hue=forward_hue, local_sat=forward_sat)
                        sleep(0.03)
                    # replace the emptiness with faded quarter
                    draw_display_pillar(2, quarter_positions[3], variable_brightness(50, 25), local_hue=forward_hue, local_sat=forward_sat)
                    
                    # otherwise, animate the first quarter   
                    print('next quarter on')
                    for on in range(display_height):
                        draw_display_pillar(2, quarter_positions[0], variable_brightness(240, 80), on + 1, local_hue=forward_hue, local_sat=forward_sat)
                        sleep(0.03)
                    draw_display_pillar(2, quarter_positions[0], variable_brightness(240, 80), local_hue=forward_hue, local_sat=forward_sat)
        
        # for the other 3 faded quarters
        else:
            draw_display_pillar(2, quarter_positions[i], variable_brightness(50, 25), local_hue=forward_hue, local_sat=forward_sat)
        
def display_hours():
    # function to display the main digits
    draw_digit(digit_list[format_hour(gmt_hr)[0]], 0, local_hue=theme_hue[get_palette_pos(format_hour(gmt_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(gmt_hr)[2])])
    draw_digit(digit_list[format_hour(gmt_hr)[1]], 4, local_hue=theme_hue[get_palette_pos(format_hour(gmt_hr)[2])], local_sat=theme_sat[get_palette_pos(format_hour(gmt_hr)[2])])
    
def incr_hour_delta(delta=1):
    # function for changing the hour by a set amount, measured by the change from the global time
    global hr_delta
    hr_delta = hr_delta + delta
    if hr_delta > 23:
        hr_delta = 0
        
def toggle_hr12_mode():
    # function for toggling 12-hour clock on or off
    global hr12_mode
    hr12_mode = not hr12_mode
    print('Toggle 12/24h mode')
    
def toggle_dst_mode():
    global dst_mode
    dst_mode = not dst_mode

def check_dst():
    # function to determine if it's the date and time to change the clock automatically
    
    global dst
    
    #TODO: test this properly
    if gmt_month >= 11 or gmt_month <= 3:
        if gmt_month == 11 and gmt_date >= 7:
            dst = 0
        elif gmt_month == 3 and gmt_date <= 14:
            dst = 0      
        else:
            dst = 1
    else:
        dst = 1
                            
def hour_transition():
    # animation when changing hours
    for i in range(display_width/2):
        fade = variable_brightness(30, 0) + (i*variable_brightness(20, 10))
        draw_display_pillar(1, (math.ceil(display_width/2)) + i, fade)
        draw_display_pillar(1, (math.floor(display_width/2)-1) - i, fade)
        sleep(1/display_width)
    for i in range(display_width/2):
        fade = max(0, (variable_brightness(255, 100) - (i*variable_brightness(40, 20))))
        draw_display_pillar(1, (math.ceil(display_width/2)) + i, fade)
        draw_display_pillar(1, (math.floor(display_width/2)-1) - i, fade)
        sleep(1/display_width)
    for i in range(display_width/2):
        fade = max(0, (variable_brightness(255, 100) - (i*variable_brightness(40, 20))))
        draw_display_pillar(1, (math.ceil(display_width/2)) + i, fade)
        draw_display_pillar(1, (math.floor(display_width/2)-1) - i, fade)
        draw_display_pillar(1, (math.ceil(display_width/2)+1) + (i-1), 0)
        draw_display_pillar(1, (math.floor(display_width/2)-1) - (i), 0)
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
    
def callback_button_a(pin):
    print('button A')
    d = check_debounce(pin)

    if d == None:
        return
    elif not d:
        exit_loop = False
        you_win = False
        sleep(0.5)
        while not exit_loop:
            print('Toggle disco mode')
            for i in range(32):
                if i < 16:
                    pos = i
                    hue = theme_hue[i]
                else:
                    pos = 31 - i
                    hue = theme_hue[i - 16]
 
                r, g, b = convert_color(hue, 1.0, 220)
                
                for x in range(display_width):
                    for y in range(display_height):
                        picounicorn.set_pixel(pos, y, r, g, b)
                sleep(0.01)
                
                if picounicorn.is_pressed(picounicorn.BUTTON_A):
                    # if you stop the bar in the very center you win
                    if i == 8:
                        you_win = True           
                    exit_loop = True
                    break
                sleep(1/1028)
            sleep(0.5)
                
        if you_win == True:

            # celebrate, you win! ... an animation
            for i in range(24): 
                for pos in range(16):

                    hue = random.randint(0,360)
                    sat = random.randint(70,100)/100
                    val = random.randint(50,255)
                    r, g, b = convert_color(hue, sat, val)
                    for x in range(display_width):
                        for y in range(display_height):
                            picounicorn.set_pixel(pos, random.randint(0,6), r, g, b)
                sleep(0.05)
        soft_reset()

def callback_button_b(pin):
    print('Button B')
    d = check_debounce(pin)

    if d == None:
        return
    elif not d:
        # check if button held
        for t in range (31):
            if picounicorn.is_pressed(picounicorn.BUTTON_B):
               sleep(0.1)
               
               # if held for 3 sec, toggle time between 12/24h
               if t == 30:
                toggle_hr12_mode()
                
                clear_display()
                
                # animation to show new hour format 
                if hr12_mode:
                    for f in range (6):
                        # draw blank first
                        draw_display_pillar(12, 0, 0)
                        sleep(0.1)
                        draw_digit(digit_list[1], 0)
                        draw_digit(digit_list[2], 4)
                        draw_digit(digit_list[10], 8)
                        sleep(0.2)
                        
                else:
                    for f in range (6):
                        # draw blank first
                        draw_display_pillar(12, 0, 0)
                        sleep(0.1)
                        draw_digit(digit_list[2], 0)
                        draw_digit(digit_list[4], 4)
                        draw_digit(digit_list[10], 8)
                        sleep(0.2)
                        
                soft_reset()
            
            # if button is not held, changes brightness down by 0.2, then loops around to 1.0 brightness
            else:
                # set override to true, so display no longer automatically changes brightness
                global brightness_override
                
                brightness_override = True
                set_brightness()
                
                if global_brt == 1.0:
                    brightness_override = False
                break
            
        
def callback_button_x(pin):
    print('Button X')
    d = check_debounce(pin)

    if d == None:
        return
    elif not d:
        global current_palette
        current_palette = (current_palette + 1) % len(palette_list)
        set_palette(palette_list[current_palette])
        
        for z in range(2):
        # change to new palette, then display palette color range
            for i in range(len(theme_hue)):
                
                clear_display()
                if hr12_mode:
                    first_digit, second_digit = split_digit((i%12)+1)
                else:
                    first_digit, second_digit = split_digit(i)

                draw_digit(digit_list[first_digit], 0, local_hue=theme_hue[i], local_sat=theme_sat[i])
                draw_digit(digit_list[second_digit], 4, local_hue=theme_hue[i], local_sat=theme_sat[i])
                
                for x in range(8, display_width):
                    for y in range(display_height):
                        picounicorn.set_pixel(x, y, *convert_color(theme_hue[get_palette_pos(i+1)], theme_sat[get_palette_pos(i+1)], global_brt*255))
                sleep(0.4)
        
        soft_reset()
        soft_reset()
        #TODO: something here to stop the nexttick Pulse from being the wrong color

def callback_button_y(pin):
    print('Button Y')
    d = check_debounce(pin)

    if d == None:
        return
    elif not d:
        # check if button held
        for t in range (31):
            if picounicorn.is_pressed(picounicorn.BUTTON_Y):
               sleep(0.1)
               
               # if held for 3 sec, toggle time between 12/24h
               if t == 30:
                toggle_dst_mode()
                
                clear_display()
                
                # animation to show new hour format 
                if dst_mode:
                    for f in range (6):
                        sleep(0.1)
                        draw_display_pillar(4, 0, 0)
                        #TODO: make this say "DST ON" ?
                        draw_digit(digit_list[1], 0)
                        sleep(0.2)
                else:
                    for f in range (6):
                        sleep(0.1)
                        draw_display_pillar(4, 0, 0)
                        #TODO: make this say "DST OFF" ?
                        draw_digit(digit_list[0], 0)
                        sleep(0.2)
                    
        sleep(0.5)
        
        #otherwise, change hour by 1
        incr_hour_delta()
        soft_reset()
    
def check_debounce(pin):
    # function to help prevent button presses from debouncing
    prev = None
    for _ in range(32):
        current_value = pin.value()
        if prev != None and prev != current_value:
            return None
        prev = current_value
    return prev

def soft_reset():
    # function to do a soft reset
    clear_display()
    display_hours()
    display_quarters()

# interrupt requests
button_a.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_a)
button_b.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_b)
button_x.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_x)
button_y.irq(trigger=Pin.IRQ_FALLING, handler=callback_button_y)

# one-time setup
set_brightness(True)
check_dst()
hour_transition()
soft_reset()

while True:
    gc.collect()
    #print('Mem free: {} --- Mem allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))

    # runs once per second
    if gmt_sec != rtc.get_seconds():
        print(format_hour(gmt_hr)[2], gmt_min, gmt_sec)
        
        seconds_pulse()
        ambient_light_check()
        gmt_sec = rtc.get_seconds()
                
        # check minute        
        if rtc.get_minutes() != gmt_min:
            display_quarters()
            
            gmt_min = rtc.get_minutes()
        
        # check hour  
        if rtc.get_hours() != gmt_hr:
            gmt_hr = rtc.get_hours()
            
            check_dst()
            incr_hour_delta()
            
            hour_transition()
            display_quarters()
        
        display_hours()

        gc.collect()
    else:
        pass

#cool color fading chill animation to use for later
# for r in range(2): #do it twice
#     for f in range(10): #flashing
#         
#         #clear_display()
#         for a in range(16): #color changes
#             #TODO: use convert_color() here?
#             hue = (hours[f] + (a*2))/360
#             r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, a/15, 0.8)]
#             for x in range(display_width):
#                 for y in range(display_height):
#                     picounicorn.set_pixel(a, y, r, g, b)
#             sleep(0.1)
        sleep(0.2)