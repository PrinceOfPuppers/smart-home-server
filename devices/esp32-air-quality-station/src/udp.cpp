#include "udp.h"
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// just for type
#include "PMS.h"
#include "bme680_type.h"

#include "network-info.h"
#include "general.h"

///////////////
// UDP stuff //
///////////////
WiFiUDP udp;
unsigned int localudpPort = 6833;
char incomingPacket[256];
char replyPacket[256];

//WiFiEventHandler wifi_disconnect_handler;

void wifi_disconnect_cb(WiFiEvent_t event, WiFiEventInfo_t info) {
    ESP.restart();
}

void setup_udp(){
    debugln(">>> Setting Up WiFi <<<");
    WiFi.hostname(HOST_NAME);
    WiFi.onEvent(wifi_disconnect_cb, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
    WiFi.begin(NETWORK_NAME, NETWORK_PASS);

    debug("Connecting to ");
    debug(NETWORK_NAME);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        debug(".");
    }
    debugln("");
    debug("Connected, IP address: ");
    debugln(WiFi.localIP());

    udp.begin(localudpPort);
}


void await_udp_transmitt(void (* delay_func)(uint32_t), uint32_t duration, BMEData *bmeData, PMS::DATA *pmsData, uint16_t *s8Data){
    debugln("Awaiting UDP...");
    uint32_t counter = 0;

    while(1){
        delay_func(1);
        counter += 1;
        if(counter > duration){
            break;
        }

        int packetSize = udp.parsePacket();
        if(!packetSize){
            continue;
        }

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

        // create packet
        int reply_len = snprintf(replyPacket, sizeof(replyPacket), "%f,%f,%f,%f,%f,%f,%u,%u,%u,%u",
                // bme floats (*C, RH%, Pa, iaq, ppm, ppm)
                bmeData->temperature, bmeData->humidity, bmeData->pressure, bmeData->iaq, bmeData->co2Equivalent, bmeData->breathVocEquivalent,
                // pms uint16_ts (micro g /m^3)
                pmsData->PM_AE_UG_1_0, pmsData->PM_AE_UG_2_5, pmsData->PM_AE_UG_10_0,
                // s8 uint16_t (ppm)
                *s8Data
                );

        if(reply_len < 0){
            debugln("snprintf Failed, replyPacket too small");
            continue;
        }

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write((uint8_t *)replyPacket,reply_len);
        udp.endPacket();
        continue;
    }
}
