#!/bin/bash

# Ensure that we remain discoverable at all times
# XXX: Update the MAC address here as required for your own Bluetooth speaker
bluetoothctl << EOF
discoverable on
connect 00:11:67:00:00:10
EOF