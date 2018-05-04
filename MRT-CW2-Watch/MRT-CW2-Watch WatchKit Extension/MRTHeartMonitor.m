//
//  MRTHeartMonitor.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "MRTHeartMonitor.h"

@interface HKQuery (Private)
+ (id)_predicateForObjectsFromAppleWatches;
@end

@interface MRTHeartMonitor ()
@property (nonatomic, strong) HKHealthStore *healthStore;
@property (nonatomic, strong) HKWorkoutSession *workoutSession;
@property (nonatomic, readwrite) HKWorkoutSessionState workoutSessionState;

@property (nonatomic, strong) HKQuery *hrvQuery;
@property (nonatomic, strong) HKQuery *heartrateQuery;

@property (nonatomic, strong) NSMutableDictionary *heartrateUpdateHandlers;
@property (nonatomic, strong) NSMutableDictionary *stateUpdateHandlers;
@property (nonatomic, strong) NSMutableDictionary *hrvUpdateHandlers;
@end

@implementation MRTHeartMonitor

+ (instancetype)sharedInstance {
    static MRTHeartMonitor *sharedInstance = nil;
    static dispatch_once_t onceToken;
    
    dispatch_once(&onceToken, ^{
        sharedInstance = [[MRTHeartMonitor alloc] init];
    });
    
    return sharedInstance;
}

- (instancetype)init {
    self = [super init];
    
    if (self) {
        self.healthStore = [[HKHealthStore alloc] init];
        self.workoutSessionState = HKWorkoutSessionStateNotStarted;
        
        self.heartrateUpdateHandlers = [NSMutableDictionary dictionary];
        self.hrvUpdateHandlers = [NSMutableDictionary dictionary];
        self.stateUpdateHandlers = [NSMutableDictionary dictionary];
    }
    
    return self;
}

/**
 * Requests authorisation from HealthKit for HRV and heartrate data types
 */
- (void)_requestAuthorisationIfNecessaryWithCompletion:(void (^)(BOOL success, NSError *error))completionHandler {
    // Request authorisation if needed
    NSSet *readTypes = [NSSet setWithObjects:
                        [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRateVariabilitySDNN],
                        [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate],
                        nil];
    
    // No need to re-request if already authorised
    BOOL allAuthd = YES;
    for (id type in readTypes) {
        if (![self.healthStore authorizationStatusForType:type]) {
            allAuthd = NO;
            break;
        }
    }
    
    if (!allAuthd) {
        NSLog(@"Requesting auth for read types: %@", readTypes);
        
        [self.healthStore requestAuthorizationToShareTypes:nil readTypes:readTypes completion:^(BOOL success, NSError *error) {
            completionHandler(success, error);
        }];
    } else {
        completionHandler(YES, nil);
    }
}

/**
 * Publicly accessible method for adding a data observer
 */
- (void)addObserverWithName:(NSString*)name withStateUpdateHandler:(void (^)(HKWorkoutSessionState state))stateUpdateHandler hrvUpdateHandler:(void (^)(HKQuantitySample*, NSError*))hrvUpdateHandler andHeartrateUpdateHandler:(void (^)(HKQuantitySample*, NSError*))heartrateUpdateHandler {
    
    [self.stateUpdateHandlers setObject:[stateUpdateHandler copy] forKey:name];
    [self.heartrateUpdateHandlers setObject:[heartrateUpdateHandler copy] forKey:name];
    [self.hrvUpdateHandlers setObject:[hrvUpdateHandler copy] forKey:name];
}

/**
 * Publicly accessible method for removing a data observer
 */
- (void)removeObserverWithName:(NSString*)name {
    [self.heartrateUpdateHandlers removeObjectForKey:name];
    [self.hrvUpdateHandlers removeObjectForKey:name];
    [self.stateUpdateHandlers removeObjectForKey:name];
}

/**
 * Publicly accessible method for starting heart queries (via a workout)
 */
