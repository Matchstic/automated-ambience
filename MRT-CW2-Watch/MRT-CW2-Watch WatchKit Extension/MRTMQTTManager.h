//
//  MRTMQTTManager.h
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <HealthKit/HealthKit.h>
#import <WatchConnectivity/WatchConnectivity.h>

@interface MRTMQTTManager : NSObject <WCSessionDelegate>

@property (nonatomic, strong) HKQuantitySample *lastBPMSample;
@property (nonatomic, strong) HKQuantitySample *lastHRVSample;
@property (nonatomic, strong) WCSession *companionSession;
@property (nonatomic, readwrite) BOOL isConnected;

- (void)connectToMQTTBroker;
- (void)disconnectFromMQTTBroker;

- (void)publishBPMSample:(HKQuantitySample*)sample;
- (void)publishHRVSample:(HKQuantitySample*)sample;

- (void)updatePreferences;

@end
