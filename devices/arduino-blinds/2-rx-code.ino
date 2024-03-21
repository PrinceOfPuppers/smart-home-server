#include <RCSwitch.h>

static RCSwitch rx = RCSwitch();

#define HEARD_DEBOUNCE_MS 700

// pins
#define RX_PIN 2 // int pins are 2 and 3

// rx defines
#define PROTOCOL 1
#define ON_VALUE 5272835
#define OFF_VALUE 5272844
#define BIT_LENGTH 24
#define NUM_REPEATS 3

// helper macro
#define returnReset(x) rx.resetAvailable(); return x

// -1 for not avalible, 0 for no match, ON_VALUE/OFF_VALUE for respective value
long code_matches(){
    if(rx.available()){
        if(rx.getReceivedBitlength()!=BIT_LENGTH){
            returnReset(0);
        }

        if(rx.getReceivedProtocol()!=PROTOCOL){
            returnReset(0);
        }

        long value = (long)rx.getReceivedValue();
        if(value != ON_VALUE && value != OFF_VALUE){
            returnReset(0);
        }
        returnReset(value);
    }
    return -1;
}

void setup_rx(){
    rx.enableReceive(digitalPinToInterrupt(RX_PIN));
}

static int _heard = RX_NONE;
static unsigned long _prev_heard_time = 0;

static int count = 0;
static long val = 0;
static long prevVal = 0;
void update_rx(){
        unsigned long now = millis();
        if (now - _prev_heard_time < HEARD_DEBOUNCE_MS){
            rx.resetAvailable();
            return;
        }

        val = code_matches();

        if(val == -1){
            // no value
            return;
        }

        if(val == 0){
            // code is irrelevant
            prevVal = 0;
            count = 0;
            return;
        }

        if (val != prevVal){
            // code is first on/off in a chain
            prevVal = val;
            count = 1;
            return;
        }

        // code is [count]'th in chain
        count += 1;
        if (count < NUM_REPEATS){
            // match chain not long enough
            return;
        }

        count = 0;
        prevVal = 0;

        _heard = val == ON_VALUE ? RX_UP : RX_DOWN;
        _prev_heard_time = now;
}

int get_rx_heard(){
    int x = _heard;
    _heard = RX_NONE;
    if(x!=RX_NONE){
    }

    return x;
}