- (void)startRecordingData {
    self.workoutSessionState = HKWorkoutSessionStateNotStarted;
    
    // Update observers of initial state
    for (void (^handler)(HKWorkoutSessionState) in self.stateUpdateHandlers.allValues) {
        handler(self.workoutSessionState);
    }
    
    [self _requestAuthorisationIfNecessaryWithCompletion:^(BOOL success, NSError *error) {
        // Create workout session.
        // Queries for data will begin running once the workout has started.
        if (error) {
            NSLog(@"*** Authorisation error: %@", error.localizedDescription);
            return;
        }
        
        HKWorkoutConfiguration *configuration = [[HKWorkoutConfiguration alloc] init];
        configuration.activityType = HKWorkoutActivityTypeOther;
        configuration.locationType = HKWorkoutSessionLocationTypeIndoor;
        
        NSError *err = nil;
        HKWorkoutSession *session = [[HKWorkoutSession alloc] initWithConfiguration:configuration error:&err];
        
        if (session == nil) {
            // perform proper error handling here...
            NSLog(@"*** Unable to create the workout session: %@ ***", err.localizedDescription);
        } else {
            session.delegate = self;
            [self.healthStore startWorkoutSession:session];
            
            self.workoutSession = session;
        }
    }];
}

- (void)_retrieveAverageForIdentifier:(HKQuantityType*)type withCompletionHandler:(void (^)(HKQuantity *sample, NSError *error))handler {
    // We want an average for the past week
    NSDate *startDate = [NSDate dateWithTimeIntervalSinceNow:-7*24*60*60];
    NSDate *endDate = [NSDate date];
    
    NSPredicate *predicate = [HKQuery predicateForSamplesWithStartDate:startDate endDate:endDate options:HKQueryOptionStrictStartDate];
    
    HKStatisticsQuery *query = [[HKStatisticsQuery alloc] initWithQuantityType:type quantitySamplePredicate:predicate options:HKStatisticsOptionDiscreteAverage completionHandler:^(HKStatisticsQuery *query, HKStatistics *result, NSError *error) {
        
        if (error) {
            handler(nil, error);
            return;
        }
        
        HKQuantity *quantity = result.averageQuantity;
        handler(quantity, nil);
    }];
    
    [self.healthStore executeQuery:query];
}

- (void)retrieveHeartRateAverageWithCompletionHandler:(void (^)(int average, NSError *error))handler {
    [self _retrieveAverageForIdentifier:[HKQuantityType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate] withCompletionHandler:^(HKQuantity *sample, NSError *error) {
        
        if (error) {
            handler(0, error);
        } else {
            double average = [sample doubleValueForUnit:[[HKUnit countUnit] unitDividedByUnit:[HKUnit minuteUnit]]];
            handler((int)average, nil);
        }
    }];
}

- (void)retrieveHRVAverageWithCompletionHandler:(void (^)(int average, NSError *error))handler {
    [self _retrieveAverageForIdentifier:[HKQuantityType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRateVariabilitySDNN] withCompletionHandler:^(HKQuantity *sample, NSError *error) {
        
        if (error) {
            handler(0, error);
        } else {
            double average = [sample doubleValueForUnit:[HKUnit secondUnitWithMetricPrefix:HKMetricPrefixMilli]];
            handler((int)average, nil);
        }
    }];
}

/**
 * Creates a query for the given type and update handler.
 */
