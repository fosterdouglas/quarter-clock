# Quarter-Clock!

![Prototype Image](/media/prototype.jpg "Prototype Image")

![Prototype Image](/media/beta.jpeg "Beta Image")

(prototype and alpha build images above)

This project is put together with this hardware:

- [Raspberry Pi Pico](https://shop.pimoroni.com/products/raspberry-pi-pico?variant=32402092294227)
- [Pico Unicorn Pack](https://shop.pimoroni.com/products/pico-unicorn-pack)
- [RV3028 Real-Time Clock (RTC)](https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout)
- [TEMT6000 Light Sensor](https://www.amazon.com/HiLetgo-TEMT6000-Sensor-Professional-Arduino/dp/B07WDW9BHD/ref=sr_1_3?crid=UP8D28EVTBIA&keywords=temt6000&qid=1641287814&sprefix=temt600%2Caps%2C323&sr=8-3)

And this software:

- [Pimoroni's](https://shop.pimoroni.com) custom [Pico firmware](https://github.com/pimoroni/pimoroni-pico) v0.X.X, which uses MicroPython v1.16
- An adapted RV3028 library for MicroPython found at this [GitHub repo](https://github.com/x10dit/rv3028_rtc)

To control the Quarter-Clock:

## A -- Visualizations

In Quarter-Clock mode, changes to different visualizations.

## B -- Options

In Quarter-Clock mode, changes in and out of the options mode.

(If a visualization is displaying, this will instead interact with it)

## X -- Brightness / Switch Option

In Quarter-Clock mode, changes brightness level.

In Options mode, cycles to the next option.

## Y -- Color Theme / Edit Option

In Quarter-Clock mode, changes the color theme.

In Options mode, changes the option's current setting.

## Options

- HOR (Hour Adjustment):
  - Changes the displaying hour
- DST (Automatic Daylight Savings Time):
  - When **Auto**, Quarter-Clock will **automatically** adjust its time forward 1 hour between Mar 13 and Nov 6
  - Default: **Auto**
- BRT (Automatic Brightness):
  - When **Auto**, Quarter-Clock will automatically adjust its display brightness to the ambient light
  - Adjusting the brightness manually at any time will set this to **Off**
  - Default: **Auto**
- COL (Color Theme):
  - Changes the current color theme (Rainbow / Ocean / Fire+Ice)
  - Quarter-Clock will quickly cycle throguh 24 hours to demonstate the selected color theme
  - Default: **Rainbow**
- 24H (12/24 Display Style):
  - Changes the 24-hour time display style
  - Default: **On**

## Resetting the date/time of Quarter-Clock:

The Quarter-Clock will need its date/time set once when first plugging it in, and it may need it reset if the battery dies. To enter the configuration mode:

- Plug in the Quarter-Clock
- From any screen or mode, **press and hold** the _X_ button for 10 seconds
- The display will flash the words 'RSET'
- On each of the following screens, use the _A_ and _B_ buttons to increase/decrease the current value, and press the _Y_ button to proceed

Note: the following values are not actually set until the end of the process when given to option to confirm or restart the process. Keep this in mind when setting the _minute_ value specifically, if the goal is to set it precisely.

To start, set the date (these values are important for the Quarter-Clock to keep track of leap years and month/days, which is used for Automatic DST):

- YR - the **current year** in a two-digit format of 20XX, from 00 - 99
- MO - the **current month** from 01 - 12 (January - December)
- DAY - the **current day** from 01 - 31

Next, set the time:

- HOR - the **current hour** which should be set to the local time zone hour, from 00 - 23 (Midnight - 11PM)
- MIN - the **current minute** which should be set to the local time zone minute, from 00 - 59

On the final step, use the _Y_ button to confirm, or the _X_ button to restart the reset process.

## The RTC battery

If the small battery inside of the RTC chip dies (and it someday will), the Quarter-Clock will continue to function normally although it will _not retain its set date/time if it's unplugged_. In this case, use the instructions above to reset the date/time each time its unplugged.

Alternatively, to change the battery:

- Get a new [337 battery](https://www.amazon.com/Energizer-337-Button-Cell-Battery/dp/B001C1FZ6K)
- Open the Quarter-Clock case
- Remove the battery from the external chip labelled "RV3028" (a tweezers works well, pushing it out from the back)
- Replace the new battery, ensuring the proper polarity is facing downward
- Close the Quarter-Clock case
- Plug in the Quarter-Clock, and use the steps above to reset the date and time, which will now be properly stored in memory if there's power missing

## Development notes:

- This project was developed as the maker's first use of Python (and MicroPython)
- Most of the code is not remotely optimized, although it is performant running on a Raspberry Pi Pico
- Some aspects of the software will still be iterated on, in particular the design of the "Quaters" display, and the visualizations
