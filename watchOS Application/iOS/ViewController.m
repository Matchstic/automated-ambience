//
//  ViewController.m
//  MRT-CW2-Watch
//
//  Created by Matt Clarke on 20/03/2018.
//  Copyright © 2018 Matt Clarke. All rights reserved.
//

#import "ViewController.h"

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    
    [self _registerNotifications];
    
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        [self _bpmAnimation];
    });
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)_bpmAnimation {
    if (self.currentBPM > 0) {
        double timestamp_now = CACurrentMediaTime();
        
        CGFloat beats_per_second = (CGFloat)self.currentBPM / 60.0;
        
        CGFloat scale = (sinf(M_PI * 2.0 * timestamp_now * beats_per_second) + 1.0) / 8.0;
        scale += 0.75;
        
        dispatch_async(dispatch_get_main_queue(), ^{
            self.heartOutputImageView.transform = CGAffineTransformMakeScale(scale, scale);
        });
    }
    
    // Loop
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        [self _bpmAnimation];
    });
}

- (void)_registerNotifications {
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(_onWatchConnected:) name:@"com.matchstic.mrt-cw2/watchConnected" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(_onWatchDisconnected:) name:@"com.matchstic.mrt-cw2/watchDisconnected" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(_onMQTTConnected:) name:@"com.matchstic.mrt-cw2/mqttConnected" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(_onNewData:) name:@"com.matchstic.mrt-cw2/newData" object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(_onBluetoothChanged:) name:@"com.matchstic.mrt-cw2/bluetoothChanged" object:nil];
}

- (void)_onWatchConnected:(NSNotification*)notification {
    dispatch_async(dispatch_get_main_queue(), ^{
        self.watchConnectionLabel.text = @"Connected";
        self.watchConnectionLabel.textColor = [UIColor greenColor];
    });
}

- (void)_onWatchDisconnected:(NSNotification*)notification {
    dispatch_async(dispatch_get_main_queue(), ^{
        self.watchConnectionLabel.text = @"Disconnected";
        self.watchConnectionLabel.textColor = [UIColor redColor];
    });
}

- (void)_onNewData:(NSNotification*)notification {
    NSDictionary *data = notification.object;
    
    int bpm = [[data objectForKey:@"bpm"] intValue];
    int hrv = [[data objectForKey:@"hrv"] intValue];
    
    self.currentBPM = bpm;
    
    dispatch_async(dispatch_get_main_queue(), ^{
        self.bpmOutputLabel.text = [NSString stringWithFormat:@"%d bpm", bpm];
        self.hrvOutputLabel.text = [NSString stringWithFormat:@"%d ms", hrv];
    });
}

- (void)_onBluetoothChanged:(NSNotification*)notification {
    NSNumber *rssi = notification.object;
    
    dispatch_async(dispatch_get_main_queue(), ^{
        int integerRSSI = [rssi intValue];
        
        if (integerRSSI != INT_MAX) {
            self.bluetoothConnectionLabel.text = @"Visible";
            self.bluetoothConnectionLabel.textColor = [UIColor greenColor];
        } else {
            self.bluetoothConnectionLabel.text = @"Not visible";
            self.bluetoothConnectionLabel.textColor = [UIColor redColor];
        }
    });
}

- (void)_onMQTTConnected:(NSNotification*)notification {
    dispatch_async(dispatch_get_main_queue(), ^{
        self.mqttConnectionLabel.text = @"Connected";
        self.mqttConnectionLabel.textColor = [UIColor greenColor];
    });
}

@end
