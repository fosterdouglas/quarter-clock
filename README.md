# Quarter-Clock 

This project uses an adapted library for the RV3028 RTC, found at this https://github.com/x10dit/rv3028_rtc GitHub repo.

It also uses Pimoroni's custom Pico firmware v0.X.X, which uses MicroPython v1.16, found here: https://github.com/pimoroni/pimoroni-pico.

## A -- Select

In Quarter-Clock mode, cycles through different visualizations.

## B -- Options

In Quarter-Clock mode, toggles in and out of the options mode.

(If a visualization is displaying, this will instead interact with or modify it)

## X -- Brightness/Cycle Option

In Quarter-Clock mode, changes brightness level.

In Options mode, cycles to the next option.

## Y -- Color/Change Option

In Quarter-Clock mode, changes the color theme.

In Options mode, changes the option's current setting.

## Options

- HOR (Hour Adjustment):
    - Changes the hour
    - Default: GMT-0
- DST (Daylight Savings Time): 
    - When enabled, Quarter-Clock will **automatically** adjust its time forward 1 hour between Mar 13 and Nov 6
    - Default: Auto
- BRT (Auto-Brightness):
    - When enabled, Quarter-Clock will automatically adjust its display brightness to the ambient light
    - Adjusting the brightness manually will also set this to OFF
    - Default: On 
- COL (Color Theme):
    - Changes the current color theme (Rainbow / Ocean / Fire+Ice)
    - When selected, Quarter-Clock will quickly cycle throguh 24 hours to demonstate the selected color theme
    - Default: Rainbow
- 24H (12/24 Display Style):
    - Enables or disables the 24H time display style
    - DEfault: On

## Resetting the Quarter-Clock:
[ soon ]

## Notes:
[ soon ]

## TODO:

- Figure out error handling for battery dying? like, if rtc HAS no value when it starts up, it needs the run the one time setting up
- Write README description  
- Add interaction to visuals 