#ifndef GENERAL_H_
#define GENERAL_H_

#include <Arduino.h>

// #define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print(msg)
#define debugln(msg) Serial.println(msg)
#else
#define debug(msg) 
#define debugln(msg) 
#endif

#endif
