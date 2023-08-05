#if LIGHT_SENSOR_ENABLED

#define LIGHT_SENSOR_ENABLE_PIN 4
#define LIGHT_SENSOR_A_PIN A7

// miliseconds
#define LIGHT_SWITCH_RESPONSE_DELAY 100

static int lightMid = 0;

int readLightSensor() {
    int x = analogRead(LIGHT_SENSOR_A_PIN);
#if DEBUG_SERIAL_ENABLED
    Serial.print("Light Sensor Reading: ");
    Serial.println(x);
#endif
    return x;
}

void _lightSensitiveSwitch(bool on){
    int inital = readLightSensor();

    bool isOn = inital > lightMid;

    if ( on == isOn ){
        return;
    }

    servoPress(true);
    delay(LIGHT_SWITCH_RESPONSE_DELAY);
    int current = readLightSensor();
    if (
        on  && current < lightMid || // light was successfully turned off
        !on && current > lightMid    // light was successfully turned on
    ) { return; }

    servoPress(false);
    delay(LIGHT_SWITCH_RESPONSE_DELAY);
    return;
}
// turns light on/off depending on current state
void lightSensitiveSwitch(bool on){
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, HIGH);
    _lightSensitiveSwitch(on);
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

}

void calibrate(){
    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, HIGH);

    servoPress(true);
    int a = readLightSensor();
    delay(LIGHT_SWITCH_RESPONSE_DELAY);

    servoPress(false);
    int b = readLightSensor();
    delay(LIGHT_SWITCH_RESPONSE_DELAY);

    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

    int min = a < b ? a : b;
    int max = a < b ? b : a;
    int delta = max - min;

    lightMid = min + delta/2;

#if DEBUG_SERIAL_ENABLED
    if(delta < 50){
        Serial.print("Warning: Light Sensor on/off Delta Small: ");
        Serial.println(delta);
    }
#endif
}

void setupLightSensor(){
    pinMode(LIGHT_SENSOR_ENABLE_PIN, OUTPUT);
    pinMode(LIGHT_SENSOR_A_PIN, INPUT);

    calibrate();
#if DEBUG_SERIAL_ENABLED
    Serial.println("Light Sensor Setup and Calibrated");
#endif
}

#endif
