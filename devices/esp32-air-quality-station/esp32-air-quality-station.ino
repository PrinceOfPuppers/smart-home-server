#include "PMS.h"
#include "bme680_type.h"
#include "bsec.h"
#include "WiFi.h"



#define SERIAL_BAUD 115200

#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print((msg))
#define debugln(msg) Serial.println((msg))
#else
#define debug(msg) 
#define debugln(msg) 
#endif

#define AQS_STATUS_OK 0
#define AQS_STATUS_NO_UPDATE 1
#define AQS_STATUS_WARN 2
#define AQS_STATUS_ERR 3


///////////////
// LED COMMS //
///////////////

#define LED_PIN 2

// number of flashes of led
#define LED_ERR_BME 2
#define LED_ERR_PMS 3
#define LED_ERR_S8  4
#define LED_ERR_OTHER 5

#define LED_ERR_PAUSE 1000
#define LED_ERR_PULSE 200

void setLed(bool on){
    digitalWrite(LED_PIN, on ? HIGH : LOW);
}

void hardfault(int numFlashes){
    while(1){
        for(int i = 0; i < numFlashes; i++){
            digitalWrite(LED_PIN, HIGH);
            delay(LED_ERR_PULSE);
            digitalWrite(LED_PIN, LOW);
            delay(LED_ERR_PULSE);
        }
        delay(LED_ERR_PAUSE);
    }
}


// number of read errors until hardfault (error on startup hardfaults immediately)
#define MAX_READ_ERR 5

#define MinsMs 60*1000

static BMEData bmeData;
static uint16_t bmeErrCounter = 0;
#define BME_UPDATE_PERIOD_Mins 1

static PMS::DATA pmsData;
static uint16_t pmsErrCounter = 0;
#define PMS_UPDATE_PERIOD_Mins 3

static uint16_t s8Data;
static uint16_t s8ErrCounter = 0;
#define S8_UPDATE_PERIOD_Mins 1

static uint16_t timingErrorCounter = 0;

////////////////
// setup/loop //
////////////////
void setup(){
#ifdef DEBUG_ENABLED
    Serial.begin(SERIAL_BAUD);
    while(!Serial) {}
#endif
    // begin pms setup
    setup_pms();
    wakeup_pms();

    // bme setup
    int status = setup_bme680();
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_BME);}
    status = update_bme(&bmeData);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_BME);}

    // s8 setup
    status = setup_s8();
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_S8);}
    status = update_s8(&s8Data);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_S8);}

    // end pms setup
    status = update_pms(&pmsData);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_PMS);}

    setup_udp();
}

void updateAll(uint32_t counterMins){
    int status;
    // BME
    if((counterMins % BME_UPDATE_PERIOD_Mins) == 0){
        status = update_bme(&bmeData);
        if(status != AQS_STATUS_OK){
            if ((++bmeErrCounter) > MAX_READ_ERR){
                hardfault(LED_ERR_BME);
            }
        }
        else {
            bmeErrCounter = 0;
        }
    }

    // s8
    if((counterMins % S8_UPDATE_PERIOD_Mins) == 0){
        status = update_s8(&s8Data);
        if(status != AQS_STATUS_OK){
            if ((++s8ErrCounter) > MAX_READ_ERR){
                hardfault(LED_ERR_S8);
            }
        }
        else {
            s8ErrCounter = 0;
        }
    }

    // PMS
    if((counterMins % PMS_UPDATE_PERIOD_Mins) == 0){
        status = update_pms(&pmsData);
        if(status != AQS_STATUS_OK){
            if ((++pmsErrCounter) > MAX_READ_ERR){
                hardfault(LED_ERR_PMS);
            }
        }
        else {
            pmsErrCounter = 0;
        }
    }
}

void loop(){
    uint32_t counterMins = 0;

    uint32_t startMs = 0;
    uint32_t durationMs = 0;

    // each loop takes 1 minute
    while(1){
        counterMins+=1;
        startMs = millis();

        updateAll(counterMins);

        durationMs = millis() - startMs;

        // handle error for long reads
        if(durationMs > MinsMs){
            debugln("Err: read took longer than a minute");
            timingErrorCounter += 1;
            if(timingErrorCounter > MAX_READ_ERR){

                hardfault(LED_ERR_OTHER);
            }
            continue;
        }
        timingErrorCounter = 0;

        // transmitt with remining time
        await_udp_transmitt(MinsMs - durationMs, &bmeData, &pmsData, &s8Data);
    }
}
