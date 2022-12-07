#!/bin/sh
# create systemd service
PROGRAM="smart-home-server"
# user service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
BIN_LOCATION="/usr/local/bin/$PROGRAM"

systemctl --user unmask $PROGRAM
systemctl --user stop $PROGRAM
systemctl --user disable $PROGRAM

sudo rm $SERVICE_FILE
sudo rm $BIN_LOCATION

#rm symlink
rm "$HOME/.config/systemd/user/multi-user.target.wants/smart-home-server.service"

sudo systemctl daemon-reload
