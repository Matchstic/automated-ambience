//
//  ExtensionDelegate.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "ExtensionDelegate.h"
#import "MRTHeartMonitor.h"
#import "MRTMQTTManager.h"

@interface ExtensionDelegate ()
@property (nonatomic, strong) MRTHeartMonitor *sharedHeartMonitor;
@property (nonatomic, strong) MRTMQTTManager *mqttManager;
@end

@implementation ExtensionDelegate

- (void)applicationDidFinishLaunching {
    // Perform any final initialization of your application.
    self.sharedHeartMonitor = [MRTHeartMonitor sharedInstance];
    self.mqttManager = [[MRTMQTTManager alloc] init];
    
    [self.mqttManager connectToMQTTBroker];
    
    __weak __typeof__(self) weakSelf = self;
    [self.sharedHeartMonitor addObserverWithName:@"extension-delegate" withStateUpdateHandler:^(HKWorkoutSessionState state) {
        if (state == HKWorkoutSessionStateRunning) {
            // Grab our averages now that the workout is running!
            
            [weakSelf.sharedHeartMonitor retrieveHeartRateAverageWithCompletionHandler:^(int average, NSError *error) {
                [[NSUserDefaults standardUserDefaults] setInteger:average forKey:@"averageBpm"];
                [weakSelf.mqttManager updatePreferences];
            }];
            
            [weakSelf.sharedHeartMonitor retrieveHRVAverageWithCompletionHandler:^(int average, NSError *error) {
                [[NSUserDefaults standardUserDefaults] setInteger:average forKey:@"averageHrv"];
                [weakSelf.mqttManager updatePreferences];
            }];
        }
    } hrvUpdateHandler:^(HKQuantitySample *sample, NSError *error) {
        if (!error) {
            [weakSelf didObtainNewHRVSample:sample];
        } else {
            NSLog(@"*** HRV error: %@", error.localizedDescription);
        }
    } andHeartrateUpdateHandler:^(HKQuantitySample *sample, NSError *error) {
        if (!error) {
            [weakSelf didObtainNewHeartrateSample:sample];
        } else {
            NSLog(@"*** Heartrate error: %@", error.localizedDescription);
        }
    }];
    
    // Add some observers for user interaction!
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didReceiveStartMonitoringNotification:) name:@"com.matchstic.mrt-cw2/startmonitoring" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didReceiveStopMonitoringNotification:) name:@"com.matchstic.mrt-cw2/stopmonitoring" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didRecievePreferencesChanged:) name:@"com.matchstic.mrt-cw2/prefschanged" object:nil];
}

- (void)applicationDidBecomeActive {
    // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
}

- (void)applicationWillResignActive {
    // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
    // Use this method to pause ongoing tasks, disable timers, etc.
}

- (void)handleBackgroundTasks:(NSSet<WKRefreshBackgroundTask *> *)backgroundTasks {
    // Sent when the system needs to launch the application in the background to process tasks. Tasks arrive in a set, so loop through and process each one.
    for (WKRefreshBackgroundTask * task in backgroundTasks) {
        // Check the Class of each task to decide how to process it
        if ([task isKindOfClass:[WKApplicationRefreshBackgroundTask class]]) {
            // Be sure to complete the background task once you’re done.
            WKApplicationRefreshBackgroundTask *backgroundTask = (WKApplicationRefreshBackgroundTask*)task;
            [backgroundTask setTaskCompletedWithSnapshot:NO];
        } else if ([task isKindOfClass:[WKSnapshotRefreshBackgroundTask class]]) {
            // Snapshot tasks have a unique completion call, make sure to set your expiration date
            WKSnapshotRefreshBackgroundTask *snapshotTask = (WKSnapshotRefreshBackgroundTask*)task;
            [snapshotTask setTaskCompletedWithDefaultStateRestored:YES estimatedSnapshotExpiration:[NSDate distantFuture] userInfo:nil];
        } else if ([task isKindOfClass:[WKWatchConnectivityRefreshBackgroundTask class]]) {
            // Be sure to complete the background task once you’re done.
            WKWatchConnectivityRefreshBackgroundTask *backgroundTask = (WKWatchConnectivityRefreshBackgroundTask*)task;
            [backgroundTask setTaskCompletedWithSnapshot:NO];
        } else if ([task isKindOfClass:[WKURLSessionRefreshBackgroundTask class]]) {
            // Be sure to complete the background task once you’re done.
            WKURLSessionRefreshBackgroundTask *backgroundTask = (WKURLSessionRefreshBackgroundTask*)task;
            [backgroundTask setTaskCompletedWithSnapshot:NO];
        } else {
            // make sure to complete unhandled task types
            [task setTaskCompletedWithSnapshot:NO];
        }
    }
}

////////////////////////////////////////////////////////////////////////////////
// Data monitor handling
////////////////////////////////////////////////////////////////////////////////

- (void)didReceiveStartMonitoringNotification:(id)sender {
    [self.sharedHeartMonitor startRecordingData];
    
    // TODO: Handle starting Bluetooth LE scanning
}

- (void)didReceiveStopMonitoringNotification:(id)sender {
    [self.sharedHeartMonitor stopRecordingData];
    
    // TODO: Handle stopping Bluetooth LE scanning
}

- (void)didRecievePreferencesChanged:(id)sender {
    [self.mqttManager updatePreferences];
}

- (void)didObtainNewHRVSample:(HKQuantitySample*)sample {
    // Retrieve milliseconds from sample
    HKUnit *unit = [HKUnit secondUnitWithMetricPrefix:HKMetricPrefixMilli];
    double newHRVValue = [sample.quantity doubleValueForUnit:unit];
    
    NSLog(@"New HRV: %f ms @ %@", newHRVValue, [sample startDate]);
    
    // Send to MQTT broker
    [self.mqttManager publishHRVSample:sample];
}

- (void)didObtainNewHeartrateSample:(HKQuantitySample*)sample {
    // Retrieve count/min from sample
    HKUnit *unit = [[HKUnit countUnit] unitDividedByUnit:[HKUnit minuteUnit]];
    int newHeartrateValue = (int)[sample.quantity doubleValueForUnit:unit];
    
    NSLog(@"New BPM: %d count/min @ %@", newHeartrateValue, [sample startDate]);
    
    // Send to MQTT broker
    [self.mqttManager publishBPMSample:sample];
}

- (void)didObtainNewBluetoothSample:(NSInteger)sample {
    // TODO: Process, and add to MQTT queue.
    // NOTE: A value of -1 denotes no base station in range
}

@end
