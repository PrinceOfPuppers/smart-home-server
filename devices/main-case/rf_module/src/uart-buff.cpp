#include "uart-buff.h"
#include <Arduino.h>
#include <stdint.h>
#include <string.h>

#define MAX_CHARS 63
static uint8_t inboundBuffIndex = 0;
// +1 for nullbyte
static char inboundBuff[MAX_CHARS + 1];
static char *rest = inboundBuff;

void buff_reset(){
    inboundBuffIndex = 0;
    inboundBuff[0] = '\0';
    rest = inboundBuff;
}

// returns 1 if buffer reset due to overflow
int buff_push_char(char c){
    if (inboundBuffIndex >= MAX_CHARS - 1) {
        buff_reset();
        return 1;
    }
    inboundBuff[inboundBuffIndex] = c;
    inboundBuff[inboundBuffIndex+1] = '\0';
    inboundBuffIndex++;
    return 0;
}


char *buff_strtok(const char* delim){
    return strtok_r(rest, delim, &rest);
}

