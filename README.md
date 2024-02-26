# Smart Home Server
> A Full Smart Home System and Associeated IOT Devices

- [DEVICES](#devices)
  * [ESP32 AIR QUALITY STATION](#esp32-air-quality-station)
  * [ESP DASHBOARD](#esp-dashboard)
  * [ESP WEATHER STATION](#esp-weather-station)
  * [ARDUINO LIGHT SWITCHER](#arduino-light-switcher)
- [ABOUT](#about)
  * [JOBS AND MACROS](#jobs-and-macros)
  * [DATASOURCES](#datasources)
- [PAGES](#pages)

# DEVICES

<img align="left" width="500" src="devices/main-case/images/full-front.jpg">
<br clear="left"/>
<br clear="left"/>


## ESP32 AIR QUALITY STATION
[README Link](devices/esp32-air-quality-station/README.md)

<img align="left" width="500" src="devices/esp32-air-quality-station/images/full-right.jpg">
<br clear="left"/>
<br clear="left"/>

## ESP DASHBOARD
[README Link](devices/esp-dashboard/README.md)

<img align="left" width="500" src="devices/esp-dashboard/images/full-right.jpg">
<br clear="left"/>
<br clear="left"/>

## ESP WEATHER STATION
[README Link](devices/esp-weather-station/README.md)

<img align="left" width="500" src="devices/esp-weather-station/images/full.jpg">
<br clear="left"/>
<br clear="left"/>

## ARDUINO LIGHT SWITCHER
[README Link](devices/arduino-light-switcher/README.md)

<img align="left" width="500" src="devices/arduino-light-switcher/images/motion_dev_pic.jpg">
<br clear="left"/>
<br clear="left"/>

# ABOUT
The smart-home-server (hereto called "the server") is a device for collecting data and controlling IOT devices (hereto called "devices"). The server runs a full web interface for easy control on mobile or desktop

The servers functionality is best understood through the following catigories

## Jobs and Macros
Jobs are things the server can do, they include:
- Transmitting RF signals (for controlling RF outlets and relays)
- Sending HTTP requests
- Updating remote LCD Dashboard formats (see lcds page)
- Running Job Macros
- Updating the server
- And more

Jobs can be organized into macros and setup to trigger in on RF signals, button presses on the servers case, or manually throught the webpage.
Jobs and macros can also be run using a scheduler (ie turn off the lights at 11pm) or can be triggered on conditions (ie turn on the humidifer whenever reletive humidity is below 35%). See the [Schedule](#schedule) and [Trigger](#trigger) pages for more details

Macros can also include delays and other macros, 

### Example 
Here is an example of a simple nightime macro:

<img align="left" width="500" src="images/macro-example.png">
<br clear="left"/>
<br clear="left"/>

This macro turns off all the lights, turns off a loud air filter in the bedroom, waits for 8h30min, prevents you from oversleeping by turning on the bedroom light, and then turns everyting in the bedroom off after 30 more minutes. 

This macro could be hooked up to an rf button outside the bedroom to be run without having to open the web app (how I do it).

The macros like bedroom on/off would be replaced with single rf switching jobs, ie) `press bedroom ch: 1 on`, for the example macros where used so they could be labeled.

## Datasources
The server collects data from `datasources` with a set polling period. The data can then be used to:
- [Trigger](#trigger) [Jobs](#jobs)and-macros] on conditions
- Displayed on the [dashboard](#dashboard)
- [Graphed](#graph)
- Displayed on local and remote [LCDs](#lcd)

<img align="left" width="300" src="images/dashboard-example.png">
<img align="left" width="300" src="images/graph-example.png">
<br clear="left"/>
<br clear="left"/>

<img align="left" width="300" src="images/trigger-example.png">
<img align="left" width="300" src="devices/esp-dashboard/images/full-front.jpg">
<br clear="left"/>
<br clear="left"/>

# PAGES
