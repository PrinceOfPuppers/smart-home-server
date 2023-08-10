#if SERVO_ENABLED
#include <Servo.h>

#define SERVO_MOVE_DELAY 150

#define SERVO_PIN 7
#define INITAL_SERVO_POS 90
#define SERVO_PRESS_ANGLE_UP 18
#define SERVO_PRESS_ANGLE_DOWN 18
// swaps up and down angles
#define SERVO_INVERT 0

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
    serv.attach(SERVO_PIN);
    setServ(INITAL_SERVO_POS);
    serv.detach();

#if DEBUG_SERIAL_ENABLED
    Serial.println("Servo Setup");
#endif
}

#endif

// Behaves like stub if servo is disabled
void servoPress(bool up){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Servo Press: ");
    Serial.print(up ? "UP" : "DOWN");
    Serial.println(SERVO_INVERT ? " (Inverted)" : "");
#endif


#if SERVO_ENABLED

#if SERVO_INVERT
    int angle = up ?
            INITAL_SERVO_POS - SERVO_PRESS_ANGLE_UP :
            INITAL_SERVO_POS + SERVO_PRESS_ANGLE_DOWN;
#else
    int angle = up ?
            INITAL_SERVO_POS + SERVO_PRESS_ANGLE_UP :
            INITAL_SERVO_POS - SERVO_PRESS_ANGLE_DOWN;
#endif

    serv.attach(SERVO_PIN);
    setServ(angle);
    setServ( INITAL_SERVO_POS );
    serv.detach();
#endif
}

void testServo(){
    while(1){
        servoPress(1);
        delay(1000);
        servoPress(0);
        delay(1000);
    }
}
