#include "HID-Project.h"
#include "LCD_Driver.h"

#include "buttons.h"
#include "config.h"
#include "pin_map.h"
#include "debug.h"
#include <EEPROM.h>

uint8_t rawhidData[CHUNK_BYTE_SIZE];

static uint8_t backlight;
void write_backlight(uint8_t bl){
    EEPROM.write(0, bl); 
    backlight = bl;
}


///////////
// SETUP //
///////////
void setup(void) {
    RawHID.begin(rawhidData, sizeof(rawhidData));
    setup_debug();
    backlight = EEPROM.read(0);
    // LCD_Init(SCREEN_WIDTH, SCREEN_HEIGHT, CS_PIN, RST_PIN, DC_PIN, BL_PIN);
    LCD_Init(backlight);
    LCD_Clear(0x0000);


    setup_buttons();

    debug("Chunk Size: ");
    debugSln(CHUNK_BYTE_SIZE);
}

//////////////////
// Controls OUT //
//////////////////

#define CHAR_LAST 'L'
#define CHAR_ERR 'E'
#define CHAR_TIMEOUT 'T'
// button controls
#define CHAR_NEXT 'N'
#define CHAR_PREV 'P'

/////////////////
// Controls IN //
/////////////////

// request monitor info
#define CHAR_INFO 'I'
#define CHAR_START 'S'
#define CHAR_BACKLIGHT 'B'

///////////////////
// Controls BOTH //
///////////////////
#define CHAR_ACK 'A'


void err_invalid_chunk(int bytesAvailable){
    debug("Inv Chunk Size: ");
    debugSln(bytesAvailable);
    debug_freeze(); // during testing everything should stop
    RawHID.enable();
    RawHID.write(CHAR_ERR);
}

char blocking_read_char(){
    int bytesAvailable;
    while( (bytesAvailable = RawHID.available()) == 0 ){
        delay(1);
    }
    if(bytesAvailable != 2){
        err_invalid_chunk(bytesAvailable);
    }
    char c = RawHID.read(); 
    RawHID.enable(); // set buffer as read
    
    return c;
}

#ifdef DEBUG_ENABLED
#define await_ack() { char __c = blocking_read_char(); if(__c != 'A') {debug("expected A got: "); debugSln(__c);} }
#else
#define await_ack() blocking_read_char()
#endif


#define FRAME_TIMEOUT_MS 60 * 1000
void drawFrame(){
    // used for timeout, we start only when there is an inital byte
    uint32_t start_time = millis();

    uint16_t row = 0;
    uint16_t chunk = 0;
    LCD_SetCursor(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
    while(1){
        delay(1);

        // check timeout
        if(millis() - start_time > FRAME_TIMEOUT_MS){
            RawHID.write(CHAR_TIMEOUT);
            break;
        }


        { // check bytes avalible
            int bytesAvailable = RawHID.available();

            if(bytesAvailable == 0){continue;}
            debug_dump_buffer(bytesAvailable, rawhidData);

            if(bytesAvailable != CHUNK_BYTE_SIZE){
                err_invalid_chunk(bytesAvailable);
                return;
            }
        }
        
        { // push chunk to lcd
            uint16_t start = chunk*CHUNK_PIXEL_SIZE;
            for(int i = 0; i < CHUNK_PIXEL_SIZE; i++){
                LCD_WriteData_Word(((uint16_t *)rawhidData)[i]);
            }
        }

        // resets RawHID.available()
        RawHID.enable();

        chunk++;
        if(chunk >= CHUNKS_PER_LINE){
            // move to next line
            chunk = 0;
            row++;

            if (row >= SCREEN_HEIGHT){
                break;
                RawHID.write(CHAR_LAST);
            }
        }

        RawHID.write(CHAR_ACK);

    } // end loop
}

void send_monitor_info(){
    delay(1);
    uint16_t i[4];
    i[0] = SCREEN_WIDTH;
    i[1] = SCREEN_HEIGHT;
    i[2] = CHUNK_BYTE_SIZE;
    i[3] = backlight;

    RawHID.write((uint8_t *)&i, sizeof(i));
    await_ack();
}


void loop(){
    debugln("switch");
    int c = blocking_read_char();
    switch (c) {
      case CHAR_START:
        debugln("start");
        RawHID.write(CHAR_ACK);
        drawFrame();
        break;
      case CHAR_INFO:
        debugln("req");
        send_monitor_info();
        break;
      case CHAR_BACKLIGHT:
        debugln("bl");
        RawHID.write(CHAR_ACK);
        write_backlight(blocking_read_char());
        break;

      default:
        debug("Wrong Char: ");
        debugSln(c);
        // code block
    }
}
