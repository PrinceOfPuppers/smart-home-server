#include <RCSwitch.h>
#include <Servo.h>

RCSwitch rx = RCSwitch();
Servo serv;

// pins
#define SERVO_PIN 7
#define RX_INT_PIN 0 // 0 = pin2, 1 = pin3

#define INITAL_SERVO_POS 90
#define SERVO_PRESS_ANGLE_UP 16
#define SERVO_PRESS_ANGLE_DOWN 16

// rx defines
#define PROTOCOL 1
#define ON_VALUE 9872892
#define OFF_VALUE 9872884
#define BIT_LENGTH 24
#define NUM_REPEATS 3

/*
void rxTest(){
    if(rx.available()){
        Serial.print( rx.getReceivedValue() );      
        Serial.print(" / ");     
        Serial.print( rx.getReceivedBitlength() );      
        Serial.print(" bit ");      
        Serial.print(" Protocol: ");     
        Serial.println( rx.getReceivedProtocol() );
        rx.resetAvailable();
    }
}
*/

int servPos = 0;
void setServ(int pos){
    servPos = pos;
    serv.write(servPos);
    delay(100);
}

void press(bool on){
    int angle = on ? INITAL_SERVO_POS + SERVO_PRESS_ANGLE_UP : 
                     INITAL_SERVO_POS - SERVO_PRESS_ANGLE_DOWN;
    setServ(angle);
    setServ( INITAL_SERVO_POS );
}

void setup() {
    // Serial.begin(9600);

    serv.attach(SERVO_PIN);
    setServ(INITAL_SERVO_POS);

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    rx.enableReceive(RX_INT_PIN);
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


static int count = 0;
static unsigned long val = 0;
static unsigned long prevVal = 0;

void loop() {
    val = codeMatches();

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

    // we've heard the code enough times
    count = 0;
    prevVal = 0;
    press(val == ON_VALUE);

    // debounce
    delay(1000);
}

