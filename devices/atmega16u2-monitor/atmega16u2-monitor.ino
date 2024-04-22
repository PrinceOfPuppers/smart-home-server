// #include <SoftWire.h>
// #include <LiquidCrystal_I2C.h>
// #include <Servo.h>
// #include <RCSwitch.h>
// #include <avr/iom16u2.h>
// #include <avr/io.h>
// #  include <avr/iom16u2.h>
#include "pin_map.h"
#include "test.h"
#include <SPI.h>
#include <SoftwareSerial.h>


// TODO: rename to TFT_ST7735_MINI.h
// #include <TFT_ST7735.h> // Graphics and font library for ST7735 driver chip

#include "HID-Project.h"


/*
#define CS D0
#define DC D1
#define RESET D2
*/

#define CS 42
#define DC 43
#define RESET 44

#define PACKET_LEN 5
uint8_t rawhidData[PACKET_LEN + 2];
uint8_t myBuff[PACKET_LEN + 1];

SoftwareSerial mySerial(D0, D1); // RX, TX

// TFT_ST7735 tft = TFT_ST7735();

void setup(void) {
    // tft.init();
    // tft.setRotation(3);
    RawHID.begin(rawhidData, sizeof(rawhidData));
    // test();
    //
    mySerial.begin(4800);
    myBuff[PACKET_LEN] = '\0';
    mySerial.println("setup done");
    RawHID.write("test\n");
}

void test() {
  // Fill screen with grey so we can see the effect of printing with and without 
  // a background colour defined
  // tft.drawColorImage(close,0,0, closeWidth, closeHeight);

    // Serial.print(RawHID.readString());
    // Serial.flush();
    //
    auto bytesAvailable = RawHID.available();
    if(bytesAvailable == 0){
        return;
    }

    for(int i = 0; i < bytesAvailable; i++){
        RawHID.write(RawHID.read());
    }
    return;

    /*
    // Write data to led array
    uint8_t* ptr = (uint8_t*)leds;
    for (int i = 0; i < sizeof(leds); i++) {
      *ptr = RawHID.read();
      ptr++;
    }
    */
}
void loop(){test();}

/*
void setup() {
    // initialize the myScreen
    myScreen.init();
    // myScreen.initR(INITR_BLACKTAB);
    myScreen.setRotation(3);
    myScreen.setCursor(0,0);

    // make the background white
    myScreen.background(0,0,255);
    //myScreen.text("test123", 5, 5);

  // write the static text to the screen
  // set the font color to white
  myScreen.stroke(255, 255, 255);
  // set the font size
  myScreen.setTextSize(2);
  // write the text to the top left corner of the screen
  myScreen.text("Sensor Value :\n ", 0, 0);
  // set the font size very large for the loop
  // myScreen.setTextSize(5);
}

void loop() {
}
*/

/*
#include <LiquidCrystal_SoftI2C.h>

#define LCD_WIDTH 20
#define LCD_LINES 4
#define LCD_ADDR 0x27

SoftwareWire myWire(0,1);
static LiquidCrystal_I2C lcd(LCD_ADDR,LCD_WIDTH, LCD_LINES, &myWire);

void setup_lcd(){
    for(int i = 13; i < 13+8; i++){
        pinMode(i, INPUT_PULLUP);
    }
    lcd.begin();
    lcd.setBacklight(1);
    lcd.setCursor(0,0);
}

void setup() {
    setup_lcd();
    lcd.clear();
    // lcd.print("hi 123");
}

void loop() {
    delay(1000);

    for(int i = 13; i < 13+8; i++){
        lcd.setCursor(i-13,1);
        lcd.write(digitalRead(i) ? '1' : '0');
    }

}
*/
