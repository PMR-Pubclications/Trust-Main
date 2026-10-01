#include <sys/utsname.h>
#include <iostream>

void printKernelInfo() {
    struct utsname sysInfo;
    if (uname(&sysInfo) == 0) {
        std::cout << "Kernel OS Name: " << sysInfo.sysname << "\n";
        std::cout << "Kernel Release: " << sysInfo.release << "\n";
        std::cout << "Architecture:   " << sysInfo.machine << "\n";
    }
}
