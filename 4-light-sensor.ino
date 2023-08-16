#if LIGHT_SENSOR_ENABLED

#define LIGHT_SENSOR_ENABLE_PIN 4
#define LIGHT_SENSOR_A_PIN A7

#define MIN_LIGHT_DELTA 100

// miliseconds
#define LIGHT_SWITCH_RESPONSE_DELAY 150

static int lightMid = 0;

int getMid(int a, int b){
    int min = a < b ? a : b;
    int max = a < b ? b : a;
    int delta = max - min;
#if DEBUG_SERIAL_ENABLED
    if(delta < MIN_LIGHT_DELTA){
        Serial.print("Warning: Light Sensor on/off Delta Small: ");
        Serial.println(delta);
    }
#endif
    return min + delta/2;
}

int readLightSensor() {
    int x = analogRead(LIGHT_SENSOR_A_PIN);
#if DEBUG_SERIAL_ENABLED
    Serial.print("Light Sensor Reading: ");
    Serial.println(x);
#endif
    return x;
}

void _lightSensitiveSwitch(bool on, void(*action)(bool)){
    // for debugging
    int initalMid = lightMid;

    int a = readLightSensor();

    bool isOn = a > lightMid;

    if ( on == isOn ){
        return;
    }

    (*action)(true);
    delay(LIGHT_SWITCH_RESPONSE_DELAY);
    int b = readLightSensor();

    // recalibrate if light changed
    if (abs(a-b) > MIN_LIGHT_DELTA) {
        lightMid = getMid(a,b);
    }

    if (
        !on && b < lightMid || // light was successfully turned off
        on  && b > lightMid    // light was successfully turned on
    ) { return; }

    (*action)(false);
    delay(LIGHT_SWITCH_RESPONSE_DELAY);

    // catch errors
    int c = readLightSensor();
    // recalibrate if light changed
    if (abs(b - c) > MIN_LIGHT_DELTA) {
        lightMid = getMid(b, c);
    }

    if (
        !on && c < lightMid || // light was successfully turned off
        on  && c > lightMid    // light was successfully turned on
    ) { return; }

    // inital position of light was correct, lightMid was incorrect
    (*action)(true);

#if DEBUG_SERIAL_ENABLED
    Serial.print("Error: Light Sensitive Switch Was Miscalibrated\nInital lightMid: ");
    Serial.println(initalMid);
    Serial.print("Current lightMid: ");
    Serial.println(lightMid);
    Serial.print("a: ");
    Serial.println(a);
    Serial.print("b: ");
    Serial.println(b);
    Serial.print("c: ");
    Serial.println(c);
#endif

    return;
}
// turns light on/off depending on current state
void lightSensitiveSwitch(bool on, void(*action)(bool)){
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, HIGH);
    _lightSensitiveSwitch(on, action);
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

}

int calibrateHelper(bool onOff, void(*action)(bool)){
    (*action)(onOff);
    int x = readLightSensor();
    delay(LIGHT_SWITCH_RESPONSE_DELAY);
    return x;
}


void calibrate(void(*action)(bool)){
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, HIGH);

    int a = calibrateHelper(true, action);
    int b = calibrateHelper(false, action);

    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

    lightMid = getMid(a, b);

}

void setupLightSensor(void(*action)(bool)){
    pinMode(LIGHT_SENSOR_ENABLE_PIN, OUTPUT);
    pinMode(LIGHT_SENSOR_A_PIN, INPUT);

    calibrate(action);
#if DEBUG_SERIAL_ENABLED
    Serial.println("Light Sensor Setup and Calibrated");
#endif
}

void testLightSensor(void(*action)(bool)){
    while(1){
#if DEBUG_SERIAL_ENABLED
        digitalWrite(LIGHT_SENSOR_ENABLE_PIN, HIGH);
        Serial.println("Light Sensor Test Sequence Start");
        Serial.println("Getting Light Sample a in...");
        Serial.println("3");
        delay(1000);
        Serial.println("2");
        delay(1000);
        Serial.println("1");
        delay(1000);
        int a = calibrateHelper(true, action);
        Serial.println("Sample a recieved!");
        delay(1000);

        Serial.println("Getting Light Sample B in...");
        Serial.println("3");
        delay(1000);
        Serial.println("2");
        delay(1000);
        Serial.println("1");
        delay(1000);
        int b = calibrateHelper(false, action);
        Serial.println("Sample b recieved!");
        delay(1000);
        digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

        Serial.print("Values \na: ");
        Serial.print(a);
        Serial.print(" b: ");
        Serial.println(b);
        Serial.print("Midpoint: ");
        int x = getMid(a, b);
        Serial.println(x);
        delay(5000);
#else
        // requires serial debugging
        delay(1000);
#endif
    }

}

#endif
