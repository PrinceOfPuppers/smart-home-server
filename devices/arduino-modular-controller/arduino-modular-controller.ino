// number of times an action is done per trigger
#define ACTION_REPEATS 4
#define ACTION_REPEATS_DELAY_MS 500

// triggers
#define LIGHT_TRIGGER_ENABLED 1
#define RX_ENABLED 0
#define MOTION_SENSOR_ENABLED 0
#define POWER_TRIGGER_ENABLED 0

// actions
#define TX_ENABLED 0
#define SERVO_ENABLED 1

// modifiers
#define LIGHT_SENSOR_ENABLED 0

// debugging
#define DEBUG_LED_ENABLED 0
#define DEBUG_SERIAL_ENABLED 0


// sanity checks
#if MOTION_SENSOR_ENABLED + RX_ENABLED + POWER_TRIGGER_ENABLED + LIGHT_TRIGGER_ENABLED > 1
    #error "Rx Trigger, Motion Trigger and Power Trigger are Mutually Exclusive"
#endif
#if TX_ENABLED && SERVO_ENABLED
    #error "Tx Action and Servo Action are Mutually Exclusive"
#endif

#if LIGHT_TRIGGER_ENABLED && LIGHT_SENSOR_ENABLED
    #error "Light Sensor and Light Trigger are Mutually Exclusive"
#endif



// pull either pin low and restart to enter test mode
#define SERVO_TEST_PIN_1 11 // test with no on/off
#define SERVO_TEST_PIN_2 12 // test with on/off



////////////
// action //
////////////

#if SERVO_ENABLED
#define _action(up) servoPress(up)
#define _action servoPress
#elif TX_ENABLED
#define _action(up) txTransmit(up)
#define _action txTransmit
#else
// stub
void _action(bool up){
#if DEBUG_SERIAL_ENABLED
    Serial.print("Action Stub: ");
    Serial.println(up ? "UP" : "DOWN");
#endif
#if DEBUG_LED_ENABLED
    digitalWrite(LED_BUILTIN, 1);
#endif
}
#endif


#if ACTION_REPEATS > 1
void action(bool up){
    for(int i = 0; i < ACTION_REPEATS; i++){
        _action(up);
        delay(ACTION_REPEATS_DELAY_MS);
    }
}
#else
// if action is only done once, there is no need to add an additional function call
// (relevant for time sensitive actions like power switch)
#define action(up) _action(up)
#define action _action
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

    // actions
#if TX_ENABLED
    setupTx();
#elif SERVO_ENABLED
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

    // mods
#if LIGHT_SENSOR_ENABLED
    setupLightSensor(action);
#endif

    // triggers
#if MOTION_SENSOR_ENABLED
    setupMotionSensor();
#elif RX_ENABLED
    setupRx();
#elif POWER_TRIGGER_ENABLED
    setupPowerTrigger(modAction);
#elif LIGHT_TRIGGER_ENABLED
    setupLightTrigger();
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
    // testLightTrigger();
    // testServo90();

    //////////////
    // triggers //
    //////////////
#if MOTION_SENSOR_ENABLED
    motionOnOff(modAction);
#elif RX_ENABLED
    runOnCodeMatch(modAction);
#elif POWER_TRIGGER_ENABLED
    powerTrigger(modAction);
#elif LIGHT_TRIGGER_ENABLED
    lightTrigger(modAction);
#else
#error "At Least 1 Trigger is Required"
#endif
}

