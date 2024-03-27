#include <Encoder.h>

#define MOTOR_UP_PIN 11
#define MOTOR_DOWN_PIN 12

// used for calibrating speed at which motor is considered stalled
#define MOTOR_STALL_POT_ENABLE_PIN 7
#define MOTOR_STALL_POT_PIN A1

// pot calibration goes from zero to this number, units are encoder steps per second
// (should essentially be the motors max speed, pot adjusts down from there)
#define MAX_MOTOR_STALL_SPEED 4000.

#define ENCODER_A_PIN 8
#define ENCODER_B_PIN 9


void motor_stop(){
    digitalWrite(MOTOR_DOWN_PIN, LOW);
    digitalWrite(MOTOR_UP_PIN, LOW);
}


// for timeout
static long _last_move_time = 0;

void motor_move(bool up){
    motor_stop();
    _last_move_time = millis();
    if(up){
        digitalWrite(MOTOR_UP_PIN, HIGH);
        return;
    }
    digitalWrite(MOTOR_DOWN_PIN, HIGH);
}


void check_motor_timeout(int timeout_secs){
    long now = millis();
    if (now - _last_move_time > 1e3*timeout_secs){
        motor_stop();
    }
}

// set during setup, speeds below this are considered stall
static long min_encoder_step_per_sec = 0;
void check_motor_stall(){

    // grace period 
    long now = millis();
    if (now - _last_move_time < 100){
        return;
    }

    double s = get_speed();
    if(abs(s) < min_encoder_step_per_sec){
        motor_stop();
    }
}

static long _last_pos = 0;
static unsigned long _last_micros = 0;

Encoder encoder(ENCODER_A_PIN, ENCODER_B_PIN);

void poll_encoder(){
    encoder.read();
}

// in encoder steps/sec
double get_speed(){
    long new_pos = encoder.read();
    unsigned long new_micros = micros();
    long dx = 1e6*(new_pos - _last_pos);
    long dt = new_micros - _last_micros;

    _last_pos = new_pos;
    _last_micros = new_micros;

    double s = ((double)dx)/((double)dt);

    return s;
}

float _getStallCalPotValue(){
    digitalWrite(MOTOR_STALL_POT_ENABLE_PIN, HIGH);
    delay(10);
    int a = analogRead(MOTOR_STALL_POT_PIN);
    digitalWrite(MOTOR_STALL_POT_ENABLE_PIN, LOW);

    // value between 0 and 1 corrisponding to pot rotation
    return a/1023.;
}

void setup_motor(){
    min_encoder_step_per_sec = lround(MAX_MOTOR_STALL_SPEED * _getStallCalPotValue());

    pinMode(MOTOR_UP_PIN, OUTPUT);
    pinMode(MOTOR_DOWN_PIN, OUTPUT);

    // prime encoder data
    _last_pos = encoder.read();
    _last_micros = micros();
}

void debug_mode_pot(){
    while(true){
        min_encoder_step_per_sec = lround(MAX_MOTOR_STALL_SPEED * _getStallCalPotValue());
        digitalWrite(LED_BUILTIN, HIGH);
        delay(min_encoder_step_per_sec);
        digitalWrite(LED_BUILTIN, LOW);
        delay(100);
    }
}




