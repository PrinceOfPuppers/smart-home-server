#if POWER_TRIGGER_ENABLED

// analog measurement defines
#define POWER_APIN A5
#define POWER_A_READ_THRESHOLD 3

// calibration defines
#define POWER_CALIBRATE_DELAY 2
#define POWER_CALIBRATE_CYCLES 15
static bool calibrate = true;
static int calibrateValue = 5000;
static uint8_t currentCycles = 0;

/*
void readPowerTrigger(){
    int val = analogRead(POWER_APIN);

    Serial.print("Cal:");
    Serial.print(calibrateValue);
    Serial.print(" ");

    Serial.print("Val: ");
    Serial.println(val);
}
*/

void calibrateHelper(){
    int x = analogRead(POWER_APIN);
    bool withinThreshold = x==calibrateValue;
    currentCycles = withinThreshold ? currentCycles + 1 : 0;

    calibrateValue = x;

    if(currentCycles > POWER_CALIBRATE_CYCLES){
        calibrate = false;
        digitalWrite(LED_BUILTIN, LOW);
    }
    delay(POWER_CALIBRATE_DELAY);
}

void setupPowerTrigger(void(*modAction)(bool)) {

#if DEBUG_LED_ENABLED
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
#endif
    
    modAction(true);
    while(calibrate){
        calibrateHelper();
    }
#if DEBUG_SERIAL_ENABLED
    Serial.println("Power Trigger Setup")
#endif
}


void powerTrigger(void(*modAction)(bool)){
    int r;
    while(1){
        r = analogRead(POWER_APIN);
        if( r - calibrateValue < POWER_A_READ_THRESHOLD){return;}
        // redundant measurement
        //r = analogRead(POWER_APIN);
        //if( r - calibrateValue < POWER_A_READ_THRESHOLD){return;}

        modAction(false);

        // for debugging erronious triggers
#if DEBUG_LED_ENABLED
        digitalWrite(LED_BUILTIN, HIGH);
#endif
#if DEBUG_SERIAL_ENABLED
        Serial.println("Power Off Detected!")
#endif
        delay(4294967295); // sleep till power off
    }
}

#endif
