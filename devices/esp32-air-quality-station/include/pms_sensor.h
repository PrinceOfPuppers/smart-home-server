#ifndef PMS_SENSOR_H_
#define PMS_SENSOR_H_
#include "PMS.h"

void wakeup_pms();

void setup_pms();

void _awaitWakeup();

int update_pms(PMS::DATA *data);

#endif
