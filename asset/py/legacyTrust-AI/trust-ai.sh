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

python3 -m piper_train.preprocess \
    --language en-us \
    --input-dir /path/to/custom_voice_dataset \
    --output-dir /path/to/preprocessed_data \
    --dataset-format ljspeech \
    --single-speaker \
    --sample-rate 22050

python3 -m piper_train \
    --dataset-dir /path/to/preprocessed_data \
    --accelerator gpu \
    --devices 1 \
    --batch-size 16 \
    --validation-split 0.05 \
    --num-test-examples 5 \
    --max_epochs 3000 \
    --resume_from_checkpoint /path/to/base_model/model-en_US-lessac-medium.ckpt \
    --checkpoint-epochs 100 \
    --output-dir /path/to/training_output


python3 -m piper_train.export_onnx \
    /path/to/training_output/checkpoints/epoch=2500-step=15000.ckpt \
    /path/to/custom_voice.onnx

python3 -m piper_train.make_config \
    --dataset-dir /path/to/preprocessed_data \
    --output-config /path/to/custom_voice.onnx.json


pip install faster-whisper pydub

pip install ffmpeg-python

g++ -O3 -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) \
    engine_wrapper.cpp -o audio_video_engine$(python3-config --extension-suffix)


docker compose up -d --build

pip install -e .


