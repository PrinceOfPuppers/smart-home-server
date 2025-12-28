#ifndef UDP_H_
#define UDP_H_
#include <Arduino.h>

// just for type
#include "PMS.h"
#include "bme680_type.h"


void setup_udp();
void await_udp_transmitt(void (* delay_func)(uint32_t), uint32_t duration, BMEData *bmeData, PMS::DATA *pmsData, uint16_t *s8Data);

#endif
