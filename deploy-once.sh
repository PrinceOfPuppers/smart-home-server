#!/bin/sh

mountPath=$(cd "$(dirname "$1")"; pwd)/$(basename "$1")smart_home_server/storage
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

if ! grep -Fxq "$mountPath" /etc/fstab
then
    echo "UUID=$dev       $mountPath   $ftype  defaults          0    1" >> /etc/fstab
fi

sudo mount $mountPath

# usb mounting over

sudo systemctl enable pigpiod
pip3 install -e .

hupper -m smart-home-server
