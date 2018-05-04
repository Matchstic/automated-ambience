//
//  MRTMQTTManager.m
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "MRTMQTTManager.h"

#define MQTT_SERVER @"m14.cloudmqtt.com"
#define MQTT_PORT 15466
#define MQTT_USERNAME @"watch-client"
#define MQTT_PASSWORD @"raspberrymrt"
#define MQTT_TOPICS @["data", "prefs"]

@implementation MRTMQTTManager

- (instancetype)init {
    self = [super init];
    
    if (self) {
        self.client = [[MQTTClient alloc] initWithClientId:MQTT_USERNAME cleanSession:YES];
        
        self.client.username = MQTT_USERNAME;
        self.client.password = MQTT_PASSWORD;
        self.client.port = MQTT_PORT;
        self.client.host = MQTT_SERVER;
        
        self.isConnected = NO;
        
        // Hook up the WCSession.
        if ([WCSession isSupported]) {
            self.watchSession = [WCSession defaultSession];
            self.watchSession.delegate = self;
            
            [self.watchSession activateSession];
        }
    }
    
    return self;
}

- (void)connectToMQTTBroker {
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        [self.client connectWithCompletionHandler:^(MQTTConnectionReturnCode returnCode) {
            switch (returnCode) {
                case ConnectionAccepted:
                    NSLog(@"[MQTT] Connected to the MQTT broker");
                    self.isConnected = YES;
                    break;
                case ConnectionRefusedNotAuthorized:
                    NSLog(@"[MQTT] Connection refused - not authorised");
                    break;
                case ConnectionRefusedIdentiferRejected:
                    NSLog(@"[MQTT] Connection refused - identifier rejected");
                    break;
                case ConnectionRefusedServerUnavailable:
                    NSLog(@"[MQTT] Connection refused - server unavailable");
                    break;
                case ConnectionRefusedBadUserNameOrPassword:
                    NSLog(@"[MQTT] Connection refused - bad username or password");
                    break;
                case ConnectionRefusedUnacceptableProtocolVersion:
                    NSLog(@"[MQTT] Connection refused - unacceptable protocol version");
                    break;
                default:
                    break;
            }
        }];
    });
}

- (void)disconnectFromMQTTBroker {
    [self.client disconnectWithCompletionHandler:^(NSUInteger code) {
        // nop
    }];
}

- (void)publishString:(NSString*)payload onTopic:(NSString*)topic retain:(BOOL)retain {
    [self.client publishString:payload toTopic:topic withQos:AtLeastOnce retain:retain completionHandler:^(int messageID) {
        // nop.
    }];
}

////////////////////////////////////////////////////////////////////
// WCSession delegate
////////////////////////////////////////////////////////////////////


- (void)session:(nonnull WCSession *)session activationDidCompleteWithState:(WCSessionActivationState)activationState error:(nullable NSError *)error {
    if (error)
        NSLog(@"activation did complete with error: %@", error.localizedDescription);
}

- (void)sessionDidBecomeInactive:(nonnull WCSession *)session {
    // nop
}

- (void)sessionDidDeactivate:(nonnull WCSession *)session {
    // nop
}

- (void)session:(WCSession *)session didReceiveMessage:(NSDictionary<NSString *, id> *)message replyHandler:(void(^)(NSDictionary<NSString *, id> *replyMessage))replyHandler {
   
    NSLog(@"Recieved message: %@", message);
    
    NSString *opcode = [message objectForKey:@"opcode"];
    
    if ([opcode isEqualToString:@"connect"]) {
        [self connectToMQTTBroker];
    } else if ([opcode isEqualToString:@"disconnect"]) {
        [self disconnectFromMQTTBroker];
    } else if ([opcode isEqualToString:@"publish"]) {
        
        if (!self.isConnected) {
            [self connectToMQTTBroker];
        } else {
            NSString *payload = [message objectForKey:@"payload"];
            NSString *topic = [message objectForKey:@"topic"];
            
            BOOL sticky = [[message objectForKey:@"retain"] boolValue];
            
            [self publishString:payload onTopic:topic retain:sticky];
        }
    }
}

@end
