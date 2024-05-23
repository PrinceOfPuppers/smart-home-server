#include "debug.h"

#include <Arduino.h>
#include <stdint.h>

#ifdef DEBUG_ENABLED
void serial_bb_print(const char *x){
    // presuming len is less than 255
    uint8_t i = 0;
    uint8_t j = 0;

    while(x[i] != '\0'){
        // start pull low
        PORTD &= ~SERIAL_MASK;
        for(j = 0; j < 8; j++){
            delayMicroseconds(SERIAL_DELAY_US);
            PORTD = x[i] & (1<< (j)) ? 
                (PORTD | SERIAL_MASK)  :    // high
                (PORTD & ~SERIAL_MASK) ;  // low
        }
        delayMicroseconds(SERIAL_DELAY_US);
        PORTD |= SERIAL_MASK; // end high
        delayMicroseconds(SERIAL_DELAY_US);
        i++;
    }
}
#endif
