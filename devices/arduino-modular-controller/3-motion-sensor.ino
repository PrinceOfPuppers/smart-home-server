#if MOTION_SENSOR_ENABLED
#include <LowPower.h>

#define MOTION_SENSOR_PIN 3
#define MOTION_INT_PIN digitalPinToInterrupt(MOTION_SENSOR_PIN)

// interrupt cb for motion detector
void motionInt(){
#if DEBUG_SERIAL_ENABLED
    Serial.println("Motion Interrupt Called");
    Serial.flush();
#endif
}

void setupMotionSensor(){
    pinMode(MOTION_SENSOR_PIN, INPUT);

#if DEBUG_SERIAL_ENABLED
    Serial.println("Motion Sensor Setup");
#endif

}

void motionOnOff(void (* on_off_cb)(bool)){
    while(1){
        attachInterrupt(MOTION_INT_PIN, motionInt, CHANGE);
        LowPower.powerDown(SLEEP_FOREVER, ADC_OFF, BOD_OFF);
        detachInterrupt(MOTION_INT_PIN);

        int x = digitalRead(MOTION_SENSOR_PIN);
#if DEBUG_SERIAL_ENABLED
        Serial.print("Motion Sensor: ");
        Serial.println(x ? "Movement" : "Movement Stopped");
        Serial.flush();
#endif

#if DEBUG_LED_ENABLED
        digitalWrite(LED_BUILTIN, x);
#endif

        on_off_cb(x);
    }
}

#endif
