#!/usr/bin/env python3
import socket
import os
import time
import json
import numpy as np

# Attempt native pyboson import installed as local system package
try:
    import pyboson
    HAS_PYBOSON = True
except ImportError:
    HAS_PYBOSON = False

SOCKET_PATH = "/tmp/trust_first_responder.sock"

class FirstResponderDaemon:
    def __init__(self, device_path="/dev/video0"):
        self.device_path = device_path
        self.camera = pyboson.FlirBosonCamera(device_path) if HAS_PYBOSON else None
        
    def start_ipc_server(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(SOCKET_PATH)
        server.listen(5)
        print(f"[firstResponder] Daemon active on Unix Socket: {SOCKET_PATH}")

        if self.camera and self.camera.initialize():
            print(f"[firstResponder] FLIR Boson driver bound to {self.device_path}")
        else:
            print("[firstResponder] Running in synthetic fallback mode.")

        try:
            while True:
                conn, _ = server.accept()
                self._handle_client(conn)
        except KeyboardInterrupt:
            print("\n[firstResponder] Shutting down daemon...")
        finally:
            if self.camera:
                self.camera.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)

    def _handle_client(self, conn):
        try:
            # Capture frame or build synthetic 640x512 matrix
            frame = self.camera.get_next_frame() if self.camera else None
            if frame is None:
                frame = np.full((512, 640), 36.5, dtype=np.float32)

            # Compress radiometric matrix for streaming
            payload = {
                "timestamp": time.time(),
                "sensor": "FLIR_BOSON_640",
                "width": frame.shape[1],
                "height": frame.shape[0],
                "min_temp_c": float(np.min(frame)),
                "max_temp_c": float(np.max(frame)),
                "frame_flat": frame.tolist()  # Export radiometric array
            }
            
            data_bytes = json.dumps(payload).encode('utf-8')
            conn.sendall(len(data_bytes).to_bytes(4, byteorder='big') + data_bytes)
        except Exception as e:
            print(f"[firstResponder ERROR] {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    daemon = FirstResponderDaemon()
    daemon.start_ipc_server()
