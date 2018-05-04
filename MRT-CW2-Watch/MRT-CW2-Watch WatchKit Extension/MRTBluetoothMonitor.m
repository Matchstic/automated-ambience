//
//  MRTBluetoothMonitor.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "MRTBluetoothMonitor.h"

@implementation MRTBluetoothMonitor

+ (instancetype)sharedInstance {
    static MRTBluetoothMonitor *sharedInstance = nil;
    static dispatch_once_t onceToken;
    
    dispatch_once(&onceToken, ^{
        sharedInstance = [[MRTBluetoothMonitor alloc] init];
    });
    
    return sharedInstance;
}




@end
