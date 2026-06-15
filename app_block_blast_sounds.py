"\"\"\"Procedurally generated 8-bit style sound effects.

Generating the audio in code means the repo stays tiny – there are no
WAV files to ship.  If numpy or the audio device is unavailable we
silently fall back to a no-op so the game still runs.
\"\"\"

import numpy as np
import pygame


class SoundFX:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sounds = {}
        if not enabled:
            return
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
            self._build_library()
        except pygame.error:
            # No audio device (e.g. CI / headless) – disable gracefully.
            self.enabled = False

    # ------------------------------------------------------------------
    # Synthesis helpers
    # ------------------------------------------------------------------
    def _tone(self, freq, ms, volume=0.4, shape=\"square\", decay=True):
        \"\"\"Build a single tone as a pygame Sound from a numpy buffer.\"\"\"
        rate = 44100
        n = int(rate * ms / 1000)
        t = np.linspace(0, ms / 1000, n, endpoint=False)
        if shape == \"square\":
            wave = np.sign(np.sin(2 * np.pi * freq * t))
        elif shape == \"saw\":
            wave = 2 * (t * freq - np.floor(0.5 + t * freq))
        else:  # sine
            wave = np.sin(2 * np.pi * freq * t)
        if decay:
            wave *= np.linspace(1.0, 0.0, n) ** 1.5
        audio = (wave * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)

    def _chord(self, freqs, ms, volume=0.35, shape=\"square\"):
        rate = 44100
        n = int(rate * ms / 1000)
        t = np.linspace(0, ms / 1000, n, endpoint=False)
        wave = np.zeros(n)
        for f in freqs:
            if shape == \"square\":
                wave += np.sign(np.sin(2 * np.pi * f * t))
            else:
                wave += np.sin(2 * np.pi * f * t)
        wave /= max(1, len(freqs))
        wave *= np.linspace(1.0, 0.0, n) ** 1.5
        audio = (wave * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(audio)

    def _build_library(self):
        self.sounds[\"place\"] = self._tone(440, 80, 0.35, \"square\")
        self.sounds[\"invalid\"] = self._tone(120, 120, 0.4, \"saw\")
        self.sounds[\"clear\"] = self._chord([523, 659, 784], 220, 0.4)
        self.sounds[\"combo\"] = self._chord([523, 659, 784, 988], 320, 0.45)
        self.sounds[\"levelup\"] = self._chord([659, 880, 1175], 400, 0.5)
        self.sounds[\"gameover\"] = self._chord([196, 165, 131], 600, 0.5, \"saw\")
        self.sounds[\"power\"] = self._chord([880, 1175, 1568], 260, 0.45)
        self.sounds[\"click\"] = self._tone(660, 40, 0.25, \"square\")

    # ------------------------------------------------------------------
    def play(self, name):
        if not self.enabled:
            return
        s = self.sounds.get(name)
        if s is not None:
            s.play()

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.stop()
"