//
//  MRTBluetoothMonitor.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "MRTBluetoothMonitor.h"

#define DEVICE_NAME @"ambience"

@implementation MRTBluetoothMonitor

+ (instancetype)sharedInstance {
    static MRTBluetoothMonitor *sharedInstance = nil;
    static dispatch_once_t onceToken;
    
    dispatch_once(&onceToken, ^{
        sharedInstance = [[MRTBluetoothMonitor alloc] init];
    });
    
    return sharedInstance;
}

- (instancetype)init {
    self = [super init];
    
    if (self) {
        self.bluetoothManager = [[CBCentralManager alloc] initWithDelegate:self queue:nil];
    }
    
    return self;
}

- (void)startPeriodicScanningWithDelegate:(id<MRTBluetoothMonitorDelegate>)delegate {
    self.delegate = delegate;
    [self performSelector:@selector(_sendScanResults) withObject:nil afterDelay:5];
}

- (void)_sendScanResults {
    NSLog(@"[BLUETOOTH] Sending scan results...");
    
    if (self.didSeeDeviceOnLastScan) {
        [self.delegate didFindDeviceWithRSSI:self.deviceLastRSSI];
        self.didSeeDeviceOnLastScan = NO;
    } else {
        [self.delegate didNotFindDevice];
    }
    
    [self performSelector:@selector(_sendScanResults) withObject:nil afterDelay:5];
}

/////////////////////////////////////////////////////////////////////////////////////
// Bluetooth delegate
/////////////////////////////////////////////////////////////////////////////////////

- (void)centralManagerDidUpdateState:(nonnull CBCentralManager *)central {
    // nop
    
    switch (central.state) {
        case CBManagerStatePoweredOff:
            NSLog(@"[BLUETOOTH] Hardware is powered off");
            break;
        case CBManagerStatePoweredOn:
            NSLog(@"[BLUETOOTH] Hardware is powered on and ready");
            [self.bluetoothManager scanForPeripheralsWithServices:@[[CBUUID UUIDWithString:@"181C"]] options:nil];
            break;
        case CBManagerStateResetting:
            NSLog(@"[BLUETOOTH] Hardware is resetting");
            break;
        case CBManagerStateUnauthorized:
            NSLog(@"[BLUETOOTH] State is unauthorized");
            break;
        case CBManagerStateUnknown:
            NSLog(@"[BLUETOOTH] State is unknown");
            break;
        case CBManagerStateUnsupported:
            NSLog(@"[BLUETOOTH] Hardware is unsupported on this platform");
            break;
        default:
            break;
    }
}

- (void)centralManager:(CBCentralManager *)central didDiscoverPeripheral:(CBPeripheral *)peripheral advertisementData:(NSDictionary<NSString *,id> *)advertisementData RSSI:(NSNumber *)RSSI {
    
    NSDictionary *data = [advertisementData objectForKey:@"kCBAdvDataServiceData"];
    NSData *serviceData = [data objectForKey:[CBUUID UUIDWithString:@"181C"]];
    NSString *serviceName = [[NSString alloc] initWithData:serviceData encoding:NSASCIIStringEncoding];
    
    if ([serviceName isEqualToString:DEVICE_NAME]) {
        self.didSeeDeviceOnLastScan = YES;
        self.deviceLastRSSI = [RSSI intValue];
    }
}

@end
