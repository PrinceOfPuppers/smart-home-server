#!/bin/bash

# get directory of this script
pushd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
popd

sudo cp -R -u -p $SCRIPT_DIR/../../10-atmega16u2.rules /etc/udev/rules.d/10-atmega16u2.rules
sudo udevadm control --reload-rules
