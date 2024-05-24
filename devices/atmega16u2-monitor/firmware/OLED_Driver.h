// Heavily modified Waveshare driver


/*****************************************************************************
* | File      	:   OLED_Driver.h
* | Author      :   Waveshare team
* | Function    :   1.5inch RGB OLED Module Drive function
* | Info        :
*----------------
* |	This version:   V2.0
* | Date        :   2020-08-20
* | Info        :
* -----------------------------------------------------------------------------
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#ifndef __OLED_DRIVER_H
#define __OLED_DRIVER_H		

#include <SPI.h>
#include <stdint.h>

/********************************************************************************
function:	
		Define the full screen height length of the display
********************************************************************************/

// port manipulation
#define PORT_DDR DDRD
#define PORT PORTD

// relative to port
#define DEV_CS_PIN  0
#define DEV_DC_PIN  1
#define DEV_RST_PIN 2

#define setup_port() PORT_DDR |= (1 << DEV_CS_PIN) | (1 << DEV_DC_PIN) | (1 << DEV_RST_PIN)
#define set_low(pin) PORT &= ~(1 << pin)
#define set_high(pin) PORT |= (1 << pin)

void OLED_WriteWord(uint16_t Data);
void OLED_Set_Cursor(uint8_t xstart, uint8_t ystart, uint8_t xend, uint8_t yend);
void OLED_Init(void);
void OLED_Clear(uint8_t width, uint8_t height);

#endif  
	 
