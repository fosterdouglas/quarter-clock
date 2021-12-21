# Quarter Clock

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

In Visuals mode, interacts with the visual.

## X -- Cycle Up

In Quarter Clock mode, cycles up through brightness levels.

In Options mode, cycles through options:

- HRD (Hour Delta):
    - Changes the hour
    - Default: GMT-0
- DST (Daylight Savings Time): 
    - When enabled, clock will automatically adjusts its time during DST
    - Default: On
- BRT (Auto-Brightness):
    - When enabled, clock will automatically adjust its display brightness to the ambient light
    - Adjusting the brightness manually will also set this to OFF
    - Default: On 
- COL (Color Theme):
    - Changes the current color theme (Rainbow / Ocean / Fire+Ice)
    - When changed, clock will quickly cycle throguh 24 hours to demonstate color theme
    - Default: Rainbow
- 24H (12/24 Display Style):
    - Enables or disables the 24H time display style
    - DEfault: On


In Visuals mode, cycles through different visuals.


## Y -- Cycle Down

Cycles opposite direction.