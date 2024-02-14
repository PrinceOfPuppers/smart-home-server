#include "PMS.h"
#include "bme680_type.h"
#include "bsec.h"
#include "WiFi.h"



#define SERIAL_BAUD 115200

// #define DEBUG_ENABLED

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
    debug("Hardfault: ");
    debugln(numFlashes);
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


/////////////////////////////
// s8 calibration callback //
/////////////////////////////

#define S8_INTERRUPT_PIN 12

static bool s8_calibrate_flag = false;
void calibrate_s8_cb(){
    s8_calibrate_flag = true;

}


// number of read errors until hardfault (error on startup hardfaults immediately)
#define MAX_READ_ERR 5

#define MinsMs 60*1000

static BMEData bmeData;
static uint16_t bmeErrCounter = 0;
#define BME_UPDATE_PERIOD_Mins 1

static PMS::DATA pmsData;
static uint16_t pmsErrCounter = 0;
#define PMS_UPDATE_PERIOD_Mins 5

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
    delay(2000);
    debugln("========== Startup ==========");
#endif
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    // wait for devices to power up
    delay(2000);

    // begin pms setup
    setup_pms();
    delay(1000);
    wakeup_pms();
    debugln("");
    delay(1000);

    // wifi setup
    setup_udp();
    debugln("");
    delay(1000);

    // bme setup
    int status = setup_bme680();
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_BME);}
    delay(1000);
    status = update_bme(&bmeData);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_BME);}
    debugln("");
    delay(2000);

    // s8 setup
    status = setup_s8();
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_S8);}
    delay(1000);
    status = update_s8(&s8Data);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_S8);}
    debugln("");
    delay(1000);

    // end pms setup
    status = update_pms(&pmsData);
    if(status != AQS_STATUS_OK){hardfault(LED_ERR_PMS);}
    debugln("");
    delay(1000);

    // attach S8 calibration interrupt
    pinMode(S8_INTERRUPT_PIN, INPUT_PULLUP);
    attachInterrupt(S8_INTERRUPT_PIN, calibrate_s8_cb, FALLING);

    digitalWrite(LED_PIN, LOW);

    debugln("======== Startup End ========");
    debugln("");


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
    // wakeup 1 minute before call
    if((counterMins + 1) % PMS_UPDATE_PERIOD_Mins == 0){
        wakeup_pms();
    }
    // actual call
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

// called whenever loop delays
void busy_delay(uint32_t delayMs){
    if(s8_calibrate_flag){
        digitalWrite(LED_PIN, HIGH);
        int status = calibrate_s8();
        if (status != AQS_STATUS_OK){
            hardfault(LED_ERR_S8);
        }
        s8_calibrate_flag = false;
        digitalWrite(LED_PIN, LOW);
        delay(200);
        digitalWrite(LED_PIN, HIGH);
        delay(200);
        digitalWrite(LED_PIN, LOW);
    }
    delay(delayMs);
}

void loop(){
    uint32_t counterMins = 0;

    uint32_t startMs = 0;
    uint32_t durationMs = 0;

    // each loop takes 1 minute
    while(1){
        counterMins+=1;
        startMs = millis();
        debugln("=========== Loop ============");
        debug("Minute: ");
        debugln(counterMins);
        debugln("");

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

        // transmit with remining time
        debugln("");
        await_udp_transmitt(busy_delay,MinsMs - durationMs, &bmeData, &pmsData, &s8Data);
        debugln("");
    }
}
