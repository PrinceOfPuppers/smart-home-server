#if RX_ENABLED
#include <RCSwitch.h>

static RCSwitch rx = RCSwitch();

#define RX_PRESS_DEBOUNCE_MS 700

// pins
#define RX_PIN 2 // int pins are 2 and 3

// rx defines
#define RX_PROTOCOL 1
#define RX_ON_VALUE 5264835
#define RX_OFF_VALUE 5264844
// #define RX_ON_VALUE 9872889
// #define RX_OFF_VALUE 9872881
#define RX_BIT_LENGTH 24
#define RX_NUM_REPEATS 3

void testRx(){
#if DEBUG_SERIAL_ENABLED
    Serial.println("Testing RX");
#endif

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

// 0 for no match, RX_ON_VALUE/RX_OFF_VALUE for respective value
unsigned long codeMatches(){
    while(1){
        if(rx.available()){
            if(rx.getReceivedBitlength()!=RX_BIT_LENGTH){
                returnReset(0);
            }

            if(rx.getReceivedProtocol()!=RX_PROTOCOL){
                returnReset(0);
            }

            unsigned long value = rx.getReceivedValue();
            if(value != RX_ON_VALUE && value != RX_OFF_VALUE){
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
        if (count < RX_NUM_REPEATS){
            // match chain not long enough
            continue;
        }

        // we've heard the code enough times
#if DEBUG_LED_ENABLED
    digitalWrite(LED_BUILTIN, val == RX_ON_VALUE ? HIGH : LOW);
#endif

#if DEBUG_SERIAL_ENABLED
    Serial.print("Matched Code: ");
    Serial.println(val == RX_ON_VALUE ? "ON" : "OFF");
#endif
        count = 0;
        prevVal = 0;
        on_off_cb(val == RX_ON_VALUE);

        // debounce
        delay(RX_PRESS_DEBOUNCE_MS);
        rx.resetAvailable();
    }
}

#endif
