#include "PMS.h"

#define RX1 5
#define TX1 18
#define PMS_SLEEP_MS 30*1000

PMS pms(Serial1);

static uint32_t lastWakeMs = 0;
static bool sleeping = false;

void wakeup_pms(){
    pms.wakeUp();
    lastWakeMs = millis();
}

void _sleep_pms(){
    pms.sleep();
    sleeping = true;
}

void setup_pms()
{
    Serial1.begin(9600, SERIAL_8N1, RX1, TX1);
    pms.passiveMode();    // Switch to passive mode
    debugln("Setup PMS Complete!");
    _sleep_pms();
}

void _awaitWakeup(){
    if(sleeping){
        debugln("PMS Rude Wakeup");
        wakeup_pms();
    }

    uint32_t msSinceWake = millis() - lastWakeMs;
    if (msSinceWake < PMS_SLEEP_MS){
        delay(PMS_SLEEP_MS - msSinceWake);
    }
}

int update_pms(PMS::DATA *data){
    _awaitWakeup();

    pms.requestRead();

    if(pms.readUntil(*data)){
        debugln("PMS Data:");
        // memebers are of type uint16_t
        debugln("PM1.0: " + String(data->PM_AE_UG_1_0) + "(ug/m3)");
        debugln("PM2.5: " + String(data->PM_AE_UG_2_5) + "(ug/m3)");
        debugln("PM10 : " + String(data->PM_AE_UG_10_0) + "(ug/m3)");
        return AQS_STATUS_OK;
    }
    _sleep_pms();

    debugln("PMS no Update");
    return AQS_STATUS_NO_UPDATE;
}

