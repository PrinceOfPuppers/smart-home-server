#include <BME280I2C.h>
#include <Wire.h>

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "network-info.h"

#define SERIAL_BAUD 115200

//#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
#define debug(msg) Serial.print(msg)
#define debugln(msg) Serial.println(msg)
#else
#define debug(msg) 
#define debugln(msg) 
#endif

///////////////
// BME stuff //
///////////////
BME280I2C::Settings settings(
   BME280::OSR_X1,
   BME280::OSR_X1,
   BME280::OSR_X1,
   BME280::Mode_Forced,
   BME280::StandbyTime_1000ms,
   BME280::Filter_Off,
   BME280::SpiEnable_False,
   BME280I2C::I2CAddr_0x76
);


BME280I2C bme(settings);

struct BMEData{
    float temp;
    float humid;
    float pressure;
};

void get_bme_data( struct BMEData *out ){
    bme.read(out->pressure, out->temp, out->humid, BME280::TempUnit_Celsius, BME280::PresUnit_Pa);
}


void setup_bme(){
    Wire.begin();

    while(!bme.begin())
    {
        debug("Could not find BME280 sensor!");
        delay(1000);
    }

    // first sample is often inaccurate
    BMEData inital_sample;
    get_bme_data(&inital_sample);
}

void print_bme(struct BMEData *data){
    debug("Temp: ");
    debug(data->temp);
    debug("°C");
    debug("\t\tHumidity: ");
    debug(data->humid);
    debug("% RH");
    debug("\t\tPressure: ");
    debug(data->pressure);
    debug("Pa");
}


///////////////
// UDP stuff //
///////////////
WiFiUDP udp;
unsigned int localudpPort = 6831;
char incomingPacket[256];
char replyPacket[256];

#define HOST_NAME "esp-weather-station"

void setup_udp(){
    WiFi.hostname(HOST_NAME);
    WiFi.begin(NETWORK_NAME, NETWORK_PASS);

    debug("Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        debug(".");
    }
    debugln("");
    debug("Connected, IP address: ");
    debugln(WiFi.localIP());

    udp.begin(localudpPort);
}

void await_udp_transmitt(){
    size_t counter = 0;

    while(1){
        delay(1);
        counter += 1;
        int packetSize = udp.parsePacket();
        if(!packetSize){

            // make a call every minute to keep sample fresh
            if(counter > 1000*58){
                BMEData data;
                get_bme_data(&data);
#ifdef DEBUG_ENABLED
                debugln("Warming bme:");
                print_bme(&data);
#endif
                counter = 0;
            }

            continue;
        }

        counter = 0;

#ifdef DEBUG_ENABLED
        debug("Received: ");
        debug(packetSize);
        debug(" bytes from: ");
        debug(udp.remoteIP().toString().c_str());
        debug(" , port: ");
        debugln(udp.remotePort());
        
        int len = udp.read(incomingPacket, 255);
        if(len > 0){
            incomingPacket[len] = '\0';
        }
        debug("UDP packet contents: ");
        debugln(incomingPacket);
#endif
        BMEData data;
        get_bme_data(&data);
        int reply_len = snprintf(replyPacket, sizeof(replyPacket), "%f,%f,%f", data.temp, data.humid, data.pressure);
        if(reply_len < 0){
            debugln("snprintf Failed, replyPacket too small");
            continue;
        }

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write(replyPacket,reply_len);
        udp.endPacket();
        break;
    }
}

////////////////
// setup/loop //
////////////////
void setup(){
#ifdef DEBUG_ENABLED
    Serial.begin(SERIAL_BAUD);
    while(!Serial) {}
#endif
    setup_bme();
    setup_udp();
}

void loop(){
    await_udp_transmitt();
}


