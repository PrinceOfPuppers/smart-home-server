#include <BME280I2C.h>
#include <Wire.h>

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "network-info.h"

#define SERIAL_BAUD 115200

//#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print(msg)
#define debugln(msg) Serial.println(msg)
#else
#define debug(msg) 
#define debugln(msg) 
#endif

#define STATUS_OK 0
#defien STATUS_NO_UPDATE 1
#defien STATUS_WARN 2
#defien STATUS_ERR 3
