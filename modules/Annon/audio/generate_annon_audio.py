import os
import math
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
from pydub.generators import WhiteNoise

# Directory output structure
OUTPUT_DIR = "modules/Annon/audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_light_wind_background(duration_ms: int) -> AudioSegment:
    """Generates a soft, non-rhythmic, low-pass filtered wind background."""
    # Generate white noise at low volume (-35 dB)
    noise = WhiteNoise().to_audio_segment(duration=duration_ms, volume=-35.0)
    
    # Low-pass filter to simulate gentle wind/ambient air (cutoff ~400 Hz)
    wind = noise.low_pass_filter(400)
    
    # Apply fade in and fade out for smooth loop transitions
    wind = wind.fade_in(500).fade_out(500)
    return wind


def create_spoken_track(text: str, output_path: str, speed_factor: float = 1.0):
    """
    Synthesizes speech to MP3, adjusts playback speed, and overlays soft wind background.
    """
    temp_speech_path = output_path.replace(".mp3", "_temp.mp3")
    
    # 1. Synthesize text to speech
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(temp_speech_path)
    
    # 2. Load synthesized speech
    speech = AudioSegment.from_file(temp_speech_path)
    
    # 3. Adjust speech speed if requested (modifying frame rate)
    if speed_factor != 1.0:
        new_frame_rate = int(speech.frame_rate * speed_factor)
        speech = speech._spawn(speech.raw_data, overrides={"frame_rate": new_frame_rate})
        speech = speech.set_frame_rate(44100)
    
    # Add brief silence padding (1 second start/end)
    silence = AudioSegment.silent(duration=1000)
    speech = silence + speech + silence
    
    # 4. Generate matching background wind layer
    wind = generate_light_wind_background(len(speech))
    
    # 5. Overlay speech over background (-2 dB on speech, -32 dB background)
    final_audio = wind.overlay(speech, position=0)
    
    # 6. Export to final MP3 target
    final_audio.export(output_path, format="mp3", bitrate="192k")
    
    # Clean up temp file
    if os.path.exists(temp_speech_path):
        os.remove(temp_speech_path)
        
    print(f"Successfully generated: {output_path}")


# Define emotion profiles and corresponding speech transcripts
audio_profiles = {
    "annon_response_output.mp3": {
        "speed": 1.0,
        "script": (
            "Annon status report. System online. Battery active, mesh link active, vault secure. "
            "Annon log evidence. Evidence logged and secured to local ledger. "
            "Annon finalize report. Report finalized. Hash compiled and signed."
        )
    },
    "calm_sample.mp3": {
        "speed": 0.95,  # Slightly slower, steady pacing
        "script": (
            "Good morning. Systems initializing. "
            "Annon, status report. System online. Battery active, mesh link active, vault secure. "
            "Annon, log vitals. Vitals recorded to ePCR entry. "
            "Annon, mark roadway clear. Roadway status set to clear. Telemetry updated."
        )
    },
    "authoritative_sample.mp3": {
        "speed": 1.0,  # Measured, firm, and clear
        "script": (
            "Annon, lockdown vault. Vault locked and encrypted. Immediate authentication required to access. "
            "Annon, initiate scene scan. 3D scene scanning in progress. Hold position. "
            "Annon, structural check. Structural integrity data logged."
        )
    },
    "urgent_sample.mp3": {
        "speed": 1.15,  # Faster, rapid delivery
        "script": (
            "Annon, trigger duress. Duress signal dispatched. Location telemetry locked. "
            "Annon, read hazmat placard. Hazmat placard analyzed. Safety protocol queued. "
            "Annon, scan hot spots. Hot spot analysis running. Thermal anomaly detected."
        )
    },
    "aggressive_sample.mp3": {
        "speed": 1.25,  # Forced, rapid, high-priority command delivery
        "script": (
            "WARNING. Security protocol breached. Lockdown sequence initiated immediately. "
            "Annon, trigger duress! Duress signal dispatched! Location telemetry locked! "
            "Annon, lockdown vault! Vault locked and encrypted! All terminal access revoked!"
        )
    }
}


if __name__ == "__main__":
    print("Generating Annon OS audio modules...")
    for filename, config in audio_profiles.items():
        target_file = os.path.join(OUTPUT_DIR, filename)
        create_spoken_track(
            text=config["script"],
            output_path=target_file,
            speed_factor=config["speed"]
        )
    print("\nAll audio tracks created in 'modules/Annon/audio/'.")
