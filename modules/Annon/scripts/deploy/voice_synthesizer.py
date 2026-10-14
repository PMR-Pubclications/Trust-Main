import os
import librosa
import soundfile as sf
from TTS.api import TTS

class AnnonVoiceSynthesizer:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        print(f"Loading Annon AI Voice Engine: {model_name}...")
        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=True)

    def _prepare_audio_source(self, audio_path: str) -> str:
        """
        Automatically handles both WAV and MP3 files. If an MP3 is provided, 
        it converts it to a compatible WAV format on the fly.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio source file not found at: {audio_path}")
            
        # Check if the file is an MP3
        if audio_path.lower().endswith('.mp3'):
            wav_converted_path = audio_path.rsplit(".", 1)[0] + "_converted.wav"
            if not os.path.exists(wav_converted_path):
                print(f"Converting MP3 reference to compatible WAV format: {audio_path}...")
                # Load audio and resample to 22050Hz optimal for voice cloning
                y, sr = librosa.load(audio_path, sr=22050)
                sf.write(wav_converted_path, y, sr)
            return wav_converted_path
            
        return audio_path

    def generate_emotional_speech(self, text_to_say: str, emotion: str, output_path: str, language: str = "en"):
        """
        Synthesizes speech using MP3 or WAV reference voice files mapped to emotions.
        """
        # You can now use .mp3 files here instead of just .wav files!
        emotion_sources = {
            "neutral": "modules/Annon/wav/voice_samples.mp3", # Can be .mp3 or .wav
            "urgent": "modules/Annon/wav/urgent_sample.mp3",
            "authoritative": "modules/Annon/wav/authoritative_sample.mp3",
            "calm": "modules/Annon/wav/calm_sample.mp3"
        }
        
        raw_source_path = emotion_sources.get(emotion, emotion_sources["neutral"])
        
        try:
            speaker_wav_path = self._prepare_audio_source(raw_source_path)
        except FileNotFoundError:
            print(f"Warning: Reference file for '{emotion}' not found. Falling back to default.")
            speaker_wav_path = self._prepare_audio_source("modules/Annon/wav/voice_samples.mp3")

        print(f"Synthesizing '{emotion}' speech for Annon...")
        
        self.tts.tts_to_file(
            text=text_to_say,
            speaker_wav=speaker_wav_path,
            language=language,
            file_path=output_path
        )
        
        print(f"Voice output compiled successfully to: {output_path}")
        return output_path

if __name__ == "__main__":
    synthesizer = AnnonVoiceSynthesizer()
    
    output_audio = "modules/Annon/logs/results/anon_response_output.wav"
    response_text = "Attention unit: system operational. Processing audio telemetry."
    
    # synthesizer.generate_emotional_speech(response_text, emotion="neutral", output_path=output_audio)
