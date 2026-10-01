// PhoneMicSearcher.mm (Compile as Objective-C++)
#import <AVFoundation/AVFoundation.h>
#include <vector>
#include <string>
#include <iostream>

struct IOSMicrophone {
    std::string portName;
    std::string orientation; // "Front", "Back", "Bottom"
    std::string polarPattern; // "Omnidirectional", "Cardioid"
    void* dataSourceID;
};

class IOSMicSearcher {
public:
    static std::vector<IOSMicrophone> findPhoneMicrophones() {
        std::vector<IOSMicrophone> availableMics;
        
        AVAudioSession* session = [AVAudioSession sharedInstance];
        NSError* error = nil;
        [session setCategory:AVAudioSessionCategoryRecord error:&error];
        [session setActive:YES error:&error];

        // Retrieve available input ports
        NSArray<AVAudioSessionPortDescription*>* inputs = [session availableInputs];

        for (AVAudioSessionPortDescription* input in inputs) {
            if ([input.portType isEqualToString:AVAudioSessionPortBuiltInMic]) {
                
                // Inspect data sources (individual physical capsules)
                for (AVAudioSessionDataSourceDescription* source in input.dataSources) {
                    IOSMicrophone mic;
                    mic.portName = [input.portName UTF8String];
                    mic.dataSourceID = (__bridge void*)source.dataSourceID;

                    // Determine physical placement on phone
                    if ([source.orientation isEqualToString:AVAudioSessionOrientationFront]) {
                        mic.orientation = "Front (Screen Side)";
                    } else if ([source.orientation isEqualToString:AVAudioSessionOrientationBack]) {
                        mic.orientation = "Back (Camera Side)";
                    } else if ([source.orientation isEqualToString:AVAudioSessionOrientationBottom]) {
                        mic.orientation = "Bottom (Main Speaker Side)";
                    } else {
                        mic.orientation = "Unknown / Secondary";
                    }

                    // Determine polar pattern support
                    if ([source.selectedPolarPattern isEqualToString:AVAudioSessionPolarPatternCardioid]) {
                        mic.polarPattern = "Cardioid";
                    } else {
                        mic.polarPattern = "Omnidirectional";
                    }

                    availableMics.push_back(mic);
                }
            }
        }
        return availableMics;
    }
};
