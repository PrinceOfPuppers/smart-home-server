#define RX_ENABLED 1
#define MOTION_SENSOR_ENABLED 0
#define LIGHT_SENSOR_ENABLED 0

#define DEBUG_LED_ENABLED 0
#define DEBUG_SERIAL_ENABLED 0

void setup() {
#if DEBUG_SERIAL_ENABLED
    Serial.begin(9600);
#endif 

#if DEBUG_LED_ENABLED
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
#endif 


#if RX_ENABLED
    setupRx();
#endif

#if MOTION_SENSOR_ENABLED
    setupMotionSensor();
#endif

    setupServo();

#if DEBUG_SERIAL_ENABLED
    Serial.println("Setup Complete");
#endif
}


void loop() {
#if MOTION_SENSOR_ENABLED
    motionStartStop();
#endif

#if RX_ENABLED
    runOnCodeMatch(servoPress);
#endif
}

