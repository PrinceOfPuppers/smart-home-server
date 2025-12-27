#!/bin/sh

mountPath=$(cd "$(dirname "$1")"; pwd)/$(basename "$1")smart_home_server/storage
mkdir -p $mountPath
echo "Mount Path: $mountPath"

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
    sudo systemctl daemon-reload
    sudo mount -a
    #sudo mount $mountPath
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
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git

pathappend "$HOME/.local/bin"
source "$HOME/.profile"
sudo raspi-config nonint do_i2c 0
sudo loginctl enable-linger $(id -u)
sudo apt-get update
sudo apt-get install pigpio
sudo apt install python3-pip
sudo apt install libhidapi-hidraw0
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl enable systemd-time-wait-sync
sudo systemctl start systemd-time-wait-sync
python3 -m venv venv
source ./venv/bin/activate
pip3 install -e .

# create bin

PROGRAM="smart-home-server"
echo "#!$(which python3) -u" > "./$PROGRAM"
echo "if __name__ == \"__main__\":" >> "./$PROGRAM"
echo "    from smart_home_server import main" >> "./$PROGRAM"
echo "    main()" >> "./$PROGRAM"
sudo chmod +x "./$PROGRAM"

# create update script
UPDATE_PROGRAM="smart-home-update"

echo "#!/bin/sh" > "./$UPDATE_PROGRAM"
echo "git -C $PWD pull" | sudo tee -a "./$UPDATE_PROGRAM"
sudo chmod +x "./$UPDATE_PROGRAM"

# create systemd service
# user service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
BIN_LOCATION="/usr/local/bin/$PROGRAM"
UPDATE_BIN_LOCATION="/usr/local/bin/$UPDATE_PROGRAM"

#TODO replace with symlinks
sudo mv "./$PROGRAM" $BIN_LOCATION
sudo mv "./$UPDATE_PROGRAM" $UPDATE_BIN_LOCATION

sudo cp $PROGRAM.service $SERVICE_FILE
sudo chmod 644 $SERVICE_FILE

sudo systemctl daemon-reload
systemctl --user daemon-reload
systemctl --user enable $PROGRAM
systemctl --user start $PROGRAM

#create udev rules
UDEV_RULE="10-atmega16u2.rules"
UDEV_RULE_LOCATION="/etc/udev/rules.d/$UDEV_RULE"
sudo cp $UDEV_RULE $UDEV_RULE_LOCATION
sudo udevadm control --reload-rules

# enable overlay filesystem and reboot
sudo raspi-config nonint enable_overlayfs
sudo reboot
