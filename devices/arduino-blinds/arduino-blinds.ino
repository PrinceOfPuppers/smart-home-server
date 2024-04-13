// #define DEBUG_SERIAL

#define MOTOR_TIMEOUT_SECS 3*60

#define PUSHED_NONE 0
#define PUSHED_UP 1
#define PUSHED_DOWN 2

#define RX_NONE 0
#define RX_UP 1
#define RX_DOWN 2

// enum for setup_buttons return, if buttons are held during boot
#define NO_BUTTON 0
#define DEBUG_POT 1
#define PROGRAM_RX 2

void setup() {
#ifdef DEBUG_SERIAL
    Serial.begin(9600);
#endif

    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);

    // if down button is pressed during startup, enter debug mode potentiometer
    int button_ret = setup_buttons();
    setup_motor();

    if(button_ret == DEBUG_POT){
        debug_mode_pot();
    }
    setup_rx(button_ret == PROGRAM_RX );


#ifdef DEBUG_SERIAL
    Serial.println("Setup Complete");
    Serial.flush();
#endif
}

uint32_t counter = 0;

void loop() {
    poll_encoder();
    counter++;

    switch(counter % 1000){
        // check rx recieved
        case 3: {
            int heard = get_rx_heard();
            if(heard == PUSHED_NONE) {return;}
            motor_move(heard == RX_UP);
            break;
        }

        // check button
        case 2:{
            int pushed = get_button_pushed();
            if(pushed == PUSHED_NONE) {return;}
            motor_move(pushed == PUSHED_UP);
            break;
        }

        // check stall
        case 1:{
            check_motor_stall();
            break;
        }

        // check moving time
        case 0:{
            check_motor_timeout(MOTOR_TIMEOUT_SECS);
            break;
        }

        // update rx
        default:{
            update_rx();
        }
    }
    return;
}

