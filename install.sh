#!/bin/bash

basePath="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
basePath="${basePath%/}"
mountPath="$basePath/smart_home_server/storage"

mkdir -p $mountPath
echo "Mount Path: $mountPath"

if ! grep -Fq "$mountPath" /etc/fstab
then
    readarray -t uuids < <(basename -a /dev/disk/by-uuid/*)

    valid_array=()

    echo "Pick a USB Device to Mount:"
    for uuid in "${uuids[@]}"; do
        part=$(readlink -f "/dev/disk/by-uuid/$uuid")
        [[ -b "$part" ]] || continue

        disk_name=$(lsblk -no PKNAME "$part" 2>/dev/null) || continue
        disk="/dev/$disk_name"
        [[ -b "$disk" ]] || continue

        # USB devices only
        [[ "$(lsblk -no TRAN "$disk" 2>/dev/null)" == "usb" ]] || continue

        size=$(lsblk -no SIZE "$part" 2>/dev/null)
        label=$(lsblk -no LABEL "$part" 2>/dev/null)
        model=$(lsblk -no MODEL "$disk" 2>/dev/null)

        valid_array+=("$uuid")
        line="${#valid_array[@]}) $part"

        [[ -n "$model" ]] && line+=" Model:$model"
        [[ -n "$label" ]] && line+=" Label:$label"

        line+=" ($size)"

        echo "$line"
    done
    if [ ${#valid_array[@]} -eq 0 ]; then
        echo "No USB devices detected."
        exit 1
    fi

    read input
    re='^[0-9]+$'

    if ! [[ $input =~ $re ]] ; 
    then
      echo "Invalid Input: ${input}"
      exit 1
    fi

    if (( input > ${#valid_array[@]} || input < 1 )); then
      echo "input: ${input} not within range given"
      exit 1
    fi

    chosen_uuid=${valid_array[input-1]}

    echo "Chosen UUID: $chosen_uuid"

    OWNER_USER="${SUDO_USER:-$(id -un)}"
    OWNER_GROUP="$(id -gn "$OWNER_USER")"

    echo "FSTAB entry:"
    echo "UUID=$chosen_uuid       $mountPath   auto   rw,nofail,noatime 0 2 # smart-home-server" | sudo tee -a /etc/fstab
    sudo systemctl daemon-reload
    sudo mount -a
    sudo chown -R "$OWNER_USER:$OWNER_GROUP" $mountPath
    sudo chmod 755 $mountPath
fi

# usb mounting over
set -x;

pathappend() {
  for ARG in "$@"
  do
    if [ -d "$ARG" ] && [[ ":$PATH:" != *":$ARG:"* ]]; then
        PATH="${PATH:+"$PATH:"}$ARG"
    fi
  done
}
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get -y install git

pathappend "$HOME/.local/bin"
source "$HOME/.profile"
sudo raspi-config nonint do_i2c 0
sudo loginctl enable-linger $(id -u)
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-rpi.gpio
sudo apt-get -y install libhidapi-hidraw0
sudo systemctl enable systemd-time-wait-sync
sudo systemctl start systemd-time-wait-sync
python3 -m venv venv --system-site-packages
source ./venv/bin/activate
pip3 install -e .

# create bin for systemd to execute
PROGRAM="smart-home-server"
echo "#!/bin/sh" > "./$PROGRAM"
echo "$basePath/venv/bin/python3 $basePath/bin/smart-home-server" >> "./$PROGRAM"
sudo chmod +x "./$PROGRAM"

# create update script
UPDATE_PROGRAM="smart-home-update"
echo "#!/bin/sh" > "./$UPDATE_PROGRAM"
echo "git -C $basePath pull" >> "./$UPDATE_PROGRAM"
sudo chmod +x "./$UPDATE_PROGRAM"

mkdir -p "$HOME/.local/bin"
BIN_LOCATION="$HOME/.local/bin/$PROGRAM"
UPDATE_BIN_LOCATION="$HOME/.local/bin/$UPDATE_PROGRAM"

#TODO replace with symlinks
sudo mv "./$PROGRAM" $BIN_LOCATION
sudo mv "./$UPDATE_PROGRAM" $UPDATE_BIN_LOCATION

# create systemd userspace service
SERVICE_FILE="/usr/lib/systemd/user/$PROGRAM.service"
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

# allow sd card writes to finish
sync
sleep 1
# enable overlay filesystem and reboot
sudo raspi-config nonint enable_overlayfs
sudo reboot
