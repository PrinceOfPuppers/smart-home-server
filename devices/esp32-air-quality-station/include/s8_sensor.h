#ifndef S8_SENSOR_H_
#define S8_SENSOR_H_
#include <Arduino.h>

int diagnose_s8();

int setup_s8();

int calibrate_s8();

int update_s8(uint16_t *co2_out);

#endif
