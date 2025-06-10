#!/bin/bash
for MAC in XX:XX:XX:XX:XX:XX YY:YY:YY:YY:YY:YY; do
    bluetoothctl connect "$MAC"
done

