## Ambience

This project provides ambient sound and lighting to achieve the following:

1. Increased user attention throughout the day, by enriching the local environment with greater blue light levels and playing "study music"
2. Automated user stress reduction based upon heart data, by emitting a red hue and playing "calming music"
3. Optional biofeedback to the user of their heart data when stress is detected, by blinking the output LEDs in sync with the user's heart data

Also included is power management through Bluetooth-based proximity detection.

To generate heart data, two methods can be used: live readings from an Apple Watch's heart sensor, or through emulation.

### Dependancies

This project relies on the following:

- `paho-mqtt`
- `pyaudio`
- `MQTTKit`

Only `paho-mqtt` and `pyaudio` need to first be installed on either the Raspberry Pi, or the machine emulating it.

`MQTTKit` has been pre-compiled for the Apple Watch application, as `/MRT-CW2-Watch/lib/libMQTTKit.a`. This is the result of compiling [MQTTKit](https://github.com/mobile-web-messaging/MQTTKit), available under the Apache License 2.0.

### Setup

#### Emulated

If no Raspberry Pi with a Unicorn pHAT is available, then emulation is required.

First, install the requisite dependencies on your machine:

```
#########################################
# MQTT library
#########################################

sudo pip install --user paho-mqtt

#########################################
# Audio output
#########################################

# For macOS users:
# brew install portaudio

# For Debian/Ubuntu
# sudo apt-get install python-pyaudio

sudo pip install --user pyaudio
```

Then to emulate the Raspberry Pi, run `python Ambience/main.py`. This is the same code as ran on a real device, with the Unicorn pHAT being emulated via a simple GUI window rendered by `tkinter`.

Also supported is emulation of heart data. This can be used in conjunction with either a real or emulated Raspberry Pi.
To emulate heart data, run `python Faux\ Data/main.py`.

#### Full Installation

Refer to [`INSTALL.md`](https://github.com/Matchstic/automated-ambience/blob/master/INSTALL.md) for full installation instructions.

#### MQTT Broker

To communicate between the producer of heart data, and the Raspberry Pi, the MQTT protocol is utilised. An MQTT broker faciliates a publish-subscribe model between multiple devices over a number of `topics`.

In `Ambience`, the MQTT broker may be emulated, such as when needing to send data through a firewall. This emulation occurs when both heart data and the Raspberry Pi are being emulated on the same machine.

When running on real hardware, you will need access to an MQTT broker. One that is known to work well with this project is CloudMQTT, which offers a free plan. Once you have access to a broker, update the following global variables in `/Local/data/MQTTManager.py` as appropriate:

- `MQTT_SERVER` - the broker's address, e.g. `xyz.cloudmqtt.com`
- `MQTT_PORT` - the broker's port number, e.g. `1883`.

Furthermore, update the same variables in `/watchOS Application/iOS/MRTMQTTManager.m`

Next, the broker's users must be configured. Assuming you are using CloudMQTT, open the `Users` page on your MQTT instance.

Create two users, `rpi-client` and `watch-client`. The password for each is of your choosing. Once created, update the previous two files with the password/s chosen.

These two users now need to be afforded read/write privileges to MQTT topics. Create two new `Topic` ACLs on the same page, one for each user, with the pattern for both users being "#" without the quotation marks.
Make sure to enable read access for `rpi-client`, and write access for `watch-client`.

### Other Notes

Due to the Unicorn pHAT preventing usage of the 3.5mm device for audio output, Bluetooth audio has been implemented. See [`INSTALL.md`](https://github.com/Matchstic/automated-ambience/blob/master/INSTALL.md) for configuration details on real hardware.

The subsumption architecture is utilised to arbitrate between the output for the different tasks of `Ambience`. The power management task is highest priority, with `StressReductionTask`, `DaytimeAttentionTask` then `InitialisationTask` in priority order.

The time of day is taken into account in the `DaytimeAttentionTask`, where an increased level of red is emitted closest to midnight, and an increased level of green at midday. This then adjusts the outputted blue hue throughout the day.

### Related Research and Publications

// TODO: blue for attention, red for de-stress, Yorgos biofeedback, other biofeedback

### License

Licensed under the GNU Public License, version 2 (GPLv2).
