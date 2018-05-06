# LICENSING NOTICE
# The vast majority of this code is reused from:
# https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test/example-advertisement

'''
 *  BlueZ - Bluetooth protocol stack for Linux
 *
 * Copyright (C) 2000-2001  Qualcomm Incorporated
 * Copyright (C) 2002-2003  Maxim Krasnyansky <maxk@qualcomm.com>
 * Copyright (C) 2002-2010  Marcel Holtmann <marcel@holtmann.org>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

from multiprocessing import Process

# Class is provided by mclarke, to encapuslate the original main() function.
class BluetoothLowEnergyBroadcast():
    def __init__(self):
        pass
        
    def speaker_connected(self):
        self.start_broadcast()
        
    def start_broadcast(self):
        # Create and start the sub_process
        self.subprocess = AdvertisementSubprocess()
    
        self.subprocess_process = Process(target=self.subprocess.main_loop)
        self.subprocess_process.start()

########################################################################################
# Subprocess
########################################################################################

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

IS_EMULATED = True

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

import array
import gobject

from random import randint

class AdvertisementSubprocess():    
    def __init__(self):
        self.mainloop = None
    
    def main_loop(self):            
        self.mainloop = None
            
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SystemBus()

        adapter = self.find_adapter(bus)
        if not adapter:
            print '[WARN] LEAdvertisingManager1 interface not found'
            return

        adapter_props = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                       "org.freedesktop.DBus.Properties");

        adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

        ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)

        test_advertisement = AdvertisementSubprocess.UserDataAdvertisement(bus, 0)

        mainloop = gobject.MainLoop()

        ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                         reply_handler=self.register_ad_cb,
                                         error_handler=self.register_ad_error_cb)
        # Start the broadcast!
        mainloop.run()

    def register_ad_cb(self):
        print '[INFO] Bluetooth Low Energy advertisement started'

    def register_ad_error_cb(self, error):
        print '[WARN] Failed to register advertisement: ' + str(error)
        #self.mainloop.quit()

    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()

        for o, props in objects.iteritems():
            if LE_ADVERTISING_MANAGER_IFACE in props:
                return o

        return None
    

    class InvalidArgsException(dbus.exceptions.DBusException):
        _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


    class NotSupportedException(dbus.exceptions.DBusException):
        _dbus_error_name = 'org.bluez.Error.NotSupported'


    class NotPermittedException(dbus.exceptions.DBusException):
        _dbus_error_name = 'org.bluez.Error.NotPermitted'


    class InvalidValueLengthException(dbus.exceptions.DBusException):
        _dbus_error_name = 'org.bluez.Error.InvalidValueLength'


    class FailedException(dbus.exceptions.DBusException):
        _dbus_error_name = 'org.bluez.Error.Failed'


    class Advertisement(dbus.service.Object):
        PATH_BASE = '/org/bluez/example/advertisement'

        def __init__(self, bus, index, advertising_type):
            self.path = self.PATH_BASE + str(index)
            self.bus = bus
            self.ad_type = advertising_type
            self.service_uuids = None
            self.manufacturer_data = None
            self.solicit_uuids = None
            self.service_data = None
            self.include_tx_power = None
            dbus.service.Object.__init__(self, bus, self.path)

        def get_properties(self):
            properties = dict()
            properties['Type'] = self.ad_type
            if self.service_uuids is not None:
                properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
                                                        signature='s')
            if self.solicit_uuids is not None:
                properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
                                                        signature='s')
            if self.manufacturer_data is not None:
                properties['ManufacturerData'] = dbus.Dictionary(
                    self.manufacturer_data, signature='qv')
            if self.service_data is not None:
                properties['ServiceData'] = dbus.Dictionary(self.service_data,
                                                            signature='sv')
            if self.include_tx_power is not None:
                properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
            return {LE_ADVERTISEMENT_IFACE: properties}

        def get_path(self):
            return dbus.ObjectPath(self.path)

        def add_service_uuid(self, uuid):
            if not self.service_uuids:
                self.service_uuids = []
            self.service_uuids.append(uuid)

        def add_solicit_uuid(self, uuid):
            if not self.solicit_uuids:
                self.solicit_uuids = []
            self.solicit_uuids.append(uuid)

        def add_manufacturer_data(self, manuf_code, data):
            if not self.manufacturer_data:
                self.manufacturer_data = dbus.Dictionary({}, signature='qv')
            self.manufacturer_data[manuf_code] = dbus.Array(data, signature='y')

        def add_service_data(self, uuid, data):
            if not self.service_data:
                self.service_data = dbus.Dictionary({}, signature='sv')
            self.service_data[uuid] = dbus.Array(data, signature='y')

        @dbus.service.method(DBUS_PROP_IFACE,
                             in_signature='s',
                             out_signature='a{sv}')
        def GetAll(self, interface):
            if interface != LE_ADVERTISEMENT_IFACE:
                raise InvalidArgsException()
            return self.get_properties()[LE_ADVERTISEMENT_IFACE]

        @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                             in_signature='',
                             out_signature='')
        def Release(self):
            pass
            #print '[BLUETOOTH] %s: Released!' % self.path

    class UserDataAdvertisement(Advertisement):

        def __init__(self, bus, index):
            AdvertisementSubprocess.Advertisement.__init__(self, bus, index, 'peripheral')
        
            # NOTE: I have modified the service UUIDs and service data here.
            # This has been modified to broadcast the User Data service ID.
        
            self.add_service_uuid('181C')
            self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
            self.add_service_data('181C', [0x61,0x6d,0x62,0x69,0x65,0x6e,0x63,0x65])
            self.include_tx_power = True
        