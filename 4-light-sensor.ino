#if LIGHT_SENSOR_ENABLED

#define LIGHT_SENSOR_ENABLE_PIN 4
#define LIGHT_SENSOR_A_PIN A7

static int lightMid = 0;

void _lightSensitiveSwitch(bool on){
    int inital = analogRead(LIGHT_SENSOR_A_PIN);

    bool isOn = inital > lightMid;

    if ( on == isOn ){
        return;
    }

    servoPress(true);
    int current = analogRead(LIGHT_SENSOR_A_PIN);
    if ( 
        on  && current < lightMid || // light was successfully turned off
        off && current > lightMid    // light was successfully turned on
    ) { return; }

    servoPress(false);
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
    int a = analogRead(LIGHT_SENSOR_A_PIN);

    servoPress(false);
    int b = analogRead(LIGHT_SENSOR_A_PIN);

    digitalWrite(LIGHT_SENSOR_ENABLE_PIN, LOW);

    int min = a < b ? a : b;
    int max = a < b ? b : a;

    lightMid = min + (max - min)/2;
}

void setupLightSensor(){
    pinMode(LIGHT_SENSOR_ENABLE_PIN, OUTPUT);
    pinMode(LIGHT_SENSOR_A_PIN, INPUT);

    calibrate();
}

#endif
