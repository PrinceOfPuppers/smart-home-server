#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#include <ESP8266WiFi.h>

#include "network-info.h"

#define SERIAL_BAUD 115200

// #define DEBUG_ENABLED

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
// TCP stuff //
///////////////

#define SERVER_IP "192.168.2.23"
const String server_ip = SERVER_IP;
static String localIP;
#define PORT 6832

WiFiClient client;

// does not include delimiter \0, extra LCD_LINES if for newlines
#define MAX_PACKET_LEN LCD_WIDTH*LCD_LINES + LCD_LINES

char incomingPacket[MAX_PACKET_LEN + 1];

void send_packet_tcp(String s){
    client.print(s);
    client.write('\0');
}

String get_packet_tcp(){
    size_t len = 0;
    char x;
    while(1){
        if(len >= MAX_PACKET_LEN){
            break;
        }

        // wait for rest of packet data
        if(!client.available()){
            delay(1);
            continue;
        }

        x = client.read();
        if(x == '\0'){
            break;
        }

        incomingPacket[len] = x;
        len++;
    }
    incomingPacket[len] = '\0';
    return String(incomingPacket);
}

void setup_tcp(){
    WiFi.begin(NETWORK_NAME, NETWORK_PASS);

    write_lcd("Connecting Wifi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }

    localIP = WiFi.localIP().toString();
}

// blocks until connection is established
void connect_server(uint8_t lcdNum){
    long attempt = 0;
    String lcdNumStr = String(lcdNum);

    while(1){
        write_lcd("Conn Attempt: " + String(attempt) + "\nL: " + localIP + "\nR: " + SERVER_IP "\nLCD Num: " + lcdNumStr);
        if(client.connect(server_ip, PORT)){
            break;
        }
        
        attempt++;
        delay(3000);
    }
    write_lcd("Connected!");

    send_packet_tcp(lcdNumStr);
}

// blocks until connection is lost
void listen_for_updates(){

    while(client.connected()){
        if(client.available()){
            write_lcd(get_packet_tcp());
        }
        delay(1);
    }

    client.stop();

    write_lcd("Server Lost!");
    delay(5000);
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
    setup_tcp();
    getLCDNum();
}

void loop(){
    connect_server(lcdNum);
    listen_for_updates();
}


