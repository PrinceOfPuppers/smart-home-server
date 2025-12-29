#include "watchdog.h"
#include <Arduino.h>
#include "general.h"
#include "ESP8266TimerInterrupt.h"

// Select a Timer Clock
#define USING_TIM_DIV1                false           // for shortest and most accurate timer
#define USING_TIM_DIV16               false           // for medium time and medium accurate timer
#define USING_TIM_DIV256              true            // for longest timer but least accurate. Default

ESP8266Timer ITimer;

static bool _reset = true;
void IRAM_ATTR TimerHandler()
{
  if(!_reset){
      ESP.restart();
  }
  _reset = false;
}
void feed_watchdog(){
    _reset=true;
}

bool setup_watchdog(long wdt_interval)
{
    feed_watchdog();
    // Interval in microsecs
    if (ITimer.attachInterruptInterval(wdt_interval * 1000, TimerHandler)) {
        debugln("Watchdog Setup");
        return true;
    }
    else{
        debugln("Watchdog Setup Failed!");
    }
    return false;
}


