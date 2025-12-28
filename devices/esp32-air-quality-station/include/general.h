#ifndef GENERAL_H_
#define GENERAL_H_

#include <Arduino.h>

#define AQS_STATUS_OK 0
#define AQS_STATUS_NO_UPDATE 1
#define AQS_STATUS_WARN 2
#define AQS_STATUS_ERR 3


// #define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print((msg))
#define debugln(msg) Serial.println((msg))
#else
#define debug(msg)
#define debugln(msg)
#endif

#endif
