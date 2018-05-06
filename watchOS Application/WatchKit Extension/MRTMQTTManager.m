//
//  MRTMQTTManager.m
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "MRTMQTTManager.h"

@implementation MRTMQTTManager

- (instancetype)init {
    self = [super init];
    
    if (self) {
        self.isConnected = NO;
        
        if ([WCSession isSupported]) {
            self.companionSession = [WCSession defaultSession];
            self.companionSession.delegate = self;
            
            [self.companionSession activateSession];
        }
    }
    
    return self;
}

- (void)connectToMQTTBroker {
    NSDictionary *message = @{@"opcode":@"connect"};
    [self _sendMessage:message];
}

- (void)disconnectFromMQTTBroker {
    NSDictionary *message = @{@"opcode":@"disconnect"};
    [self _sendMessage:message];
}

- (void)updatePreferences {
    BOOL heartFeedbackState = [[[NSUserDefaults standardUserDefaults] objectForKey:@"heartFeedback"] boolValue];
    BOOL overrideStressThreshold = [[[NSUserDefaults standardUserDefaults] objectForKey:@"overrideStressThreshold"] boolValue];
    int averageBpm = [[[NSUserDefaults standardUserDefaults] objectForKey:@"averageBpm"] intValue];
    int averageHrv = [[[NSUserDefaults standardUserDefaults] objectForKey:@"averageHrv"] intValue];
    
    // Send to MQTT broker!
    NSString *payload = [NSString stringWithFormat:@"{ \"heartFeedback\": %d, \"averageBPM\": %d, \"averageHRV\": %d, \"overrideStressThreshold\": %d }", heartFeedbackState, averageBpm, averageHrv, overrideStressThreshold];
    NSString *topic = @"prefs";
    NSNumber *retain = [NSNumber numberWithBool:YES];
    
    NSDictionary *message = @{@"opcode":@"publish", @"payload":payload, @"topic":topic, @"retain":retain};
    [self _sendMessage:message];
}

- (void)publishBPMSample:(HKQuantitySample*)sample {
    self.lastBPMSample = sample;
    
    [self _publishCurrentSamples];
}

- (void)publishHRVSample:(HKQuantitySample*)sample {
    self.lastHRVSample = sample;
    
    [self _publishCurrentSamples];
}

- (void)_publishCurrentSamples {
    NSString *payload = [self _currentDataToString];
    NSString *topic = @"data";
    NSNumber *retain = [NSNumber numberWithBool:NO];
    
    NSDictionary *message = @{@"opcode":@"publish", @"payload":payload, @"topic":topic, @"retain":retain};
    [self _sendMessage:message];
}

- (void)_sendMessage:(NSDictionary*)dictionary {
    if (!self.isConnected)
        return;
    
    [self.companionSession sendMessage:dictionary replyHandler:^(NSDictionary<NSString *,id> * _Nonnull replyMessage) {
        // nop
    } errorHandler:^(NSError * _Nonnull error) {
        if (error) {
            NSLog(@"[WCSession] Error: %@", error.localizedDescription);
        }
    }];
}

- (NSString*)_currentDataToString {
    HKUnit *unit = [[HKUnit countUnit] unitDividedByUnit:[HKUnit minuteUnit]];
    int bpm = (int)[self.lastBPMSample.quantity doubleValueForUnit:unit];
    
    HKUnit *unit2 = [HKUnit secondUnitWithMetricPrefix:HKMetricPrefixMilli];
    double hrv = [self.lastHRVSample.quantity doubleValueForUnit:unit2];
    
    return [NSString stringWithFormat:@"{ \"bpm\": %d, \"bpmTimestamp\": %d, \"hrv\": %d, \"hrvTimestamp\": %d}",
                                        bpm,
                                        (int)[self.lastBPMSample startDate].timeIntervalSince1970,
                                        (int)hrv,
                                        (int)[self.lastHRVSample startDate].timeIntervalSince1970];
}

- (void)session:(nonnull WCSession *)session activationDidCompleteWithState:(WCSessionActivationState)activationState error:(nullable NSError *)error {
    // nop.
    if (!error)
        self.isConnected = YES;
}

@end
