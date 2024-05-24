#include "HID-Project.h"

#include "config.h"
#include "pin_map.h"
#include "debug.h"
#include <EEPROM.h>

#ifdef OLED_SCREEN
#include "OLED_Driver.h"
#define clear_screen() OLED_Clear(SCREEN_WIDTH, SCREEN_HEIGHT)
#define reset_cursor() OLED_Set_Cursor(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
#define write_word(w) OLED_WriteWord((w))
#else
#include "LCD_Driver.h"
#define clear_screen() LCD_Clear(SCREEN_WIDTH, SCREEN_HEIGHT, 0x0000)
#define reset_cursor() LCD_SetCursor(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
#define write_word(w) LCD_WriteData_Word((w))
#endif

//////////////////
// Controls OUT //
//////////////////

#define CHAR_LAST 'L'
#define CHAR_ERR 'E'

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

#define BYTE_TIMEOUT_MS 100

uint8_t rawhidData[CHUNK_BYTE_SIZE];

static uint8_t backlight;
void write_backlight(uint8_t bl){
#ifndef OLED_SCREEN
    EEPROM.write(0, bl); 
    backlight = bl;
#endif
}


///////////
// SETUP //
///////////
void setup(void) {
    RawHID.begin(rawhidData, sizeof(rawhidData));
    setup_debug();
#ifdef OLED_SCREEN
    OLED_Init();
    debugln("OLED");
#else
    debugln("LCD");
    backlight = EEPROM.read(0);
    LCD_Init(backlight);
#endif
    clear_screen();

    debug("Chunk Size: ");
    debugSln(CHUNK_BYTE_SIZE);
}



void send_err(){
    debugln("Err");
    RawHID.write(CHAR_ERR);
    delay(1); // allow 1ms writes to complete
    RawHID.enable(); // dump buffer
}


bool await_bytes_timeout(uint16_t size, uint16_t timeout){
    for(uint16_t i = 0; i < timeout; i++){
        delay(1);

        int bytesAvailable = RawHID.available();

        if(bytesAvailable == 0){continue;}

        if(bytesAvailable != size){
            send_err();
            return false;
        }
        return true;
    }
    return false; // timeout
}

bool _read_check_byte(char *c_out){
    char c = RawHID.read(); 
    RawHID.enable(); // set buffer as read

    if(c == CHAR_ERR){
        delay(2); // wait for 2ms to allow driver to purge buffer
        // TODO: purge buffer?
        return false;
    }
    *c_out = c;
    return true;
}

bool await_byte_timeout(char *c_out, uint16_t timeout){
    if(!await_bytes_timeout(2, timeout)){
        return false;
    }
    return _read_check_byte(c_out);
}


bool await_byte(char *c_out){
    while(1){
        delay(1);
        int bytesAvailable = RawHID.available();

        if(bytesAvailable == 0){continue;}

        if(bytesAvailable != 2){
            send_err();
            return false;
        }
        break;
    }
    return _read_check_byte(c_out);
}


void drawFrame(){
    // used for timeout, we start only when there is an inital byte
    uint32_t start_time = millis();

    uint16_t row = 0;
    uint16_t chunk = 0;
    reset_cursor();
    while(1){
        if(!await_bytes_timeout(CHUNK_BYTE_SIZE, BYTE_TIMEOUT_MS)){
            debugln("timeout");
            return;
        }
        
        { // push chunk to lcd
            uint16_t start = chunk*CHUNK_PIXEL_SIZE;
            for(int i = 0; i < CHUNK_PIXEL_SIZE; i++){
                write_word(((uint16_t *)rawhidData)[i]);
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
                RawHID.write(CHAR_LAST);
                break;
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
#ifdef OLED_SCREEN
    i[3] = 255;
#else
    i[3] = backlight;
#endif

    RawHID.write((uint8_t *)&i, sizeof(i));
    char c;
    await_byte_timeout(&c, BYTE_TIMEOUT_MS); // no need to check c or return, going back to loop anyway
}


void loop(){
    debugln("switch");
    char c;
    if(!await_byte(&c)){
        return;
    }
    switch (c) {
        // c is allowed to be reused past here
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
            if(!await_byte_timeout(&c, BYTE_TIMEOUT_MS)){
                return;
            }
            write_backlight(c);
            break;

        default:
            debug("Err Char: ");
            debugSln(c);
    }
}
