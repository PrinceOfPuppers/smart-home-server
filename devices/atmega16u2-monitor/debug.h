#ifndef _DEBUG_H
#define _DEBUG_H

// #define DEBUG_ENABLED

/////////////////////////
// DEBUG CONFIGURATION //
/////////////////////////
#ifdef DEBUG_ENABLED

#include <SoftwareSerial.h>
SoftwareSerial mySerial(D6, D7); // rx, tx
#define debug(x) mySerial.print(x)
#define debugln(x) mySerial.println(x)
#define debug_freeze() while(1);

void _dumpBuffer(int bytesAvailable, uint8_t *buffer){
    for(int i = 0; i < CHUNK_BYTE_SIZE; i++){
        mySerial.print("0x");
        mySerial.print(buffer[i] < 16 ? "0" : "");
        mySerial.print(buffer[i], HEX);
        mySerial.print(" ");
    }
    mySerial.print("A: ");
    mySerial.println(bytesAvailable);
}
#define debug_dump_buffer(a, b) _dumpBuffer(a, b)

#else

#define debug(x)
#define debugln(x)
#define debug_freeze()
#define debug_dump_buffer(a, b)

#endif

#endif