- (HKAnchoredObjectQuery*)_queryWithType:(HKSampleType*)type andUpdateHandlers:(NSDictionary*)updateHandlers {
    // Quick private API to only get HRV objects from any Apple Watch connected
    NSPredicate *devicePredicate = [HKQuery _predicateForObjectsFromAppleWatches];
    
    // We only want new samples really, but need to get the newest of the past 6 hours to get started.
    NSPredicate *datePredicate = [HKQuery predicateForSamplesWithStartDate:[NSDate dateWithTimeIntervalSinceNow:-60*60*6] endDate:[NSDate distantFuture] options:HKQueryOptionNone];
    
    NSPredicate *predicate = [NSCompoundPredicate andPredicateWithSubpredicates:@[devicePredicate, datePredicate]];
    
    HKAnchoredObjectQuery *query = [[HKAnchoredObjectQuery alloc] initWithType:type predicate:predicate anchor:nil limit:HKObjectQueryNoLimit resultsHandler:^(HKAnchoredObjectQuery *query, NSArray<__kindof HKSample *> * _Nullable sampleObjects, NSArray<HKDeletedObject *> * _Nullable deletedObjects, HKQueryAnchor * _Nullable newAnchor, NSError * _Nullable error) {
        
        if (!error) {
            // Only take the most recent of these older samples to start off sending of data
            
            // Call all observers for this new data
            for (void (^handler)(HKQuantitySample*, NSError*) in updateHandlers.allValues) {
                handler([sampleObjects lastObject], nil);
            }
        } else {
            // Call all observers for this error
            for (void (^handler)(HKQuantitySample*, NSError*) in updateHandlers.allValues) {
                handler(nil, error);
            }
        }
        
    }];
    
    [(HKAnchoredObjectQuery*)query setUpdateHandler:^(HKAnchoredObjectQuery * _Nonnull query, NSArray<__kindof HKSample *> * _Nullable addedObjects, NSArray<HKDeletedObject *> * _Nullable deletedObjects, HKQueryAnchor * _Nullable newAnchor, NSError * _Nullable error) {
        if (!error) {
            for (HKQuantitySample *object in addedObjects) {
                // Call all observers for this new data
                for (void (^handler)(HKQuantitySample*, NSError*) in updateHandlers.allValues) {
                    handler(object, nil);
                }
            }
        } else {
            // Call all observers for this error
            for (void (^handler)(HKQuantitySample*, NSError*) in updateHandlers.allValues) {
                handler(nil, error);
            }
        }
    }];
    
    return query;
}

/**
 * Starts the HRV query
 */
- (void)_startHRVQueryWithHandlers:(NSDictionary*)updateHandlers {
    HKSampleType *type = [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRateVariabilitySDNN];
    
    self.hrvQuery = [self _queryWithType:type andUpdateHandlers:updateHandlers];
    
    [self.healthStore executeQuery:self.hrvQuery];
}

/**
 * Starts the heartrate query
 */
- (void)_startHeartrateQueryWithHandlers:(NSDictionary*)updateHandlers {
    HKSampleType *type = [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate];
    
    self.heartrateQuery = [self _queryWithType:type andUpdateHandlers:updateHandlers];
    
    [self.healthStore executeQuery:self.heartrateQuery];
}

- (void)stopRecordingData {
    // Stop workout - we don't want to save the data it generated mind you...
    [self.healthStore endWorkoutSession:self.workoutSession];
    
    // Stop queries
    [self.healthStore stopQuery:self.hrvQuery];
    [self.healthStore stopQuery:self.heartrateQuery];
}

- (HKWorkoutSessionState)currentState {
    return self.workoutSessionState;
}

////////////////////////////////////////////////////////////////////////////////////////////
// HKWorkoutSessionDelegate
////////////////////////////////////////////////////////////////////////////////////////////

- (void)workoutSession:(HKWorkoutSession *)workoutSession
      didChangeToState:(HKWorkoutSessionState)toState
             fromState:(HKWorkoutSessionState)fromState
                  date:(NSDate *)date {
    
    // Update observers of state changes
    for (void (^handler)(HKWorkoutSessionState) in self.stateUpdateHandlers.allValues) {
        handler(toState);
    }
    
    self.workoutSessionState = toState;
    
    switch (toState) {
        case HKWorkoutSessionStateRunning:
            // Start HRV updates
            [self _startHRVQueryWithHandlers:self.hrvUpdateHandlers];
            
            // Start heartbeat updates
            [self _startHeartrateQueryWithHandlers:self.heartrateUpdateHandlers];
            break;
            
        default:
            break;
    }
}

- (void)workoutSession:(nonnull HKWorkoutSession *)workoutSession didFailWithError:(nonnull NSError *)error {
    NSLog(@"*** Workout session did fail: %@", error.localizedDescription);
}

@end
