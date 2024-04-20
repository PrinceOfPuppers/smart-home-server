avrdude -v -p atmega16u2 -c "arduino_as_isp" -P /dev/ttyUSB0 -U efuse:w:0xF4:m -U hfuse:w:0xD9:m -U lfuse:w:0xFF:m
