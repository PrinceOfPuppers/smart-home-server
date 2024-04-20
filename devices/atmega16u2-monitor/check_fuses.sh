avrdude -v -p atmega16u2 -c "arduino_as_isp" -P /dev/ttyUSB0 -U hfuse:r:-:h -U lfuse:r:-:h -U efuse:r:-:h
