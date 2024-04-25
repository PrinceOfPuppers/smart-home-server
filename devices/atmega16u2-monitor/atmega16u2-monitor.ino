#include "pin_map.h"

#include "DEV_Config.h"
#include "LCD_Driver.h"

#include "HID-Project.h"

// #define DEBUG_ENABLED

#define BLACK 0x0000


#define SCREEN_WIDTH 160
#define SCREEN_HEIGHT 128

// number of chunkes each horizontal line is divided into
// SCREEN_WIDTH/CHUNKS_PER_LINE is the number of pixels updated at once
#ifdef DEBUG_ENABLED
#define CHUNKS_PER_LINE SCREEN_WIDTH
#else
#define CHUNKS_PER_LINE 8
#endif

#if SCREEN_WIDTH % CHUNKS_PER_LINE != 0
#error "screen width must be divisable by the number of chunks per line"
#endif

#define CHUNK_PIXEL_SIZE (SCREEN_WIDTH/CHUNKS_PER_LINE)
// each pixel is 16 bits
#define CHUNK_BYTE_SIZE (2*CHUNK_PIXEL_SIZE)

uint8_t rawhidData[CHUNK_BYTE_SIZE];




#ifdef DEBUG_ENABLED

#include <SoftwareSerial.h>
SoftwareSerial mySerial(D6, D7); // rx, tx
#define debug(x) mySerial.print(x)
#define debugln(x) mySerial.println(x)
#define debug_freeze() while(1);

void _dumpBuffer(int bytesAvailable){
    for(int i = 0; i < CHUNK_BYTE_SIZE; i++){
        mySerial.print("0x");
        mySerial.print(rawhidData[i] < 16 ? "0" : "");
        mySerial.print(rawhidData[i], HEX);
        mySerial.print(" ");
    }
    mySerial.print("A: ");
    mySerial.println(bytesAvailable);
}
#define debug_dump_buffer(x) _dumpBuffer(x)

#else

#define debug(x)
#define debugln(x)
#define debug_freeze()
#define debug_dump_buffer(x)

#endif

void setup(void) {
    RawHID.begin(rawhidData, sizeof(rawhidData));
#ifdef DEBUG_ENABLED
    mySerial.begin(9600);
#endif
    Config_Init();
    LCD_Init();
    LCD_Clear(BLACK);

    debug("Setup Done, Chunk Byte Size: ");
    debugln(CHUNK_BYTE_SIZE);
}

// TODO: add debounce for updates that are too soon

#define FRAME_TIMEOUT 10 * 60 * 1000 * 1000
void drawFrame(){
    // only start when bytes are available
    int bytesAvailable = RawHID.available();
    if(!bytesAvailable){
        delay(1);
        return;
    }

    // used for timeout, we start only when there is an inital byte
    uint32_t start = millis();
    debugln("New Frame");

    uint16_t row = 0;
    uint16_t chunk = 0;
    while(1){
        delay(1);

        /*
        // check timeout
        if(millis() - start > FRAME_TIMEOUT){
            break;
        }
        */

        auto bytesAvailable = RawHID.available();

        if(bytesAvailable == 0){continue;}
        debug_dump_buffer(bytesAvailable);

        if(bytesAvailable != CHUNK_BYTE_SIZE){
            debug("Invalid Chunk Size: ");
            debugln(bytesAvailable);
            debug_freeze();
            continue;
        }
        
        uint16_t start = chunk*CHUNK_PIXEL_SIZE;
        for(int i = 0; i < CHUNK_PIXEL_SIZE; i++){
            LCD_SetUWORD(start+i, row, ((uint16_t *)rawhidData)[i]);
        }

        // resets RawHID.available()
        RawHID.enable();
        RawHID.write("A");

        chunk++;
        if(chunk >= CHUNKS_PER_LINE){
            // move to next line
            chunk = 0;
            row++;
            debug("newline, row: ");
            debugln(row);

            if (row >= SCREEN_HEIGHT){
                break;
            }
        }

    }

}

// void drawFrame(){}

void loop(){
    drawFrame();
}
