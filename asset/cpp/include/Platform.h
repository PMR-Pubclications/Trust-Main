#pragma once

#if defined(__ANDROID__)
    #define PLATFORM_ANDROID 1
    #define OS_NAME "Android"
#elif defined(__APPLE__)
    #include <TargetConditionals.h>
    #if TARGET_OS_IPHONE || TARGET_OS_IOS
        #define PLATFORM_IOS 1
        #define OS_NAME "iOS"
    #endif
#elif defined(__linux__)
    #define PLATFORM_LINUX 1
    #define OS_NAME "Linux"
#else
    #error "Unsupported target operating system."
#endif
