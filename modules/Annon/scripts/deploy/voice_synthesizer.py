import os
from TTS.api import TTS

class AnnonVoiceSynthesizer:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2"):
        print(f"Loading Annon AI Voice Engine: {model_name}...")
        self.tts = TTS(model_name=model_name, progress_bar=False, gpu=True)

    def generate_emotional_speech(self, text_to_say: str, emotion: str, output_path: str, language: str = "en"):
        """
        Synthesizes speech and simulates human emotion by mapping to specific 
        emotional reference voice samples or adjusting text cues.
        
        :param text_to_say: The dynamic text the AI needs to output.
        :param emotion: The emotional state ('neutral', 'urgent', 'authoritative', 'calm').
        :param output_path: Destination path for the synthesized .wav file.
        """
        # Map emotional states to specific reference voice samples
        emotion_samples = {
            "neutral": "modules/Annon/wav/voice_samples.wav",
            "urgent": "modules/Annon/wav/urgent_sample.wav",
            "authoritative": "modules/Annon/wav/authoritative_sample.wav",
            "calm": "modules/Annon/wav/calm_sample.wav"
        }
        
        speaker_wav_path = emotion_samples.get(emotion, emotion_samples["neutral"])
        
        if not os.path.exists(speaker_wav_path):
            print(f"Warning: Reference sample for '{emotion}' not found at {speaker_wav_path}. Falling back to default.")
            speaker_wav_path = "modules/Annon/wav/voice_samples.wav"

        print(f"Synthesizing '{emotion}' speech for Annon...")
        
        # Perform synthesis using the emotion-mapped voice vector
        self.tts.tts_to_file(
            text=text_to_say,
            speaker_wav=speaker_wav_path,
            language=language,
            file_path=output_path
        )
        
        print(f"Emotional voice output compiled to: {output_path}")
        return output_path

if __name__ == "__main__":
    synthesizer = AnnonVoiceSynthesizer()
    
    output_audio = "modules/Annon/logs/results/anon_response_output.wav"
    
    # Example: Generating an urgent security alert response
    response_text = "Warning! Perimeter breach detected in sector four. Immediate action required!"
    # synthesizer.generate_emotional_speech(response_text, emotion="urgent", output_path=output_audio)
