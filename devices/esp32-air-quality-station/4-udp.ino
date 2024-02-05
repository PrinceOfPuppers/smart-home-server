#include <WiFi.h>
#include <WiFiUdp.h>
#include "network-info.h"

///////////////
// UDP stuff //
///////////////
WiFiUDP udp;
unsigned int localudpPort = 6833;
char incomingPacket[256];
char replyPacket[256];

//WiFiEventHandler wifi_disconnect_handler;

#define HOST_NAME "esp32-air-quality-station"

void wifi_disconnect_cb(WiFiEvent_t event, WiFiEventInfo_t info) {
    ESP.restart();
}

void setup_udp(){
    WiFi.hostname(HOST_NAME);
    WiFi.onEvent(wifi_disconnect_cb, WiFiEvent_t::ARDUINO_EVENT_WIFI_STA_DISCONNECTED);
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

void await_udp_transmitt(uint32_t duration){
    uint32_t counter = 0;

    while(1){
        delay(1);
        counter += 1;
        if(counter > duration){
            break;
        }

        int packetSize = udp.parsePacket();
        if(!packetSize){
            continue;
        }

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
        /* TODO: replace with proper transmission
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
        */
        continue;
    }
}
