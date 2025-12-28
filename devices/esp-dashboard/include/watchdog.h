#ifndef WATCHDOG_H_
#define WATCHDOG_H_

void feed_watchdog();

bool setup_watchdog(long wdt_interval);

#endif
