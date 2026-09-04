#include <iostream>
#include <string>
#include <cstdlib>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/rfcomm.h>

class BluetoothCameraScanner {
public:
    void scanAndConnect() {
        std::cout << "Scanning for nearby Bluetooth cameras...\n";

        int dev_id = hci_get_route(NULL);
        if (dev_id < 0) {
            std::cerr << "Error: No active Bluetooth adapter found.\n";
            return;
        }

        int sock = hci_open_dev(dev_id);
        if (sock < 0) {
            std::cerr << "Error: Could not open socket to Bluetooth adapter.\n";
            return;
        }

        // Set up inquiry parameters for scanning
        inquiry_info *iinfo = NULL;
        int max_rsp = 255;
        int num_rsp;
        
        // Inquire for 8 seconds
        int len = 8; 
        int flags = IREQ_CACHE_FLUSH;
        
        iinfo = (inquiry_info*)malloc(max_rsp * sizeof(inquiry_info));
        num_rsp = hci_inquiry(dev_id, len, max_rsp, NULL, &iinfo, flags);

        if (num_rsp < 0) {
            std::cerr << "Bluetooth inquiry failed.\n";
            free(iinfo);
            close(sock);
            return;
        }

        char addr[19] = {0};
        char name[248] = {0};
        bool cameraFound = false;

        for (int i = 0; i < num_rsp; i++) {
            ba2str(&(iinfo[i].bdaddr), addr);
            
            // Read remote device name
            memset(name, 0, sizeof(name));
            if (hci_read_remote_name(sock, &(iinfo[i].bdaddr), sizeof(name), name, 0) < 0) {
                snprintf(name, sizeof(name), "[Unknown Device]");
            }

            std::cout << "Discovered: " << name << " [" << addr << "]\n";

            // Automatically target devices identifying as cameras or specific field gear
            std::string deviceName(name);
            if (deviceName.find("Camera") != std::string::npos || deviceName.find("Cam") != std::string::npos) {
                std::cout << "Target camera detected! Attempting automatic pairing and connection...\n";
                establishConnection(addr);
                cameraFound = true;
                break;
            }
        }

        if (!cameraFound) {
            std::cout << "No compatible Bluetooth cameras found in range.\n";
        }

        free(iinfo);
        close(sock);
    }

private:
    void establishConnection(const char* targetAddress) {
        struct sockaddr_rc addr = { 0 };
        int s, status;

        // Allocate a socket
        s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM);

        // Set connection parameters (channel 1 is standard for serial/control streams)
        addr.rc_family = AF_BLUETOOTH;
        addr.rc_channel = (uint8_t)1;
        str2ba(targetAddress, &addr.rc_bdaddr);

        // Connect to the camera device
        status = connect(s, (struct sockaddr*)&addr, sizeof(addr));

        if (status == 0) {
            std::cout << "Successfully connected to camera at " << targetAddress << "\n";
            // Send initial handshake or data stream command
            std::string handshake = "INIT_EVIDENCE_STREAM\n";
            write(s, handshake.c_str(), handshake.size());
        } else {
            std::cerr << "Failed to connect to camera. Error code: " << status << "\n";
        }

        close(s);
    }
};

int main() {
    BluetoothCameraScanner scanner;
    scanner.scanAndConnect();
    return 0;
}
