#!/bin/sh
tty='/dev/ttyUSB0'
arduino-cli compile --fqbn "arduino:avr:nano" -u -p $tty
cat $tty
