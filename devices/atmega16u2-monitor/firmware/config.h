#ifndef _CONFIG_H
#define _CONFIG_H

// #define DEBUG_ENABLED

// 1.8 inch
// #define SCREEN_WIDTH 160
// #define SCREEN_HEIGHT 128

// 1.5 inch
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 128


// comment out to use lcd instead 
#define OLED_SCREEN

/*
#define CS_PIN  D0
#define DC_PIN  D1
#define RST_PIN D2
#define BL_PIN  B7
*/

// number of chunkes each horizontal line is divided into
// SCREEN_WIDTH/CHUNKS_PER_LINE is the number of pixels updated at once
#ifdef DEBUG_ENABLED
#define CHUNKS_PER_LINE 4
#else
#define CHUNKS_PER_LINE 2
#endif

#if SCREEN_WIDTH % CHUNKS_PER_LINE != 0
#error "screen width must be divisable by the number of chunks per line"
#endif

#define CHUNK_PIXEL_SIZE (SCREEN_WIDTH/CHUNKS_PER_LINE)
// each pixel is 16 bits
#define CHUNK_BYTE_SIZE (2*CHUNK_PIXEL_SIZE)


#endif