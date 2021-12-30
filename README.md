# Quarter-Clock 

This project uses an adapted library for the RV3028 RTC, found at this https://github.com/x10dit/rv3028_rtc GitHub repo.

Full description coming soon.


## A -- Mode

Press this to change the mode.

1 Quarter-Clock!

2 Options

3 Visuals

## B -- Select

In Quarter-Clock mode, [does nothing].

In Options mode, changes the option's current setting.

In Visuals mode, cycles through different visuals.

## X -- Brightness/Cycle Up

In Quarter-Clock mode, changes brightness level.

In Options mode, cycles *up* through options.

In Visuals mode, changes brightness level.

## Y -- Color/Cycle Down

In Quarter-Clock mode, changes the color theme.

In Options mode, cycles *down* through the options.

In Visuals mode, changes the color theme.


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


## TODO:

- Create and test a HOUR RESET function
- Make UP into Brightness and DOWN into Color for modes 0 and 2