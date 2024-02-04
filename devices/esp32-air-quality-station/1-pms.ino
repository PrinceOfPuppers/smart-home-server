#include "PMS.h"

#define RX1 5
#define TX1 18

PMS pms(Serial1);
PMS::DATA data;

void setup_pms()
{
  Serial1.begin(9600, SERIAL_8N1, RX1, TX1);
  debugln("Setup PMS Complete!");
}

int update_pms(PMS::DATA *data){
    if(pms.read(*data)){
        debugln("PMS Data:")
        debugln("PM1.0: " + String(data.PM_AE_UG_1_0) + "(ug/m3)");
        debugln("PM2.5: " + String(data.PM_AE_UG_2_5) + "(ug/m3)");
        debugln("PM10 : " + String(data.PM_AE_UG_10_0) + "(ug/m3)");
        return STATUS_OK;
    }

    debugln("PMS no Update");
    return STATUS_NO_UPDATE;
}

