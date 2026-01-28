#include "rf-wrappers.h"
#include <Arduino.h>
#include <RCSwitch.h>
#include "const.h"

static RCSwitch rf = RCSwitch();

////////
// RX //
////////
struct RxData {
    unsigned int protocol;
    unsigned long code;
    unsigned int bit_length;
    unsigned long pulse_length_sum; // should be averaged over num_repeats to get average pulse length
    int num_repeats;
    unsigned long time_ms;
};


static RxData last_rx;
static RxData last_sent_rx;

// this is the last time we sent an rx_code over uart, used for deboucning

void wipeRxData(struct RxData *data){
    data->protocol = 0;
    data->code = 0;
    data->bit_length = 0;
    data->pulse_length_sum = 0;
    data->num_repeats = 0;
    data->time_ms = 0;
}
bool rxDataEquals(struct RxData *d1, struct RxData *d2){
    return \
        d1->protocol == d2->protocol &&
        d1->code == d2->code &&
        d1->bit_length == d2->bit_length;
}

// 0/false for no code, 1/true 
bool getCode(struct RxData *rx_out){
    if(!rf.available()){
        return false;
    }

    unsigned long t = millis();
    if(rx_out->code != rf.getReceivedValue() ||
       rx_out->protocol != rf.getReceivedProtocol() ||
       rx_out->bit_length != rf.getReceivedBitlength() ||
       t - rx_out->time_ms > RX_REPEATS_MAX_MS
       ){
        rx_out->num_repeats = 0;
        rx_out->pulse_length_sum = 0;
    }
    rx_out->code = rf.getReceivedValue();
    rx_out->protocol = rf.getReceivedProtocol();
    rx_out->bit_length = rf.getReceivedBitlength();
    rx_out->num_repeats++;
    rx_out->pulse_length_sum += rf.getReceivedDelay();
    rx_out->time_ms = t;

    rf.resetAvailable();
    return true;
}

void handleRx(){
    if(!getCode(&last_rx)){
        return;
    }

    if(last_rx.num_repeats < RX_NUM_REPEATS){
        return;
    }

    unsigned long t = millis();
    if(rxDataEquals(&last_rx, &last_sent_rx) && (t - last_sent_rx.time_ms <= RX_UART_DEBOUNCE_MS)){
#ifdef DEBUG_SERIAL_ENABLED
        Serial.println("Debounce");
#endif
        wipeRxData(&last_rx);
        return;
    }

    // non-debounced code recieved with sufficent repeats, transmit over UART
    unsigned int pulse_length = round((float)last_rx.pulse_length_sum / last_rx.num_repeats);

    Serial.print("R,");
    Serial.print(last_rx.protocol);
    Serial.print(",");
    Serial.print(last_rx.code);
    Serial.print(",");
    Serial.print(last_rx.bit_length);
    Serial.print(",");
    Serial.println(pulse_length);
    last_sent_rx = last_rx;

    wipeRxData(&last_rx);
}


////////
// TX //
////////
void txTransmit(int protocol, unsigned long code, unsigned int bit_length, int pulse_length, int num_repeats){
#ifdef DEBUG_SERIAL_ENABLED
    Serial.print("T ");
    Serial.print(protocol);
    Serial.print(",");
    Serial.print(code);
    Serial.print(",");
    Serial.print(bit_length);
    Serial.print(",");
    Serial.print(pulse_length);
    Serial.print(",");
    Serial.println(num_repeats);
#endif
    rf.setProtocol(protocol, pulse_length);
    rf.setRepeatTransmit(num_repeats);
    rf.send(code, bit_length);
}

/////////////
// GENERAL //
/////////////

void setupRf(){
    wipeRxData(&last_rx);
    wipeRxData(&last_sent_rx);
    rf.enableTransmit(TX_PIN);
    rf.enableReceive(digitalPinToInterrupt(RX_PIN));
#ifdef DEBUG_SERIAL_ENABLED
    Serial.println("Rf Setup");
#endif
}
