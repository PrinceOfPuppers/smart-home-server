#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#include <ESP8266WiFi.h>

#include "network-info.h"

#define WATCHDOG_INTERVAL 5000

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

static bool _lcd_backlight_on = false;
void lcd_set_backlight(bool on){
   lcd.setBacklight(on);
   _lcd_backlight_on = on;
}

void lcd_toggle_backlight(){
   _lcd_backlight_on = !_lcd_backlight_on;
   lcd.setBacklight(_lcd_backlight_on);
}

void setup_lcd(){
    lcd.init();
    lcd_set_backlight(1);
    lcd.setCursor(0,0);
    feed_watchdog();
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
    feed_watchdog();
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
#define KEEPALIVE_IDLE_SEC          10*60
#define KEEPALIVE_INTERVAL_SEC      10
#define KEEPALIVE_COUNT             5


// does not include delimiter \0, extra LCD_LINES if for newlines
#define MAX_PACKET_LEN LCD_WIDTH*LCD_LINES + LCD_LINES

char incomingPacket[MAX_PACKET_LEN + 1];

WiFiEventHandler wifi_disconnect_handler;

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

void wifi_disconnect_cb(const WiFiEventStationModeDisconnected& event) {
    ESP.restart();
}

void setup_tcp(){
    wifi_disconnect_handler = WiFi.onStationModeDisconnected(wifi_disconnect_cb);

    WiFi.begin(NETWORK_NAME, NETWORK_PASS);

    write_lcd("Connecting Wifi...");
    while (WiFi.status() != WL_CONNECTED) {
        feed_watchdog();
        delay(500);
    }

    localIP = WiFi.localIP().toString();
}


// blocks until connection is established
void connect_server(uint8_t lcdNum){
    long attempt = 0;
    String lcdNumStr = String(lcdNum);

    while(1){
        feed_watchdog();
        write_lcd("Conn Attempt: " + String(attempt) + "\nL: " + localIP + "\nR: " + SERVER_IP "\nLCD Num: " + lcdNumStr);
        if(client.connect(server_ip, PORT)){
            break;
        }
        
        attempt++;
        delay(3000);
    }
    write_lcd("Connected!");

    client.keepAlive(KEEPALIVE_IDLE_SEC, KEEPALIVE_INTERVAL_SEC, KEEPALIVE_COUNT);

    feed_watchdog();
    send_packet_tcp(lcdNumStr);
}

#define CMD_ESC_CHAR 0x1b
#define SET_BACKLIGHT_CHAR 'l'

void lcd_cmd(String s){
    size_t len = s.length();
    if(len < 3 || s[0] != CMD_ESC_CHAR){
        write_lcd(s);
        return;
    }

    // len is 3 or more
    switch(s[1]){
        case SET_BACKLIGHT_CHAR:
        {
            if(s[2] == 't'){
                lcd_toggle_backlight();
                break;
            }
            lcd_set_backlight(s[2] == '1');
            break;
        }

    }

}

// blocks until connection is lost
void listen_for_updates(){

    while(client.connected()){
        feed_watchdog();
        if(client.available()){
            lcd_cmd(get_packet_tcp());
        }
        delay(1);
    }

    client.stop();

    write_lcd("Server Lost!");
    feed_watchdog();
    delay(3000);
}


////////////////
// setup/loop //
////////////////
void setup(){
#ifdef DEBUG_ENABLED
    Serial.begin(SERIAL_BAUD);
    while(!Serial) {}
#endif
    setup_watchdog(WATCHDOG_INTERVAL);
    setup_lcd();
    setup_tcp();
    getLCDNum();
}

void loop(){
    connect_server(lcdNum);
    listen_for_updates();
    feed_watchdog();
}


