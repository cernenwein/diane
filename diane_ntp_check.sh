#!/bin/bash
status=$(timedatectl status)
synced=$(echo "$status" | grep "System clock synchronized:" | awk '{print $4}')
ntp_active=$(echo "$status" | grep "NTP service:" | awk '{print $3}')
ntp_server=$(echo "$status" | grep "Server:" | awk '{print $2}')
echo "[Diane Time Check]"
echo "Clock synchronized: $synced"
echo "NTP service active: $ntp_active"
[ -n "$ntp_server" ] && echo "Current NTP server: $ntp_server"
