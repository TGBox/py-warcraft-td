"""Procedural sound synthesizer and audio manager for Element TD.

Generates real-time sound effects using NumPy and pygame.mixer with zero external audio assets.
Gracefully handles headless environments or systems without audio devices.
"""

import math
import numpy as np
from typing import Dict, Optional

try:
    import pygame
    import pygame.mixer
    MIXER_AVAILABLE = True
except ImportError:
    MIXER_AVAILABLE = False


SAMPLE_RATE = 44100


def _to_stereo_sound(samples: np.ndarray) -> Optional["pygame.mixer.Sound"]:
    """Convert float32 [-1.0, 1.0] samples to a 16-bit stereo pygame.mixer.Sound."""
    if not MIXER_AVAILABLE or not pygame.mixer.get_init():
        return None
    try:
        # Clip to [-1.0, 1.0] and convert to 16-bit PCM
        samples = np.clip(samples, -1.0, 1.0)
        pcm_16 = (samples * 32767).astype(np.int16)
        # Duplicate to stereo (N, 2)
        stereo_pcm = np.column_stack((pcm_16, pcm_16))
        return pygame.mixer.Sound(buffer=stereo_pcm.tobytes())
    except Exception:
        return None


def _synth_tone(freq: float, duration: float, decay: float = 4.0) -> np.ndarray:
    """Generate a simple sine tone with exponential decay."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)
    envelope = np.exp(-decay * t)
    wave = np.sin(2 * np.pi * freq * t) * envelope
    return wave.astype(np.float32)


def _synth_pitch_bend(f_start: float, f_end: float, duration: float, decay: float = 3.0) -> np.ndarray:
    """Generate a frequency sweep with exponential decay envelope."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)
    # Instantaneous frequency linearly interpolates
    freq = np.linspace(f_start, f_end, n_samples)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    envelope = np.exp(-decay * t)
    wave = np.sin(phase) * envelope
    return wave.astype(np.float32)


def _synth_fm(f_carrier: float, f_mod: float, mod_idx: float, duration: float, decay: float = 4.0) -> np.ndarray:
    """Frequency modulation synthesis."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)
    modulator = mod_idx * np.sin(2 * np.pi * f_mod * t)
    carrier = np.sin(2 * np.pi * f_carrier * t + modulator)
    envelope = np.exp(-decay * t)
    wave = carrier * envelope
    return wave.astype(np.float32)


def _synth_noise(duration: float, decay: float = 6.0, tone_mix: float = 0.0, tone_f: float = 200.0) -> np.ndarray:
    """White noise burst with optional low tone resonance."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)
    noise = np.random.uniform(-1.0, 1.0, n_samples)
    if tone_mix > 0.0:
        tone = np.sin(2 * np.pi * tone_f * t)
        noise = (1.0 - tone_mix) * noise + tone_mix * tone
    envelope = np.exp(-decay * t)
    wave = noise * envelope
    return wave.astype(np.float32)


def _synth_chord(freqs: list[float], duration: float, decay: float = 2.0) -> np.ndarray:
    """Synthesize a musical chord from a list of frequencies."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave = np.zeros(n_samples, dtype=np.float32)
    envelope = np.exp(-decay * t)
    for f in freqs:
        wave += np.sin(2 * np.pi * f * t)
    wave = (wave / len(freqs)) * envelope
    return wave.astype(np.float32)


def _synth_arpeggio(freqs: list[float], note_duration: float = 0.08) -> np.ndarray:
    """Synthesize an ascending sequence of notes."""
    chunks = []
    for f in freqs:
        chunks.append(_synth_tone(f, note_duration, decay=6.0))
    return np.concatenate(chunks).astype(np.float32)


class AudioManager:
    """Manages procedural sound generation and playback."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.sounds: Dict[str, Optional["pygame.mixer.Sound"]] = {}
        self._init_audio()

    def _init_audio(self) -> None:
        if not MIXER_AVAILABLE or not self.enabled:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=1024)
            self._generate_catalog()
        except Exception as e:
            # Fallback for systems without audio drivers
            print(f"[AudioManager] Audio mixer init failed ({e}), continuing silently.")
            self.enabled = False

    def _generate_catalog(self) -> None:
        """Pre-cache procedural sounds."""
        # 1. UI Click
        self.sounds["ui_click"] = _to_stereo_sound(_synth_tone(880.0, 0.04, decay=12.0))

        # 2. Tower Attacks
        self.sounds["arrow_shot"] = _to_stereo_sound(_synth_pitch_bend(750.0, 300.0, 0.12, decay=10.0))
        self.sounds["cannon_shot"] = _to_stereo_sound(_synth_noise(0.28, decay=8.0, tone_mix=0.5, tone_f=85.0))
        self.sounds["light_beam"] = _to_stereo_sound(_synth_pitch_bend(1200.0, 800.0, 0.18, decay=6.0))
        self.sounds["dark_pulse"] = _to_stereo_sound(_synth_fm(110.0, 55.0, 3.5, 0.25, decay=6.0))
        self.sounds["water_splash"] = _to_stereo_sound(_synth_pitch_bend(350.0, 650.0, 0.20, decay=7.0))
        self.sounds["fire_blast"] = _to_stereo_sound(_synth_noise(0.22, decay=9.0, tone_mix=0.3, tone_f=160.0))
        self.sounds["nature_shot"] = _to_stereo_sound(_synth_pitch_bend(440.0, 580.0, 0.16, decay=7.0))
        self.sounds["earth_slam"] = _to_stereo_sound(_synth_noise(0.30, decay=7.0, tone_mix=0.6, tone_f=65.0))

        # 3. Special / Combined Effects
        self.sounds["electric_zap"] = _to_stereo_sound(_synth_fm(440.0, 180.0, 6.0, 0.18, decay=8.0))
        self.sounds["ice_freeze"] = _to_stereo_sound(_synth_chord([1046.5, 1318.5, 1567.9], 0.24, decay=6.0))
        self.sounds["laser"] = _to_stereo_sound(_synth_pitch_bend(1800.0, 300.0, 0.14, decay=12.0))

        # 4. Economy & Game Events
        # Gold Interest: C5 - E5 - G5 - C6 arpeggio
        self.sounds["gold_interest"] = _to_stereo_sound(_synth_arpeggio([523.25, 659.25, 783.99, 1046.50], 0.07))
        self.sounds["creep_death"] = _to_stereo_sound(_synth_pitch_bend(280.0, 90.0, 0.10, decay=12.0))
        self.sounds["life_lost"] = _to_stereo_sound(_synth_chord([220.0, 233.08], 0.35, decay=4.0)) # Dissonant minor 2nd alarm

        # 5. Guardian Summon & Fanfares
        self.sounds["guardian_summon"] = _to_stereo_sound(_synth_chord([130.81, 196.00, 261.63, 392.00], 0.65, decay=2.5))
        self.sounds["victory"] = _to_stereo_sound(_synth_arpeggio([392.0, 523.25, 659.25, 783.99, 1046.50], 0.12))
        self.sounds["game_over"] = _to_stereo_sound(_synth_pitch_bend(440.0, 110.0, 0.8, decay=2.0))

    def play(self, sound_name: str, volume: float = 0.5) -> None:
        """Play a cached procedural sound with specified volume (0.0 to 1.0)."""
        if not self.enabled or sound_name not in self.sounds:
            return
        sound = self.sounds.get(sound_name)
        if sound is not None:
            try:
                sound.set_volume(max(0.0, min(1.0, volume)))
                sound.play()
            except Exception:
                pass
