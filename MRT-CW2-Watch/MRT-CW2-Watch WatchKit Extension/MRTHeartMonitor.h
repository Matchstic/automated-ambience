//
//  MRTHeartMonitor.h
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <HealthKit/HealthKit.h>

@interface MRTHeartMonitor : NSObject <HKWorkoutSessionDelegate>

+ (instancetype)sharedInstance;

// Observers for data changes
- (void)addObserverWithName:(NSString*)name withStateUpdateHandler:(void (^)(HKWorkoutSessionState state))stateUpdateHandler hrvUpdateHandler:(void (^)(HKQuantitySample*, NSError*))hrvUpdateHandler andHeartrateUpdateHandler:(void (^)(HKQuantitySample*, NSError*))heartrateUpdateHandler;
- (void)removeObserverWithName:(NSString*)name;

- (void)retrieveHeartRateAverageWithCompletionHandler:(void (^)(int average, NSError *error))handler;
- (void)retrieveHRVAverageWithCompletionHandler:(void (^)(int average, NSError *error))handler;

// State management
- (void)startRecordingData;
- (void)stopRecordingData;
- (HKWorkoutSessionState)currentState;

@end
