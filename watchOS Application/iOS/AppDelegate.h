//
//  AppDelegate.h
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "MRTBluetoothMonitor.h"

@interface AppDelegate : UIResponder <UIApplicationDelegate, MRTBluetoothMonitorDelegate>

@property (strong, nonatomic) UIWindow *window;


@end

