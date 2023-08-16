
// triggers
#define RX_ENABLED 1
#define MOTION_SENSOR_ENABLED 0

// actions
#define TX_ENABLED 1
#define SERVO_ENABLED 0

// modifiers
#define LIGHT_SENSOR_ENABLED 0

// debugging
#define DEBUG_LED_ENABLED 0
#define DEBUG_SERIAL_ENABLED 0


// sanity checks
#if MOTION_SENSOR_ENABLED && RX_ENABLED
    #error "Rx Trigger and Motion Trigger are Mutually Exclusive"
#endif
#if TX_ENABLED && SERVO_ENABLED
    #error "Tx Action and Servo Action are Mutually Exclusive"
#endif



// pull either pin low and restart to enter test mode
#define SERVO_TEST_PIN_1 11 // test with no on/off
#define SERVO_TEST_PIN_2 12 // test with on/off



////////////
// action //
////////////

#if SERVO_ENABLED
#define action(up) servoPress(up)
#define action servoPress
#elif TX_ENABLED
#define action(up) txTransmit(up)
#define action txTransmit
#else
// stub
void action(bool up){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Action Stub: ");
    Serial.println(up ? "UP" : "DOWN");
#endif
#if DEBUG_LED_ENABLED
    digitalWrite(LED_BUILTIN, 1);
#endif
}
#endif





//////////////////////
// action modifiers //
//////////////////////
#if LIGHT_SENSOR_ENABLED
void modAction(bool up){
    lightSensitiveSwitch(up, action);
}
#else
#define modAction(up) action(up)
#define modAction action
#endif




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

#if TX_ENABLED
    setupTx();
#endif

#if MOTION_SENSOR_ENABLED
    setupMotionSensor();
#endif

#if SERVO_ENABLED
    pinMode(SERVO_TEST_PIN_1, INPUT_PULLUP);
    pinMode(SERVO_TEST_PIN_2, INPUT_PULLUP);
    setupServo();
    // servo tests
    if(!digitalRead(SERVO_TEST_PIN_1)){
        testServoPot();
    }
    if(!digitalRead(SERVO_TEST_PIN_2)){
        testServo();
    }
    // disable pullups
    pinMode(SERVO_TEST_PIN_1, INPUT);
    pinMode(SERVO_TEST_PIN_2, INPUT);
#endif

#if LIGHT_SENSOR_ENABLED
    setupLightSensor(action);
#endif

#if DEBUG_SERIAL_ENABLED
    Serial.println("Setup Complete");
    Serial.flush();
#endif
}



void loop() {
    // tests:
    // testServo();
    // testServoPot();
    // testServoRange();
    // testLightSensor(action);
    // testRx();

    //////////////
    // triggers //
    //////////////
#if MOTION_SENSOR_ENABLED
    motionOnOff(modAction);

#elif RX_ENABLED
    runOnCodeMatch(modAction);
#else
#error "At Least 1 Trigger is Required"
#endif
}

