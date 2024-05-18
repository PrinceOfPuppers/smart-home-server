#!/bin/sh

#TODO create symlink for 10-smart-home-server.rules
#TODO: reload usb hid driver
# sudo udevadm control --reload-rules

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
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl enable systemd-time-wait-sync
sudo systemctl start systemd-time-wait-sync
pip3 install -e .

# create update script
UPDATE_PROGRAM="smart-home-update"

echo "#!/bin/sh" > "./$UPDATE_PROGRAM"
echo "git -C $PWD pull" | sudo tee -a "./$UPDATE_PROGRAM"
sudo chmod +x "./$UPDATE_PROGRAM"

# create systemd service
PROGRAM="smart-home-server"
# user service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
BIN_LOCATION="/usr/local/bin/$PROGRAM"
UPDATE_BIN_LOCATION="/usr/local/bin/$UPDATE_PROGRAM"

#TODO replace with symlinks
sudo chmod +x "bin/$PROGRAM"
sudo cp "bin/$PROGRAM" $BIN_LOCATION
sudo mv "./$UPDATE_PROGRAM" $UPDATE_BIN_LOCATION

sudo cp $PROGRAM.service $SERVICE_FILE
sudo chmod 644 $SERVICE_FILE

sudo systemctl daemon-reload
systemctl --user daemon-reload
systemctl --user enable $PROGRAM
systemctl --user start $PROGRAM


#TODO: add raspi-config overlay filesystem and restart

