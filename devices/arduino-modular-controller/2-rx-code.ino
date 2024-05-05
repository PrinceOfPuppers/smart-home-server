#if RX_ENABLED
#include <RCSwitch.h>

static RCSwitch rx = RCSwitch();

#define PRESS_DEBOUNCE_MS 700

// pins
#define RX_PIN 2 // int pins are 2 and 3

// rx defines
#define PROTOCOL 1
#define ON_VALUE 9872892
#define OFF_VALUE 9872884
// #define ON_VALUE 9872889
// #define OFF_VALUE 9872881
#define BIT_LENGTH 24
#define NUM_REPEATS 3

void testRx(){
    while(1){
#if DEBUG_SERIAL_ENABLED
        if(rx.available()){
            Serial.print( rx.getReceivedValue() );
            Serial.print(" / ");
            Serial.print( rx.getReceivedBitlength() );
            Serial.print(" bit ");
            Serial.print(" Protocol: ");
            Serial.println( rx.getReceivedProtocol() );
            rx.resetAvailable();
        }
#endif
    delay(10);
    }
}

// helper macro
#define returnReset(x) rx.resetAvailable(); return x

// 0 for no match, ON_VALUE/OFF_VALUE for respective value
unsigned long codeMatches(){
    while(1){
        if(rx.available()){
            if(rx.getReceivedBitlength()!=BIT_LENGTH){
                returnReset(0);
            }

            if(rx.getReceivedProtocol()!=PROTOCOL){
                returnReset(0);
            }

            unsigned long value = rx.getReceivedValue();
            if(value != ON_VALUE && value != OFF_VALUE){
                returnReset(0);
            }
            returnReset(value);
        }
    }
}

void setupRx(){
    rx.enableReceive(digitalPinToInterrupt(RX_PIN));
#if DEBUG_SERIAL_ENABLED
    Serial.println("RX Setup");
#endif
}


void runOnCodeMatch(void (* on_off_cb)(bool)){
    int count = 0;
    unsigned long val = 0;
    unsigned long prevVal = 0;

    while(1){
        val = codeMatches();

        if(val == 0){
            // code is irrelevant
            prevVal = 0;
            count = 0;
            continue;
        }

        if (val != prevVal){
            // code is first on/off in a chain
            prevVal = val;
            count = 1;
            continue;
        }

        // code is [count]'th in chain
        count += 1;
        if (count < NUM_REPEATS){
            // match chain not long enough
            continue;
        }

        // we've heard the code enough times
#if DEBUG_LED_ENABLED
    digitalWrite(LED_BUILTIN, val == ON_VALUE ? HIGH : LOW);
#endif

#if DEBUG_SERIAL_ENABLED
    Serial.print("Matched Code: ");
    Serial.println(val == ON_VALUE ? "ON" : "OFF");
#endif
        count = 0;
        prevVal = 0;
        on_off_cb(val == ON_VALUE);

        // debounce
        delay(PRESS_DEBOUNCE_MS);
        rx.resetAvailable();
    }
}

#endif
