#ifndef RFMOD_UART_BUFF_H_
#define RFMOD_UART_BUFF_H_

#include <errno.h>

void buff_reset();
int buff_push_char(char c);
char *buff_strtok(const char *delim);

#define next_token(t, e) \
errno = 0; \
e = NULL; \
if( !(t = buff_strtok(",")) ){ \
    buff_reset(); \
    return; \
}

#define strtoul_err_check(t, e) \
if (t == e || errno != 0 || e == NULL || *e != '\0') { \
    buff_reset(); \
    return; \
} 

#endif
