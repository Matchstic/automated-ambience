//
//  MRTMQTTManager.h
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 01/05/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "../include/MQTTKit.h"
#import <WatchConnectivity/WatchConnectivity.h>

@interface MRTMQTTManager : NSObject <WCSessionDelegate>

@property (nonatomic, strong) MQTTClient *client;
@property (nonatomic, strong) WCSession *watchSession;
@property (nonatomic, readwrite) BOOL isConnected;

- (void)connectToMQTTBroker;
- (void)disconnectFromMQTTBroker;

- (void)publishString:(NSString*)payload onTopic:(NSString*)topic retain:(BOOL)retain;

@end
