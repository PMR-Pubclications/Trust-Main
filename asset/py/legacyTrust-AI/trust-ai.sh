pip install eth-account cryptography pydantic

pip install psycopg[binary] pydantic

pip install eth-account cryptography pydantic psycopg[binary]

pip install eth-account pydantic psycopg[binary]

pip install speechrecognition pyaudio edge-tts pygame

pip install faster-whisper pyaudio speechrecognition pygame

pip install piper-tts onnxruntime-gpu sounddevice numpy

# Create and activate a Python virtual environment
python3 -m venv piper_env
source piper_env/bin/activate

# Install PyTorch with CUDA support and Piper Training dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install piper-train

mkdir -p base_model
cd base_model

# Download a medium quality English base checkpoint (e.g., Lessac)
wget https://github.com/rhasspy/piper/releases/download/v0.1.0/model-en_US-lessac-medium.ckpt
wget https://github.com/rhasspy/piper/releases/download/v0.1.0/model-en_US-lessac-medium.ckpt.json


