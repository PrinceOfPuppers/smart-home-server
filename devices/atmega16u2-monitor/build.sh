pushd firmware
arduino-cli compile --fqbn "HoodLoader2:avr:HoodLoader2atmega16u2" -u --programmer "arduinoasisp" -p /dev/ttyUSB0
cd ..
