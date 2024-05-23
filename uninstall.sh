#!/bin/sh

echo "Ensure Overlay Filesystem is Disabled!"

# remove fstab mount (marked with comment smart-home-server)
# TODO: create similar system that deletes line with mark and the line beneath it
# sudo sed -i '/smart-home-server/d' /etc/fstab

# create systemd service
PROGRAM="smart-home-server"
UPDATER="smart-home-update"
# user service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
BIN_LOCATION="/usr/local/bin/$PROGRAM"
UPDATE_BIN_LOCATION="/usr/local/bin/$UPDATER"

systemctl --user unmask $PROGRAM
systemctl --user stop $PROGRAM
systemctl --user disable $PROGRAM

sudo rm $SERVICE_FILE
sudo rm $BIN_LOCATION
sudo rm $UPDATE_BIN_LOCATION

#rm symlink
rm "$HOME/.config/systemd/user/multi-user.target.wants/$PROGRAM.service"

UDEV_RULE="10-atmega16u2.rules"
UDEV_RULE_LOCATION="/etc/udev/rules.d/$UDEV_RULE"
sudo rm $UDEV_RULE_LOCATION
sudo udevadm control --reload-rules

sudo systemctl daemon-reload
