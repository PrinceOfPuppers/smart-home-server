#if SERVO_ENABLED
#include <Servo.h>

//////////////////////////////
// SERVO TRIM POTENTIOMETER //
//////////////////////////////

#define SERVO_POT_READ_PIN A6
#define SERVO_POT_ENABLE_PIN 5

// neutral position of servo will be 90 plus/minus SERVO_TRIM_RANGE/2
#define SERVO_TRIM_RANGE 60

float getPotValue(){
    digitalWrite(SERVO_POT_ENABLE_PIN, 1);
    delay(10);
    int a = analogRead(SERVO_POT_READ_PIN);
    digitalWrite(SERVO_POT_ENABLE_PIN, 0);

    // value between 0 and 1 corrisponding to pot rotation
    return a/1023.;
}
#define potToPos(pot) (90 + round( SERVO_TRIM_RANGE * (pot - 0.5) ) )

// returns angle between 90-SERVO_TRIM_RANGE/2 and 90+SERVO_TRIM_RANGE/2
int getServoNeutral(){
    return potToPos(getPotValue());
}

//////////////////
// SERVO INVERT //
//////////////////

#define SERVO_INVERT_PIN A0

int getServoInvert(){
    pinMode(SERVO_INVERT_PIN, INPUT_PULLUP);
    int x = !digitalRead(SERVO_INVERT_PIN);
    // turn off pullup
    pinMode(SERVO_INVERT_PIN, INPUT);
    return x;
}


/////////////////////
// MAIN SERVO CODE //
/////////////////////

#define SERVO_MOVE_DELAY 150

#define SERVO_PIN 7
#define SERVO_PRESS_ANGLE_UP 18
#define SERVO_PRESS_ANGLE_DOWN 18
// swaps up and down angles (if presser is on left side, invert)
// pull pin low to invert (only measured at startup)
static int servo_invert = 0;

static int servoNeutralPos = 90;
static Servo serv;
static int servPos = 0;


void setServ(int pos){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Setting Servo Angle: ");
    Serial.println(pos);
#endif
    servPos = pos;
    serv.write(servPos);
    delay( SERVO_MOVE_DELAY );
}


void setupServo(){
    pinMode(SERVO_POT_ENABLE_PIN, OUTPUT);
    pinMode(SERVO_POT_READ_PIN, INPUT);

    servo_invert = getServoInvert();
    servoNeutralPos = getServoNeutral();

    serv.attach(SERVO_PIN);
    setServ(servoNeutralPos);
    serv.detach();

#if DEBUG_SERIAL_ENABLED
    Serial.println("Servo Setup");
#endif
}


void servoPress(bool up){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Servo Press: ");
    Serial.print(up ? "UP" : "DOWN");
    Serial.println(servo_invert ? " (Inverted)" : "");
#endif

    int angle;
    if (servo_invert){
        angle = up ?
             servoNeutralPos - SERVO_PRESS_ANGLE_UP :
             servoNeutralPos + SERVO_PRESS_ANGLE_DOWN;
    } else {
        angle = up ?
            servoNeutralPos + SERVO_PRESS_ANGLE_UP :
            servoNeutralPos - SERVO_PRESS_ANGLE_DOWN;
    }

    serv.attach(SERVO_PIN);
    setServ(angle);
    setServ( servoNeutralPos );
    serv.detach();
}

void servoReset(){
#if DEBUG_SERIAL_ENABLED
    Serial.println("Servo Reset");
#endif

    serv.attach(SERVO_PIN);
    setServ( servoNeutralPos );
    servPos = servoNeutralPos;
    serv.detach();
}

void testServo(){
    while(1){
        servoPress(1);
        delay(1000);
        servoPress(0);
        delay(1000);
        servoNeutralPos = getServoNeutral();
        servo_invert = getServoInvert();
    }
}

void testServoPot(){
    float prevVal = -1;
    while(1){
        float val = getPotValue();
        if(abs(prevVal - val) > 0.001){
            servoNeutralPos = potToPos(val);
            servo_invert = getServoInvert();

#if DEBUG_SERIAL_ENABLED
            Serial.print("Pot Value: ");
            Serial.println(val);

            Serial.print("Neutral Pos: ");
            Serial.println(servoNeutralPos);
#endif
            servoReset();

            prevVal = val;
        }

        delay(100);
    }
}

void testServoRange(){

    serv.attach(SERVO_PIN);
    while(1){
        for(int i = 0; i < 180; i++){
            setServ(i);
        }
    }
    serv.detach();

}

#else
// stubs
void servoPress(bool up){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Servo Press: ");
    Serial.println(up ? "UP" : "DOWN");
#endif
}
void servoReset(){
#if DEBUG_SERIAL_ENABLED
    Serial.println("Servo Resetting");
#endif

}

#endif
