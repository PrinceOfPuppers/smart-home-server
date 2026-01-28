#ifndef RFMOD_RF_WRAPPERS_H_
#define RFMOD_RF_WRAPPERS_H_

void setupRf();
void handleRx();
void txTransmit(int protocol, unsigned long code, unsigned int bit_length, int pulse_length, int num_repeats);

#endif
