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

First, run the following to obtain any available package upgrades:

```
sudo apt-get update && sudo apt-get upgrade -y
```

Optionally, change the hostname and password of your Raspberry Pi with `raspi-config`. It is recommended to change the default password due to security reasons.

Next, install the Unicorn pHAT Python library. This is done by running `curl https://get.pimoroni.com/unicornhat  | bash`, as noted [here](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-unicorn-phat).

### 4. Bluetooth Connectivity

The Unicorn pHAT prevents the usage of the 3.5mm output device on the Raspberry Pi. Therefore, audio is only available over HDMI or Bluetooth.

Thus, `Ambience` relies on Bluetooth audio.

#### `pulseaudio`

We will first configure Bluetooth audio. Install `pulseaudio` with Bluetooth support:

```
sudo apt-get install pulseaudio pulseaudio-module-bluetooth bluez
```

Optionally, install `mplayer` to test audio output:

```
sudo apt-get install mplayer
```

Each user utilising `pulseaudio` must be part of the `pulse-access` group. Thus:

```
sudo adduser root pulse-access
sudo adduser pi pulse-access
```

Next, authorise `pulseaudio` to use BlueZ's D-BUS interface:

```
sudo cat <<EOF >/etc/dbus-1/system.d/pulseaudio-bluetooth.conf
<busconfig>

<policy user="pulse">
<allow send_destination="org.bluez"/>
</policy>

</busconfig>
EOF
```

Additionally, load `pulseaudio`'s Bluetooth discovery module:

```
sudo cat <<EOF >> /etc/pulse/system.pa
#
### Bluetooth Support
.ifexists module-bluetooth-discover.so
load-module module-bluetooth-discover
.endif
EOF
```

Finally, create a `systemd` entry for `pulseaudio` so that it starts on system boot:

```
sudo cat <<EOF >/etc/systemd/system/pulseaudio.service
[Unit]
Description=Pulse Audio

[Service]
Type=simple
ExecStart=/usr/bin/pulseaudio --system --disallow-exit --disable-shm --exit-idle-time=-1

[Install]
WantedBy=multi-user.target
EOF
```

Then, enable this new service:

```
sudo systemctl daemon-reload
sudo systemctl enable pulseaudio.service
```

#### Speaker Connection

Once `pulseaudio` is configured, the Bluetooth speaker can be paired.

First, restart Bluetooth:

```
sudo systemctl restart bluetooth
```

Next, start `bluetoothctl`:

```
sudo bluetoothctl
```

Power on the Bluetooth hardware:

```
[bluetooth]# power on
[bluetooth]# agent on
[bluetooth]# default-agent
```

Scan for your Bluetooth speaker:

```
[bluetooth]# scan on

# Example output:
Discovery started
[CHG] Controller 00:19:5B:52:94:A3 Discovering: yes
...
[CHG] Device 00:1D:DF:BE:10:4C Name: PHILIPS AS111
[CHG] Device 00:1D:DF:BE:10:4C Alias: PHILIPS AS111
...
```

Note the MAC address of your speaker (i.e., `00:1D:DF:BE:10:4C`), and pair to it:

```
[bluetooth]# pair 00:1D:DF:BE:10:4C
```

Trust the device, and then connect:

```
[bluetooth]# trust 00:1D:DF:BE:10:4C
[bluetooth]# connect 00:1D:DF:BE:10:4C

# An error of "Failed to connect: org.bluez.Error.Failed" can be ignored
```

Exit `bluetoothctl`:

```
[bluetooth]# scan off
[bluetooth]# exit
```

Now, start the `pulseaudio` service to finish:

```
sudo systemctl start pulseaudio.service
```

**Keep a note of your speaker's MAC address, you will need it later!**

If you previously installed `mplayer`, it now can be used to test audio output.

```
mplayer -ao pulse file.mp3
```

Sources:
- Del Grande, D. (2015). _Bluetooth and Audio # Bluez-5 + PulseAudio-5_. Available at: https://github.com/davidedg/NAS-mod-config/blob/master/bt-sound/bt-sound-Bluez5_PulseAudio5.txt. [Accessed 7th May 2018].

#### Bluetooth LE advertisement

`Ambience` requires correctly configured Bluetooth connectivity to advertise a Bluetooth Low Energy (LE) service, used for power management.

This is a simple configuration. First, open the configuration file for the `bluetooth` service:

```
sudo nano /lib/systemd/system/bluetooth.service
```

Modify the line starting with `ExecStart`:

```
...
ExecStart=/usr/libexec/bluetooth/bluetoothd --experimental
...
```

Save the file with `CTRL+O`, then exit `nano` with `CTRL+X`.

Finally, reboot the system for configuration changes to take effect:

```
sudo reboot
```

### 5. `Ambience` Configuration

First, requisite dependencies need to be installed:

```
sudo apt-get install python pip python-pyaudio -y
sudo pip install --user paho-mqtt
```

Some further packages are required for the Bluetooth LE advertisement used in the `Ambience` system for power management:

```
sudo apt-get install python-dbus python-gobject -y
```

The `Ambience` system itself can now be installed.

First, copy the contents of the included `/Ambience` folder to `/home/pi/ambience/` via e.g. SFTP.

Then, ensure `main.py` is executable:

```
sudo chmod 0777 /home/pi/ambience/main.py
```

Next, create a `systemd` entry for `Ambience` so that it starts on system boot:

```
sudo cat <<EOF >/etc/systemd/system/ambience.service
[Unit]
Description=Automated ambient lighting and sound system
After=bluetooth.target

[Service]
ExecStart=/home/pi/ambience/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Then, enable this new service:

```
sudo systemctl daemon-reload
sudo systemctl enable ambience.service
```

#### Speaker Configuration

`Ambience` provides an automated script to connect to your Bluetooth speaker.

Open `/home/pi/ambience/audio/scripts/mrt_autopair.sh` with `nano`, and then change the following line:

```
...
connect 00:00:00:00:00:00
...

# Change to:

...
connect <YOUR MAC ADDRESS HERE>
...
```

Now, reboot the Raspberry Pi:

```
sudo reboot
```

If all is configured correctly, after around a minute a loading animation will be displayed on the Unicorn pHAT. You can turn on your Bluetooth speaker at this point, which will automatically be connected to.

Configuration is now finished. Refer back to README.md for configuring the MQTT broker for data transfer.
