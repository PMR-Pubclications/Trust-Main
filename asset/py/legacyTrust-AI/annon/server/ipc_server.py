from fastapi import FastAPI
import uvicorn
from annon import AnnonEngine

app = FastAPI(title="Annon Standalone Daemon")
engine = AnnonEngine()

@app.on_event("startup")
def startup_event():
    engine.initialize()

@app.get("/status")
def get_status():
    return {"status": "active" if engine._is_running else "offline"}

@app.post("/hardware/start")
def start_hardware():
    status = engine.hardware.start_capture()
    return {"capture_started": status}

@app.on_event("shutdown")
def shutdown_event():
    engine.shutdown()

def start_server():
    # Listens on local Unix socket or localhost port for Trust-Shell calls
    uvicorn.run(app, host="127.0.0.1", port=8443)

if __name__ == "__main__":
    start_server()
