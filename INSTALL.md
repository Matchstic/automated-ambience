## Installation

To begin, it is assumed you have the following hardware:

- Raspberry Pi 2 or newer
- WiFi USB adapter (if using the Raspberry Pi 2)
- Bluetooth USB adapter (if using the Raspberry Pi 2)
- Unicorn pHAT
- 4GB or greater SD card
- Bluetooth Speaker

### 1. Hardware

Follow the instructions found [here](https://learn.pimoroni.com/tutorial/sandyj/soldering-phats) to install the Unicorn pHAT on your Raspberry Pi.

### 2. OS Installation

Download the latest Raspbian **Lite** system image from here: [https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/).

Then, flash the OS to your SD card using [Etcher](https://etcher.io/) or something similar.

For wireless/remote setup, create an empty file on the SD card's `boot` partition named `ssh`, and copy the supplied `wpa_supplicant.conf` to the same directory. Make sure to update this latter file with your WiFi network's configuration details.

### 3. Initial Configuration

Boot the Raspberry Pi with this SD card.

First, run `sudo apt-get update && sudo apt-get upgrade` to obtain any available package upgrades.

Optionally, change the hostname and password of your Raspberry Pi with `raspi-config`. It is recommended to change the default password due to security reasons.

Next, install the Unicorn pHAT Python library. This is done by running `curl https://get.pimoroni.com/unicornhat  | bash`, as noted [here](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-unicorn-phat).

### 4. `Ambience` Configuration

// TODO: Copy the Python code into a folder on the Pi over e.g. SFTP, to e.g. `/home/pi/ambience/`.
// TODO: Create systemd entry for auto-launch on boot

### 5. Bluetooth Connectivity

The Unicorn pHAT prevents the usage of the 3.5mm output device on the Raspberry Pi. Therefore, audio is only available over HDMI or Bluetooth.

Furthermore, `Ambience` requires correctly configured Bluetooth connectivity to broadcast a Bluetooth LE service, used for power management.

// TODO: Setup - https://github.com/davidedg/NAS-mod-config/blob/master/bt-sound/bt-sound-Bluez5_PulseAudio5.txt
// TODO: BLE - https://scribles.net/running-ble-advertising-example-code-on-raspbian-stretch/

// !! Cover changing the MAC address of the speaker in `/Local/audio/scripts/mrt_autopair.sh`
