#ifndef _DEBUG_H
#define _DEBUG_H
#include <stdint.h>

#include "pin_map.h"
#include "config.h"

/////////////////////////
// DEBUG CONFIGURATION //
/////////////////////////
#ifdef DEBUG_ENABLED

#define BAUD 4800
#define SERIAL_DELAY_US 208

#define SERIAL_PIN 7
#define SERIAL_MASK (1<<SERIAL_PIN)

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

#define setup_debug() DDRD |= SERIAL_MASK; PORTD |= SERIAL_MASK; delay(10)


#define debug(x) serial_bb_print(x)
#define debugln(x) serial_bb_print(x); serial_bb_print("\n\r")
#define debugS(x) serial_bb_print(String(x).c_str())
#define debugSln(x) serial_bb_print(String(x).c_str()); serial_bb_print("\n\r")
#define debug_freeze() while(1);

/*
char const hex_chars[16] = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };

void _dumpBuffer(int bytesAvailable, uint8_t *buffer){
    for(int i = 0; i < CHUNK_BYTE_SIZE; i++){
        debug("0x");
        debug(buffer[i] < 16 ? "0" : "");
        debug(hex_chars[buffer[i]]);
        debug(" ");
    }
    debug("A: ");
    debugln(bytesAvailable);
}
*/
// #define debug_dump_buffer(a, b) _dumpBuffer(a, b)
#define debug_dump_buffer(a, b)

#else

#define setup_debug()
#define debug(x)
#define debugln(x)
#define debugS(x)
#define debugSln(x)
#define debug_freeze()
#define debug_dump_buffer(a, b)

#endif

#endif
