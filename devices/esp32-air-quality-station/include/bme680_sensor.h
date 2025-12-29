#ifndef BME680_SENSOR_H_
#define BME680_SENSOR_H_
#include "bme680_type.h"

int checkIaqSensorStatus(void);

// Entry point for the example
int setup_bme680(void);

int update_bme(BMEData *out);

#endif
