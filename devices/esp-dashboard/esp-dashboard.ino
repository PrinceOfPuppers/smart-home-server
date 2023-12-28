#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "network-info.h"

#define SERIAL_BAUD 115200

#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print(msg)
#define debugln(msg) Serial.println(msg)
#else
#define debug(msg) 
#define debugln(msg) 
#endif

///////////////
// LCD stuff //
///////////////

#define LCD_WIDTH 20
#define LCD_LINES 4
#define LCD_ADDR 0x27

static LiquidCrystal_I2C lcd(LCD_ADDR,LCD_WIDTH, LCD_LINES);

void setup_lcd(){
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
}

void write_lcd(const String &s){
    debugln("LCD Write:");
    debugln(s);
    lcd.clear();

    size_t len = s.length();

    size_t start = 0;
    for(uint8_t l = 0; l < LCD_LINES; l++){
        int nIndex = s.indexOf('\n', start);

        // check for no newline
        size_t end = nIndex < 0 ? len : nIndex;

        lcd.setCursor(0,l);

        lcd.print(s.substring(start, end - start > LCD_WIDTH ? LCD_WIDTH+start : end));

        start = end + 1; // set start to character past newline
        if (nIndex < 0){
            break;
        }
    }
}

static uint8_t lcdNum = 0;
#define LCD_NUM_PIN_1 14 //D5
#define LCD_NUM_PIN_2 12 //D6
#define LCD_NUM_PIN_3 13 //D7

void getLCDNum(){
    pinMode(LCD_NUM_PIN_1, INPUT_PULLUP);
    pinMode(LCD_NUM_PIN_2, INPUT_PULLUP);
    pinMode(LCD_NUM_PIN_3, INPUT_PULLUP);

    lcdNum = 0;
    lcdNum |= (!digitalRead(LCD_NUM_PIN_1)) << 0;
    lcdNum |= (!digitalRead(LCD_NUM_PIN_2)) << 1;
    lcdNum |= (!digitalRead(LCD_NUM_PIN_3)) << 2;
    // lcd num 0 is one attached to server
    lcdNum+=1;

    write_lcd("LCD Number: " + String(lcdNum));
    delay(1000);

    // disable pullups
    pinMode(LCD_NUM_PIN_1, INPUT);
    pinMode(LCD_NUM_PIN_2, INPUT);
    pinMode(LCD_NUM_PIN_3, INPUT);
}


///////////////
// UDP stuff //
///////////////
WiFiUDP udp;
unsigned int localudpPort = 6832;
unsigned int remoteudpPort = 6832;
char incomingPacket[LCD_WIDTH*LCD_LINES + 1];
char replyPacket[256];

#define SERVER_IP "192.168.2.16"
const String server_ip = SERVER_IP;

#define SERVER_RETRY_TIME_MS 5000

// will wait this times the expected update interval before reconnecting
#define SERVER_RECONNECT_TIME_FACTOR_MS 3

void ack(){
    udp.beginPacket(SERVER_IP, remoteudpPort);
    udp.write("A", 1);
    udp.endPacket();
}

static String localIP;
void setup_udp(){
    WiFi.begin(NETWORK_NAME, NETWORK_PASS);

    write_lcd("Connecting Wifi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    localIP = WiFi.localIP().toString();
    write_lcd("WiFi Up!\nIP: " + localIP);
    udp.begin(localudpPort);
    delay(1000);
}

// blocking, returns expected return interval
// (how frequently serer ought to return info)
long subscribe_lcd(uint8_t lcdNum){
    size_t attempt = 1;
    String lcdNumStr = String(lcdNum);


    while(1){
        write_lcd("Conn Attempt: " + String(attempt) + "\nL: " + localIP + "\nR: " + SERVER_IP "\nLCD Num: " + lcdNumStr);
        udp.beginPacket(SERVER_IP, remoteudpPort);
        udp.write(lcdNumStr.c_str(), lcdNumStr.length());
        udp.endPacket();

        attempt++;

        for(int i = 0; i < SERVER_RETRY_TIME_MS; i++){
            int packetSize = udp.parsePacket();
            if(!packetSize){
                delay(1);
                continue;
            }

            // response received
            write_lcd("Connected!");

            int len = udp.read(incomingPacket, LCD_WIDTH*LCD_LINES);
            if(len < 0){
                write_lcd("Response\nToo Large!");
                delay(5000);
                break;
            }

            incomingPacket[len] = '\0';
            String d = String(incomingPacket);
            long interval = d.toInt();
            if(interval == 0){
                write_lcd("Invalid Update\nInterval!");
                delay(5000);
                break;
            }

            ack();

            return interval;
        }
    }
}

bool get_lcd_update(long interval){
    for(int i = 0; i < interval*SERVER_RECONNECT_TIME_FACTOR_MS; i++){
        int packetSize = udp.parsePacket();
        if(!packetSize){
            delay(1);
            continue;
        }

        if(udp.remoteIP().toString() != server_ip){
            write_lcd("Recieved Data\nFrom Unknown IP");
            delay(1);
            continue;
        }

        int len = udp.read(incomingPacket, LCD_WIDTH*LCD_LINES);
        if(len < 0){
            write_lcd("Response\nToo Large!");
            delay(5000);
            break;
        }

        incomingPacket[len] = '\0';
        String d = String(incomingPacket);
        write_lcd(d);

        ack();
        return true;
    }
    write_lcd("Server Lost!");
    delay(5000);

    return false;
}


////////////////
// setup/loop //
////////////////
void setup(){
#ifdef DEBUG_ENABLED
    Serial.begin(SERIAL_BAUD);
    while(!Serial) {}
#endif
    setup_lcd();
    setup_udp();
    getLCDNum();
}

void loop(){
    long interval = subscribe_lcd(lcdNum);
    while(get_lcd_update(interval)){
    }
}


