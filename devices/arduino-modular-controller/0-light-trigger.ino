#if LIGHT_TRIGGER_ENABLED

#define LIGHT_TRIGGER_A_PIN A7

// on/off enable, 
#define LIGHT_TRIGGER_PRESS_ON 1
#define LIGHT_TRIGGER_PRESS_OFF 0

#define LIGHT_TRIGGER_MIN_LIGHT_DELTA 10 // from off to on
#define LIGHT_TRIGGER_CHANGE_SAMPLES 4

#define LIGHT_TRIGGER_CALIBRATE_SAMPLES 4
#define LIGHT_TRIGGER_CALIBRATE_SAMPLE_DELAY 100
static int maxLow = 0; // values above this will trigger on
                        //
#define aboveThreashold(value) ((value) > (maxLow + LIGHT_TRIGGER_MIN_LIGHT_DELTA))

static int readLightTrigger() {
    int x = analogRead(LIGHT_TRIGGER_A_PIN);
#if DEBUG_SERIAL_ENABLED
    Serial.print("Light Sensor Reading: ");
    Serial.println(x);
#endif
    return x;
}

static void calibrate(){
    int sample = 0;
    maxLow = 0;
    for(int i = 0; i < LIGHT_TRIGGER_CALIBRATE_SAMPLES; i++){
        sample = readLightTrigger();
        maxLow = sample > maxLow ? sample : maxLow;
        delay(LIGHT_TRIGGER_CALIBRATE_SAMPLE_DELAY);
    }
#if DEBUG_SERIAL_ENABLED
    Serial.print("Light Calibrate Max Low: ");
    Serial.println(maxLow);
#endif
}

void lightTrigger(void(*action)(bool)){
    bool on = 0;
    uint16_t changeCounter = 0;

    while(1){
        delay(1);
        if ( aboveThreashold(readLightTrigger()) ){
            if(!on){ changeCounter += 1; } // off and light is above trigger
            else { changeCounter = 0; }   // on and light is below trigger
        } else {
            if(on){ changeCounter += 1; } // on and light is below trigger
            else { changeCounter = 0; }   // off and light is below trigger
        }

        if ( changeCounter > LIGHT_TRIGGER_CHANGE_SAMPLES ){
            changeCounter = 0;
            if (on){ // turn off
                on = 0;
#if LIGHT_TRIGGER_PRESS_OFF
            action(0);
#endif
            }
            else { // turn on
            on = 1;
#if LIGHT_TRIGGER_PRESS_ON
            action(1);
#endif
            }
        }

    }
}

void setupLightTrigger(){
    pinMode(LIGHT_TRIGGER_A_PIN, INPUT);

    calibrate();
#if DEBUG_SERIAL_ENABLED
    Serial.println("Light Sensor Setup and Calibrated");
#endif
}

void testLightTrigger(){
    while(1){

#if DEBUG_SERIAL_ENABLED
        Serial.println("Light Trigger Test Sequence Start");
        Serial.println("Getting Light Calibration a in...");
        Serial.println("3");
        delay(1000);
        Serial.println("2");
        delay(1000);
        Serial.println("1");
        delay(1000);
        calibrate();
        delay(1000);

        Serial.println("Getting Light Sample in...");
        Serial.println("3");
        delay(1000);
        Serial.println("2");
        delay(1000);
        Serial.println("1");
        delay(1000);
        if ( aboveThreashold(readLightTrigger()) ){
            Serial.println("Sample Above On Threashold!");
        }
        else {
            Serial.println("Sample Below On Threashold!");
        }

        delay(5000);
#else
        // requires serial debugging
        delay(1000);
#endif
    }

}

#endif
