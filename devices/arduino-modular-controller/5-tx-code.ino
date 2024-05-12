#if TX_ENABLED
#include <RCSwitch.h>

static RCSwitch tx = RCSwitch();

#define TX_PIN 8

// tx defines
#define TX_PROTOCOL 1
#define TX_ON_VALUE 5264835
#define TX_OFF_VALUE 5264844
//#define TX_ON_VALUE 9872890
//#define TX_OFF_VALUE 9872882
#define TX_PULSE_LENGTH 195
#define TX_BIT_LENGTH 24
#define TX_NUM_REPEATS 10


void setupTx(){
    tx.enableTransmit(TX_PIN);
    tx.setProtocol(TX_PROTOCOL, TX_PULSE_LENGTH);
    tx.setRepeatTransmit(TX_NUM_REPEATS);

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
        tx.send(TX_ON_VALUE, TX_BIT_LENGTH);
        return;
    }
    tx.send(TX_OFF_VALUE, TX_BIT_LENGTH);
}

#endif
