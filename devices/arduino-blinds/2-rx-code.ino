#include <RCSwitch.h>
#include <EEPROM.h>

static RCSwitch rx = RCSwitch();

#define HEARD_DEBOUNCE_MS 700

// pins
#define RX_PIN 2 // int pins are 2 and 3

#define NUM_REPEATS 3

struct Rx_Values{
    unsigned int bit_length;
    unsigned int protocol;
    unsigned long on_value;
    unsigned long off_value;
};

Rx_Values rx_values;

// helper macros
#define returnReset(x) rx.resetAvailable(); return x

// -1 for not avalible, 0 for no match, ON_VALUE/OFF_VALUE for respective value
long code_matches(){
    if(rx.available()){
        if(rx.getReceivedBitlength()!=rx_values.bit_length){
            returnReset(0);
        }

        if(rx.getReceivedProtocol()!=rx_values.protocol){
            returnReset(0);
        }

        long value = (long)rx.getReceivedValue();
        if(value != rx_values.on_value && value != rx_values.off_value){
            returnReset(0);
        }
        returnReset(value);
    }
    return -1;
}
void program_rx(){
    unsigned int bit_length=9999;
    unsigned int protocol=9999;
    unsigned long value=9999;

    unsigned int new_bit_length=1010;
    unsigned int new_protocol=1010;
    unsigned long new_value=1010;

    uint8_t matches = 0;
    // first program value for on, then for off
    bool programming_off_value = false;

    uint16_t counter = 0;
    while(1){
        // blink led
        if(counter == 0)    {digitalWrite(LED_BUILTIN, HIGH);}
        if(counter == 65535/2){digitalWrite(LED_BUILTIN, LOW);}
        delayMicroseconds(20);
        counter++;

        if(rx.available()){
            new_bit_length = rx.getReceivedBitlength();
            new_protocol = rx.getReceivedProtocol();
            new_value = rx.getReceivedValue();
            rx.resetAvailable();
            // on and off cannot be the same value
            if (programming_off_value == true && new_value == rx_values.on_value){
                continue;
            }

            if(
                (new_bit_length == bit_length) &&
                (new_protocol == protocol)     &&
                (new_value == value)
            ){
                matches++;
            }

            // enough iterations have been reached, save value
            if(matches >= NUM_REPEATS){
                // blink led to indicate value recieved
                for(int _ = 0; _ < 3; _++){
                    digitalWrite(LED_BUILTIN, HIGH);
                    delay(100);
                    digitalWrite(LED_BUILTIN, LOW);
                    delay(100);
                }

                rx_values.bit_length = new_bit_length;
                rx_values.protocol = new_protocol;

                if(programming_off_value){
                    rx_values.off_value = new_value;
                    // both values have been programmed, leave
                    return;
                }
                // first value programmed
                rx_values.on_value = new_value;
                programming_off_value = true;
                // reset values
                matches = 0;
                bit_length=9999;
                protocol=9999;
                value=9999;
                continue;
            }

            bit_length = new_bit_length;
            protocol = new_protocol;
            value = new_value;
        }
    }
}

void setup_rx(bool program){
    rx.enableReceive(digitalPinToInterrupt(RX_PIN));
    if(program){
        program_rx();
        EEPROM.put(0, rx_values);
    }
    else{
        EEPROM.get(0, rx_values);
    }
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

        _heard = val == rx_values.on_value ? RX_UP : RX_DOWN;
        _prev_heard_time = now;
}

int get_rx_heard(){
    int x = _heard;
    _heard = RX_NONE;
    if(x!=RX_NONE){
    }

    return x;
}

