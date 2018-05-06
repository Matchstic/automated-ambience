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
        self._basestationIsVisible = YES;
        
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
                    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/mqttConnected" object:nil];
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
    [self.client publishString:payload toTopic:topic withQos:ExactlyOnce retain:retain completionHandler:^(int messageID) {
        // nop.
    }];
}

- (void)setBasestationIsVisible:(BOOL)basestationIsVisible {
    self._basestationIsVisible = basestationIsVisible;
}

////////////////////////////////////////////////////////////////////
// WCSession delegate
////////////////////////////////////////////////////////////////////

- (void)session:(nonnull WCSession *)session activationDidCompleteWithState:(WCSessionActivationState)activationState error:(nullable NSError *)error {
    if (error)
        NSLog(@"activation did complete with error: %@", error.localizedDescription);
}

- (void)sessionDidBecomeInactive:(nonnull WCSession *)session {
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/watchDisconnected" object:nil];
}

- (void)sessionDidDeactivate:(nonnull WCSession *)session {
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/watchDisconnected" object:nil];
}

- (void)session:(WCSession *)session didReceiveMessage:(NSDictionary<NSString *, id> *)message replyHandler:(void(^)(NSDictionary<NSString *, id> *replyMessage))replyHandler {
   
    NSLog(@"Recieved message: %@", message);
    [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/watchConnected" object:nil];
    
    NSString *opcode = [message objectForKey:@"opcode"];
    
    if ([opcode isEqualToString:@"connect"]) {
        [self connectToMQTTBroker];
    } else if ([opcode isEqualToString:@"disconnect"]) {
        [self disconnectFromMQTTBroker];
    } else if ([opcode isEqualToString:@"publish"]) {
        
        if (!self.isConnected) {
            [self connectToMQTTBroker];
        } else {
            
            // Pull data out of the message.
            NSString *payload = [message objectForKey:@"payload"];
            NSString *topic = [message objectForKey:@"topic"];
            
            if ([topic isEqualToString:@"data"]) {
                NSData *jsonData = [payload dataUsingEncoding:NSUTF8StringEncoding];
                NSError *error;
                
                NSMutableDictionary *parsedData = [[NSJSONSerialization JSONObjectWithData:jsonData options:kNilOptions error:&error] mutableCopy];
                
                [[NSNotificationCenter defaultCenter] postNotificationName:@"com.matchstic.mrt-cw2/newData" object:parsedData];
                
                // Now, we add the basestation_visible flag
                [parsedData setObject:[NSNumber numberWithBool:self._basestationIsVisible] forKey:@"basestation_visible"];
                
                jsonData = [NSJSONSerialization dataWithJSONObject:parsedData options:0 error:&error];
                payload = [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
            }

            BOOL sticky = [[message objectForKey:@"retain"] boolValue];
            
            [self publishString:payload onTopic:topic retain:sticky];
        }
    }
}

@end
