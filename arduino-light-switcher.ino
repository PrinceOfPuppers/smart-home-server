#define RX_ENABLED 1
#define SERVO_ENABLED 1
#define MOTION_SENSOR_ENABLED 0
#define LIGHT_SENSOR_ENABLED 1

#define DEBUG_LED_ENABLED 0
#define DEBUG_SERIAL_ENABLED 0

#if MOTION_SENSOR_ENABLED && RX_ENABLED
    #error "RX Trigger and Motion Trigger are Mutually Exclusive"
#endif

// pull either pin low and restart to enter test mode
#define SERVO_TEST_PIN_1 11 // test with no on/off
#define SERVO_TEST_PIN_2 12 // test with on/off

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
    setupLightSensor();
#endif

#if DEBUG_SERIAL_ENABLED
    Serial.println("Setup Complete");
    Serial.flush();
#endif
}

#if LIGHT_SENSOR_ENABLED
static void (* lightPresser)(bool) = lightSensitiveSwitch;
#else
static void (* lightPresser)(bool) = servoPress;
#endif

void loop() {
    // testServo();
    // testServoPot();
    // testServoRange();
    // testLightSensor();
    // testRx();
#if MOTION_SENSOR_ENABLED
    motionOnOff(lightPresser);
#endif

#if RX_ENABLED
    runOnCodeMatch(lightPresser);
#endif
}

