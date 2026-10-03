#include "AudioVideoEngine.h"

extern "C" {
    AudioVideoEngine* Engine_Create() { return new AudioVideoEngine(); }
    int Engine_Init(AudioVideoEngine* engine) { return engine->initializeHardware(); }
    void Engine_Destroy(AudioVideoEngine* engine) { delete engine; }
}
