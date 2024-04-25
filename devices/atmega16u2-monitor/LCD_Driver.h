/*****************************************************************************
* | File        :   LCD_Driver.h
* | Author      :   Waveshare team
* | Function    :   Electronic paper driver
* | Info        :
*----------------
* | This version:   V1.0
* | Date        :   2018-11-18
* | Info        :   
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
#ifndef __LCD_DRIVER_H
#define __LCD_DRIVER_H

#define LCD_WIDTH   160 //LCD width
#define LCD_HEIGHT  128 //LCD height

#define DEV_CS_PIN  13
#define DEV_DC_PIN  14
#define DEV_RST_PIN 15
#define DEV_BL_PIN  7

#include <stdint.h>
#include <stdio.h>
#include <SPI.h>
#include <avr/pgmspace.h>

/*-----------------------------------------------------------------------------*/
void LCD_WriteData_Byte(uint8_t da); 
void LCD_WriteData_Word(uint16_t da);
void LCD_WriteReg(uint8_t da);

void LCD_SetCursor(uint16_t x1, uint16_t y1, uint16_t x2,uint16_t y2);
void LCD_Setuint16_t(uint16_t x, uint16_t y, uint16_t Color);

void LCD_Init(void);
void LCD_SetBacklight(uint16_t Value);
void LCD_Clear(uint16_t Color);

#endif
