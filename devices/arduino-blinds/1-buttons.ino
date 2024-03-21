#define BUTTON_INT_PIN 3
#define UP_PIN 5
#define DOWN_PIN 6

#define DEBOUNCE_TIME 200

static int _pushed = PUSHED_NONE;
int get_button_pushed(){
    int x = _pushed;
    _pushed = PUSHED_NONE;
    if(x!=PUSHED_NONE){
    }

    return x;
}

static unsigned long prev_inter_time = 0;
void inter(){
  unsigned long now = millis();
  if (now - prev_inter_time < DEBOUNCE_TIME){
      return;
  }
  prev_inter_time  = now;

  int up   = !digitalRead(UP_PIN);
  int down = !digitalRead(DOWN_PIN);

  // sanity check
  if( (up && down) || (!up && !down) ){return;}

  // use buttons
  if (up){
      _pushed = PUSHED_UP;
      return;
  }
  _pushed = PUSHED_DOWN;
}

void setup_buttons(){
    pinMode(BUTTON_INT_PIN, INPUT_PULLUP);
    pinMode(UP_PIN, INPUT_PULLUP);
    pinMode(DOWN_PIN, INPUT_PULLUP);
    
    attachInterrupt(digitalPinToInterrupt(BUTTON_INT_PIN), inter, FALLING);
}
