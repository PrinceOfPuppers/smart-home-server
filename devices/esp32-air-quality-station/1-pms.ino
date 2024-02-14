#include "PMS.h"

#define PMS_RX1 5
#define PMS_TX1 18
#define PMS_SET 14
#define PMS_SLEEP_MS 30*1000

PMS pms(Serial1);

static uint32_t lastWakeMs = 0;
static bool sleeping = false;

void wakeup_pms(){
    debugln("Waking up PMS");
    digitalWrite(PMS_SET, HIGH);
    delay(5);
    pms.wakeUp();
    lastWakeMs = millis();
    sleeping = false;
}

void _sleep_pms(){
    debugln("Sleeping PMS");
    pms.sleep();
    delay(5);
    digitalWrite(PMS_SET, LOW);
    sleeping = true;
}

void setup_pms()
{
    debugln(">>> Setting Up PMS5003 <<<");
    pinMode(PMS_SET, OUTPUT);
    digitalWrite(PMS_SET, HIGH);

    Serial1.begin(9600, SERIAL_8N1, PMS_RX1, PMS_TX1);
    pms.passiveMode();    // Switch to passive mode
    debugln("Setup PMS Complete!");
    //_sleep_pms();
}

void _awaitWakeup(){
    if(sleeping){
        debugln("PMS Rude Wakeup");
        wakeup_pms();
    }

    uint32_t msSinceWake = millis() - lastWakeMs;
    if (msSinceWake < PMS_SLEEP_MS){
        debugln("Waiting for PMS to Wakeup...");
        delay(PMS_SLEEP_MS - msSinceWake);
    }
}

int update_pms(PMS::DATA *data){
    _awaitWakeup();

    pms.requestRead();

    if(pms.readUntil(*data)){
        debugln("PMS Data:");
        // memebers are of type uint16_t
        debugln("  PM1.0: " + String(data->PM_AE_UG_1_0) + "(ug/m3)");
        debugln("  PM2.5: " + String(data->PM_AE_UG_2_5) + "(ug/m3)");
        debugln("  PM10 : " + String(data->PM_AE_UG_10_0) + "(ug/m3)");
        _sleep_pms();
        return AQS_STATUS_OK;
    }
    _sleep_pms();

    debugln("PMS no Update");
    return AQS_STATUS_NO_UPDATE;
}

