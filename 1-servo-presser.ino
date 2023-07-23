#include <Servo.h>

#define SERVO_MOVE_DELAY 150

#define SERVO_PIN 7
#define INITAL_SERVO_POS 90
#define SERVO_PRESS_ANGLE_UP 17
#define SERVO_PRESS_ANGLE_DOWN 17

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

void servoPress(bool on){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Servo Press: ");
    Serial.println(on ? "ON" : "OFF");
#endif
    int angle = on ? INITAL_SERVO_POS + SERVO_PRESS_ANGLE_UP : 
                     INITAL_SERVO_POS - SERVO_PRESS_ANGLE_DOWN;
    setServ(angle);
    setServ( INITAL_SERVO_POS );
}

void setupServo(){
    serv.attach(SERVO_PIN);
    setServ(INITAL_SERVO_POS);

#if DEBUG_SERIAL_ENABLED
    Serial.println("Servo Setup");
#endif
}
