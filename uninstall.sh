#!/bin/sh
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

#TODO: remove udev rule

sudo systemctl daemon-reload
