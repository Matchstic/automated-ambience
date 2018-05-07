## Automated Ambience

This project provides ambient sound and lighting to achieve the following:

1. Increased user attention throughout the day
2. Automated user stress reduction based upon heart data
3. Optional biofeedback to the user of their heart data when stress is detected

Also included is power management through Bluetooth-based proximity detection.

To generate heart data, two methods can be used: live readings from an Apple Watch's heart sensor, or through emulation.

### Components

// Sensors used: heart, time of day, Bluetooth-proximity
// Hardware and software components - Unicorn pHAT

### System architecture

// subsumption architecture.

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
To emulate heart rate data, run `python Faux\ Data/main.py`.

#### Full Installation

Refer to [INSTALL.md](https://github.com/Matchstic/automated-ambience/blob/master/INSTALL.md) for full installation instructions.

#### MQTT Broker

To communicate between the producer of heart data, and the Raspberry Pi, the MQTT protocol is utilised. An MQTT broker faciliates a publish-subscribe model between multiple devices over a number of `topics`.

In this project, the MQTT broker may be emulated, such as when needing to send data through a firewall. This emulation occurs when both heart data and the Raspberry Pi are being emulated on the same machine.

When running on real hardware, you will need access to an MQTT broker. One that is known to work well with this project is CloudMQTT, which offers a free plan. Once you have access to a broker, update the following global variables in `/Local/data/MQTTManager.py` as appropriate:

- `MQTT_SERVER` - the broker's address, e.g. `xyz.cloudmqtt.com`
- `MQTT_PORT` - the broker's port number, e.g. `1883`.



// TODO: Setup of topic ACLs and users/passwords

// TODO: Update Apple Watch client's variables


### Other Notes

Due to the Unicorn pHAT preventing usage of the 3.5mm output device for output, Bluetooth audio has been implemented. See `INSTALL.md` for configuration details on real hardware.

### Related Research and Publications

// TODO: blue for attention, red for de-stress, Yorgos biofeedback, other biofeedback

### License

Licensed under the BSD 2-Clause License.
