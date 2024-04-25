#include "pin_map.h"
#include "LCD_Driver.h"
#include "HID-Project.h"
#include "debug.h"

#define SCREEN_WIDTH 160
#define SCREEN_HEIGHT 128

/*
#define CS_PIN  D0
#define DC_PIN  D1
#define RST_PIN D2
#define BL_PIN  B7
*/

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


///////////
// SETUP //
///////////
void setup(void) {
    RawHID.begin(rawhidData, sizeof(rawhidData));
#ifdef DEBUG_ENABLED
    mySerial.begin(9600);
#endif
    // LCD_Init(SCREEN_WIDTH, SCREEN_HEIGHT, CS_PIN, RST_PIN, DC_PIN, BL_PIN);
    LCD_Init();
    LCD_Clear(0x0000);

    debug("Setup Done, Chunk Byte Size: ");
    debugln(CHUNK_BYTE_SIZE);
}

//////////
// MAIN //
//////////
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
        debug_dump_buffer(bytesAvailable, rawhidData);

        if(bytesAvailable != CHUNK_BYTE_SIZE){
            debug("Invalid Chunk Size: ");
            debugln(bytesAvailable);
            debug_freeze();
            continue;
        }
        
        uint16_t start = chunk*CHUNK_PIXEL_SIZE;
        LCD_SetCursor(start, row, start+CHUNK_PIXEL_SIZE, row);
        for(int i = 0; i < CHUNK_PIXEL_SIZE; i++){
            LCD_WriteData_Word(((uint16_t *)rawhidData)[i]);
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

void loop(){
    drawFrame();
}
