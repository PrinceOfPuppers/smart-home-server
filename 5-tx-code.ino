#if TX_ENABLED
#include <RCSwitch.h>

static RCSwitch tx = RCSwitch();

#define TX_PIN 8

// tx defines
#define PROTOCOL 1
#define ON_VALUE 8638538
#define OFF_VALUE 8638530
//#define ON_VALUE 9872890
//#define OFF_VALUE 9872882
#define PULSE_LENGTH 195
#define BIT_LENGTH 24
#define NUM_REPEATS 10


void setupTx(){
    tx.enableTransmit(TX_PIN);
    tx.setProtocol(PROTOCOL, PULSE_LENGTH);
    tx.setRepeatTransmit(NUM_REPEATS);

#if DEBUG_SERIAL_ENABLED
    Serial.println("Tx Setup");
#endif
}

void txTransmit(bool on){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Tranmitting: ");
    Serial.println(on ? "ON" : "OFF");
#endif
    if(on){
        tx.send(ON_VALUE, BIT_LENGTH);
        return;
    }
    tx.send(OFF_VALUE, BIT_LENGTH);
}

#endif
