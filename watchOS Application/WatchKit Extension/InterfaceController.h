//
//  InterfaceController.h
//  MRT-CW2-Watch WatchKit Extension
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <WatchKit/WatchKit.h>
#import <Foundation/Foundation.h>

@interface InterfaceController : WKInterfaceController

@property (strong, nonatomic) IBOutlet WKInterfaceButton *startStopButton;
@property (strong, nonatomic) IBOutlet WKInterfaceLabel *bpmLabel;
@property (strong, nonatomic) IBOutlet WKInterfaceLabel *hrvLabel;
@property (strong, nonatomic) IBOutlet WKInterfaceLabel *proximityLabel;

@property (strong, nonatomic) IBOutlet WKInterfaceSwitch *heartFeedbackSwitch;

@end
