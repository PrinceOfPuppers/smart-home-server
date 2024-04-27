#include "pin_map.h"
#include "buttons.h"
#include <stdint.h>
#include <Arduino.h>

#define NEXT_PIN D3
#define PREV_PIN D4

#define DEBOUNCE_TIME 200

static uint8_t _pushed = false;

int get_button_pushed(){
    int x = _pushed;
    _pushed = PUSHED_NONE;
    return x;
}


static unsigned long prev_inter_time = 0;

// return true if bounce
bool debounce(){
  unsigned long now = millis();
  if (now - prev_inter_time < DEBOUNCE_TIME){
      return true;
  }
  prev_inter_time  = now;

}

void next_inter(){
    if(debounce()){
        return;
    }
    _pushed = PUSHED_NEXT;
}

void prev_inter(){
    if(debounce()){
        return;
    }
    _pushed = PUSHED_PREV;
}

void setup_buttons(){
    pinMode(NEXT_PIN, INPUT_PULLUP);
    pinMode(PREV_PIN, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(NEXT_PIN), next_inter, FALLING);
    attachInterrupt(digitalPinToInterrupt(PREV_PIN), prev_inter, FALLING);
}

