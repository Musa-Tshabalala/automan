#!/bin/bash

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

PSQL="psql -U $DBUSER -d $DBNAME --no-align -t -c"

echo -e "~~ Syncing device server ~~\n"
echo Please enter your name.

read NAME

until [[ $NAME =~ [A-Za-z] ]]; do
    clear
    echo Please enter a valid name.
    sleep 1
    read NAME
done

clear
sleep 1

ALL_DEVICES=('Phone' 'PC' 'VPS' 'Other')

function ADD_DEVICE {
    clear
    COUNT=0
    if [[ $1 ]]
    then
        echo $1
    fi
    for DEVICE in "${ALL_DEVICES[@]}"; do
        (( COUNT++ ))
        echo $COUNT. $DEVICE
    done
    read CHOSEN_DEVICE
}

ADD_DEVICE 'Enter the type of device you adding.'

until [[ $CHOSEN_DEVICE =~ ^[1-4]$ ]]; do
    ADD_DEVICE 'Please enter an available option'
done

DEVICE_SELECTED=${ALL_DEVICES[$CHOSEN_DEVICE - 1]}

clear
sleep 1

echo "Enter your device brand (eg. Samsung, iPhone, Dell, HP)."
read BRAND

clear
sleep 1

echo 'Enter the model (A32, iP15, Win10) IMPORTANT!'
read MODEL

ALL_OS=('IOS' 'Windows' 'Linux' 'WSL')

function ADD_OS {
    clear
    sleep 1
    if [[ $1 ]]
    then
        echo $1
    fi
    COUNT=0
    for OS in "${ALL_OS[@]}"; do
        (( COUNT++ ))
        echo $COUNT. $OS
    done
    read CHOSEN_OS
}

ADD_OS "Enter your device operating system."

until [[ $CHOSEN_OS =~ ^[1-4]$ ]]; do
    ADD_OS 'Enter a valid option'
done

clear
sleep 1

OS=${ALL_OS[$CHOSEN_OS - 1]}

echo Enter your IP address
read IP

OCTET='(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])'
IP_REGEX="^100\.${OCTET}\.${OCTET}\.${OCTET}$"


until [[ $IP =~ $IP_REGEX ]]; do
    clear
    echo "Enter a valid IP starting with 100:"
    read IP
done

ENTRY=$(
    $PSQL "INSERT INTO devices (owner, device, model, os, ip, brand)
    VALUES ('$NAME', '$DEVICE_SELECTED', '$MODEL', '$OS', '$IP', '$BRAND')"
)

if [[ "$ENTRY" == 'INSERT 0 1' ]]
then
    echo Your Devices has been Added successfully.
else
    echo Upload failed
    echo $ENTRY
fi




