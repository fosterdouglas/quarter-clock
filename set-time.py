from utime import localtime
import rv3028_rtc

#initalize the RV3028 RTC unit
sda=machine.Pin(26)
scl=machine.Pin(27)
i2c=machine.I2C(1,sda=sda, scl=scl, freq=100000)
rtc=rv3028_rtc.RV3028(0x52, i2c, "LSM")

hours = localtime()[3]-1

if hours == -1:
    hours = 23

print(localtime())

#one-time setup to give RV3028 the correct time
#date_time = (localtime()[0],localtime()[1],localtime()[2],hours,localtime()[4],localtime()[5],"mon")
date_time = (localtime()[0],10,4,3,18,0,"mon")

while True:
    if date_time[5] != rtc.get_rtc_date_time()[6]:
        rtc.set_rtc_date_time(date_time)
        print("time calibrated?")
        print(date_time)
        break
    else:
        print('waiting')
        pass

