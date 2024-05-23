#!/bin/sh
tty='/dev/ttyUSB0'
stty -F $tty 9600
arduino-cli compile --fqbn "arduino:avr:nano" -u -p $tty
cat $tty
