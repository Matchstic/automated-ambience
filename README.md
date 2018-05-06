## Automated Ambience

This project provides ambient sound and lighting to achieve the following:

1. Increasing of user attention throughout the day
2. Automated user stress reduction based upon heart data, including biofeedback

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
- `MQTTKit` (for the Apple Watch application)

Only `paho-mqtt` and `pyaudio` need to first be installed on either the Raspberry Pi, or the machine emulating it. This is done as follows:

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

`MQTTKit` has been pre-compiled for the Apple Watch application, as `/MRT-CW2-Watch/lib/libMQTTKit.a`. This is the result of compiling the source available [here](https://github.com/mobile-web-messaging/MQTTKit), available under the Apache License 2.0.

### MQTT Broker Setup

To communicate between the producer of heart data, and the Raspberry Pi, the MQTT protocol is utilised. This is implemented by integrating with a third-party shared broker, in this case CloudMQTT. More details on MQTT itself is outside of the scope of this README.

You will need access to an MQTT broker. One that is known to work well with this project is CloudMQTT, which offers a free plan. Once you have access to a broker, update the following global variables in `/Local/data/MQTTManager.py` as appropriate:

- `MQTT_SERVER` - the broker's address, e.g. `xyz.cloudmqtt.com`
- `MQTT_PORT` - the broker's port number, e.g. `1883`.

// TODO: Setup of topic ACLs and users/passwords

// TODO: Update Apple Watch client's variables

**Be aware that this communication occurs on port `15466` to the URL `m14.cloudmqtt.com`. Thus, this project relies on this port to not be blocked by a firewall. Testing in A32 has been done by connecting to an ad-hoc mobile hotspot, avoiding any firewall restrictions.**

### Emulation

If no Raspberry Pi with a Unicorn pHAT is available to use the included system image on, then emulation is required.

To emulate heart rate data, run `main.py` found in `/Faux Data`. This allows for choosing between various datasets to demonstrate the features implemented for the Raspberry Pi.

To emulate the Raspberry Pi itself, run `main.py` in `/Local`. This is the same code as ran on a real device, with the Unicorn pHAT being emulated via a simple GUI window rendered by `tkinter`.

The same MQTT broker is used for both emulation and for a real device.

### Other Notes

Due to the Unicorn pHAT preventing usage of the 3.5mm output device for output, Bluetooth audio has been implemented. See `INSTALL.md` for configuration details.

### Related Research and Publications

// TODO: blue for attention, red for de-stress, Yorgos biofeedback, other biofeedback

### License

Licensed under the BSD 2-Clause License.
