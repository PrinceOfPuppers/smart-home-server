#!/bin/sh

mountPath=$(cd "$(dirname "$1")"; pwd)/$(basename "$1")smart_home_server/storage

if ! grep -Fq "$mountPath" /etc/fstab
then
    usbDevsStr=$(find /dev/disk/by-uuid -maxdepth 1 -type l -ls | sed 's/.*by-uuid\///' | sed 's/\.\.\/\.\.\///')
    readarray -t usbDevs <<<"$usbDevsStr"

    echo "Pick a USB Device to Mount:"

    for i in "${!usbDevs[@]}"; do
        echo "$(( $i + 1 ))) ${usbDevs[i]}"
    done

    read input
    re='^[0-9]+$'

    if ! [[ $input =~ $re ]] ; 
    then
      echo "Invalid Input: ${input}"
      exit 1
    fi

    # now we mount selected UUID
    dev=$(echo ${usbDevs[input-1]} | sed 's/\s->.*//')
    ftype=$(sudo blkid | grep "$dev" | sed 's/.*\sTYPE="//' | sed 's/"\s.*//')

    echo $dev
    echo $ftype

    echo "UUID=$dev       $mountPath   $ftype  rw,user,exec,umask=000 0 1" | sudo tee -a /etc/fstab
    sudo mount $mountPath
fi

# usb mounting over

pathappend() {
  for ARG in "$@"
  do
    if [ -d "$ARG" ] && [[ ":$PATH:" != *":$ARG:"* ]]; then
        PATH="${PATH:+"$PATH:"}$ARG"
    fi
  done
}
sudo apt-get install git

# on startup update project
gitPull="git -C $PWD pull"
if ! grep -Fq "$gitPull" /etc/rc.local
    echo "$gitPull" | sudo tee -a /etc/rc.local
fi

pathappend "$HOME/.local/bin"
source "$HOME/.profile"
sudo raspi-config nonint do_i2c 0
sudo loginctl enable-linger $(id -u)
sudo apt-get update
sudo apt-get install pigpio
sudo apt install python3-pip
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
pip3 install -e .

# create systemd service
PROGRAM="smart-home-server"
# user service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
BIN_LOCATION="/usr/local/bin/$PROGRAM"

sudo chmod +x "bin/$PROGRAM"
sudo cp "bin/$PROGRAM" $BIN_LOCATION

sudo cp $PROGRAM.service $SERVICE_FILE
sudo chmod 644 $SERVICE_FILE

sudo systemctl daemon-reload
systemctl --user daemon-reload
systemctl --user enable $PROGRAM
systemctl --user start $PROGRAM

