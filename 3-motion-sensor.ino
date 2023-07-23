#if MOTION_SENSOR_ENABLED

#define MOTION_SENSOR_PIN 5


void setupMotionSensor(){
    pinMode(MOTION_SENSOR_PIN, INPUT);

#if DEBUG_SERIAL_ENABLED
    Serial.println("Motion Sensor Setup");
#endif

}

// calls cb when motion starts (bool true) or stops (bool false)
void motionStartStop(){
    int prevState = LOW;
    int state = LOW;

    while(1){
        state = digitalRead(MOTION_SENSOR_PIN);

        if(state == prevState){
            // no change
            continue;
        }

        if(state == HIGH){
            // movement detected
#if DEBUG_LED_ENABLED
            digitalWrite(LED_BUILTIN, HIGH);
#endif
#if DEBUG_SERIAL_ENABLED
            Serial.println("Motion Started");
#endif
        }
        else {
            // no movement detected
#if DEBUG_LED_ENABLED
            digitalWrite(LED_BUILTIN, LOW);
#endif
#if DEBUG_SERIAL_ENABLED
            Serial.println("Motion Stopped");
#endif
        }
        prevState = state;

    }
}

#endif
