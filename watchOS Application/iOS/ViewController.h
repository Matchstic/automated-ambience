//
//  ViewController.h
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface ViewController : UIViewController

@property (strong, nonatomic) IBOutlet UILabel *bluetoothConnectionLabel;
@property (strong, nonatomic) IBOutlet UILabel *mqttConnectionLabel;
@property (strong, nonatomic) IBOutlet UILabel *watchConnectionLabel;

@property (strong, nonatomic) IBOutlet UILabel *bpmOutputLabel;
@property (strong, nonatomic) IBOutlet UILabel *hrvOutputLabel;
@property (strong, nonatomic) IBOutlet UIImageView *heartOutputImageView;

@property (nonatomic, readwrite) int currentBPM;

@end

