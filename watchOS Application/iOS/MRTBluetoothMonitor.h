//
//  MRTBluetoothMonitor.h
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreBluetooth/CoreBluetooth.h>

@protocol MRTBluetoothMonitorDelegate
- (void)didFindDeviceWithRSSI:(int)rssi;
- (void)didNotFindDevice;
@end

@interface MRTBluetoothMonitor : NSObject <CBCentralManagerDelegate>

@property (nonatomic, strong) CBCentralManager *bluetoothManager;
@property (nonatomic, weak) id<MRTBluetoothMonitorDelegate> delegate;
@property (nonatomic, readwrite) BOOL didSeeDeviceOnLastScan;
@property (nonatomic, readwrite) int deviceLastRSSI;

+ (instancetype)sharedInstance;

- (void)startPeriodicScanningWithDelegate:(id<MRTBluetoothMonitorDelegate>)delegate;

@end
