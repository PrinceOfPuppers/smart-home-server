#include <Arduino.h>
#include <stdlib.h>
#include <limits.h>

#include "uart-buff.h"
#include "rf-wrappers.h"
#include "const.h"


// parse inboundBuffer and transmit rf signal
void transmittInboundBuffer(){
    char *token;
    char *endptr;
    // First part is `T,` (for future packet switching), discard it
    next_token(token, endptr);

    next_token(token, endptr);
    unsigned long protocol = strtoul(token, &endptr, 10);
    strtoul_err_check(token, endptr);

    next_token(token, endptr);
    unsigned long code = strtoul(token, &endptr, 10);
    strtoul_err_check(token, endptr);

    next_token(token, endptr);
    unsigned long bit_length = strtoul(token, &endptr, 10);
    strtoul_err_check(token, endptr);

    next_token(token, endptr);
    unsigned long pulse_length = strtoul(token, &endptr, 10);
    strtoul_err_check(token, endptr);

    next_token(token, endptr);
    unsigned long num_repeats = strtoul(token, &endptr, 10);
    strtoul_err_check(token, endptr);

    buff_reset();
    // basic sanity checks
    if (protocol > 12 || bit_length > INT_MAX || pulse_length > 1000 || num_repeats > 64){
        return;
    }
    txTransmit(protocol, code, bit_length, pulse_length, num_repeats);
}

void handleUart(){
    if(!Serial.available()){
        return;
    }
    char c = Serial.read();
#ifdef DEBUG_SERIAL_ENABLED
    Serial.print(c);
#endif
    if (c != '\n' && c !='\r'){
        buff_push_char(c);
        return;
    }

    transmittInboundBuffer();
}

void setup(){
    Serial.begin(115200);
    buff_reset();
    setupRf();
}

void loop(){
    handleRx();
    handleUart();
}
