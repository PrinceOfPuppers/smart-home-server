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

pathappend "$HOME/.local/bin"
source "$HOME/.profile"

sudo apt-get update
sudo apt-get install pigpio
sudo apt install python3-pip
sudo systemctl enable pigpiod
pip3 install -e .
