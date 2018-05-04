//
//  InterfaceController.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "InterfaceController.h"
#import "MRTHeartMonitor.h"

@interface InterfaceController ()
@property (nonatomic, strong) MRTHeartMonitor *sharedHeartMonitor;
@property (nonatomic, readwrite) BOOL hasStarted;
@end

@implementation InterfaceController

- (void)awakeWithContext:(id)context {
    [super awakeWithContext:context];

    // Configure interface objects here.
    self.sharedHeartMonitor = [MRTHeartMonitor sharedInstance];
    [self.heartFeedbackSwitch setOn:[self _currentHeartFeedbackState]];
}

- (void)willActivate {
    // This method is called when watch view controller is about to be visible to user
    [super willActivate];
    
    if (self.hasStarted)
        [self _updateButtonForState:[self.sharedHeartMonitor currentState]];
    else {
        [self _updateButtonForState:HKWorkoutSessionStateEnded];
        self.hasStarted = YES;
    }
    
    __weak __typeof__(self) weakSelf = self;
    [self.sharedHeartMonitor addObserverWithName:@"interface-controller" withStateUpdateHandler:^(HKWorkoutSessionState state) {
        [weakSelf _updateButtonForState:state];
    } hrvUpdateHandler:^(HKQuantitySample *sample, NSError *error) {
        if (!error)
            [weakSelf didObtainNewHRVSample:sample];
    } andHeartrateUpdateHandler:^(HKQuantitySample *sample, NSError *error) {
        if (!error)
            [weakSelf didObtainNewHeartrateSample:sample];
    }];
}

- (void)didDeactivate {
    // This method is called when watch view controller is no longer visible
    [super didDeactivate];
    
    [self.sharedHeartMonitor removeObserverWithName:@"interface-controller"];
}

/////////////////////////////////////////////////////////////////////////////////////////
// UI handling
/////////////////////////////////////////////////////////////////////////////////////////

- (IBAction)userDidTapStartStopButton:(id)sender {
    // Start monitoring in the extension delegate as required.
    if ([self.sharedHeartMonitor currentState] != HKWorkoutSessionStateRunning) {
        [self _broadcastStartNotification];
    } else {
        [self _broadcastStopNotification];
    }
}

- (void)_broadcastStartNotification {
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/startmonitoring" object:nil];
}

- (void)_broadcastStopNotification {
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/stopmonitoring" object:nil];
}

- (void)_updateButtonForState:(HKWorkoutSessionState)state {
    switch (state) {
        case HKWorkoutSessionStateRunning:
            [self.startStopButton setTitle:@"Stop Monitor"];
            [self.startStopButton setEnabled:YES];
            break;
        case HKWorkoutSessionStateEnded:
        case HKWorkoutSessionStatePaused:
            [self.startStopButton setTitle:@"Start Monitor"];
            [self.startStopButton setEnabled:YES];
            break;
        case HKWorkoutSessionStateNotStarted:
            break;
            
        default:
            break;
    }
}

/////////////////////////////////////////////////////////////////////////////////////////
// Data handling
/////////////////////////////////////////////////////////////////////////////////////////

- (void)didObtainNewHRVSample:(HKQuantitySample*)sample {
    HKUnit *unit = [HKUnit secondUnitWithMetricPrefix:HKMetricPrefixMilli];
    [self.hrvLabel setText:[NSString stringWithFormat:@"HRV: %d ms", (int)[sample.quantity doubleValueForUnit:unit]]];
}

- (void)didObtainNewHeartrateSample:(HKQuantitySample*)sample {
    HKUnit *unit = [[HKUnit countUnit] unitDividedByUnit:[HKUnit minuteUnit]];
    [self.bpmLabel setText:[NSString stringWithFormat:@"BPM: %d count/min", (int)[sample.quantity doubleValueForUnit:unit]]];
}

/////////////////////////////////////////////////////////////////////////////////////////
// Settings handling
/////////////////////////////////////////////////////////////////////////////////////////

- (BOOL)_currentHeartFeedbackState {
    return [[[NSUserDefaults standardUserDefaults] objectForKey:@"heartFeedback"] boolValue];
}

- (IBAction)onHeartFeedbackChanged:(BOOL)value {
    [[NSUserDefaults standardUserDefaults] setObject:[NSNumber numberWithBool:value] forKey:@"heartFeedback"];
    
    // Ensure this change gets posted to the MQTT broker.
    NSLog(@"Notifying prefs changed");
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/prefschanged" object:nil];
}
    
- (IBAction)onThresholdOverrideChanged:(BOOL)value {
    [[NSUserDefaults standardUserDefaults] setObject:[NSNumber numberWithBool:value] forKey:@"overrideStressThreshold"];
    
    // Ensure this change gets posted to the MQTT broker.
    NSLog(@"Notifying prefs changed");
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/prefschanged" object:nil];
}

@end



