//
//  AppDelegate.m
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "AppDelegate.h"
#import <HealthKit/HealthKit.h>
#import "MRTMQTTManager.h"

@interface AppDelegate ()

@property (nonatomic, strong) HKHealthStore *healthStore;
@property (nonatomic, strong) MRTMQTTManager *mqttManager;

@end

@implementation AppDelegate


- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions {
    // Override point for customization after application launch.
    self.healthStore = [[HKHealthStore alloc] init];
    self.mqttManager = [[MRTMQTTManager alloc] init];
    
    NSSet *readTypes = [NSSet setWithObjects:
                        [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRateVariabilitySDNN],
                        [HKObjectType quantityTypeForIdentifier:HKQuantityTypeIdentifierHeartRate],
                        nil];
    
    [self.healthStore requestAuthorizationToShareTypes:nil readTypes:readTypes completion:^(BOOL success, NSError *error) {
        if (error)
            NSLog(@"[HealthKit]: %@", error.localizedDescription);
    }];
    
    return YES;
}


- (void)applicationWillResignActive:(UIApplication *)application {
    // Sent when the application is about to move from active to inactive state. This can occur for certain types of temporary interruptions (such as an incoming phone call or SMS message) or when the user quits the application and it begins the transition to the background state.
    // Use this method to pause ongoing tasks, disable timers, and invalidate graphics rendering callbacks. Games should use this method to pause the game.
}


- (void)applicationDidEnterBackground:(UIApplication *)application {
    // Use this method to release shared resources, save user data, invalidate timers, and store enough application state information to restore your application to its current state in case it is terminated later.
    // If your application supports background execution, this method is called instead of applicationWillTerminate: when the user quits.
}


- (void)applicationWillEnterForeground:(UIApplication *)application {
    // Called as part of the transition from the background to the active state; here you can undo many of the changes made on entering the background.
}


- (void)applicationDidBecomeActive:(UIApplication *)application {
    // Restart any tasks that were paused (or not yet started) while the application was inactive. If the application was previously in the background, optionally refresh the user interface.
}


- (void)applicationWillTerminate:(UIApplication *)application {
    // Called when the application is about to terminate. Save data if appropriate. See also applicationDidEnterBackground:.
}

- (void)applicationShouldRequestHealthAuthorization:(UIApplication *)application{
    // Called when Apple Watch requests HealthKit authorisation
    [self.healthStore handleAuthorizationForExtensionWithCompletion:^(BOOL success, NSError * _Nullable error) {
        if (success) {
            
        } else {
            NSLog(@"AUTH ERROR: %@", error.localizedDescription);
        }
    }];
}

@end
