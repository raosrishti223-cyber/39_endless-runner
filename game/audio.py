from array import array
import math

import pygame


class SoundEffects:
    def __init__(self):
        self._sounds = {}
        self._disabled = False

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

            mixer_format = pygame.mixer.get_init()
            if mixer_format is None or mixer_format[1] != -16:
                self._disable("the active mixer does not use signed 16-bit audio")
                return

            self._sounds = {
                "jump": self._make_tone(500, 850, 0.12),
                "score": self._make_tone(950, 1200, 0.1),
                "game_over": self._make_tone(420, 150, 0.35),
            }
        except pygame.error as error:
            self._disable(str(error))

    def _make_tone(self, start_frequency, end_frequency, duration):
        sample_rate, _, channels = pygame.mixer.get_init()
        sample_count = int(sample_rate * duration)
        samples = array("h")

        for index in range(sample_count):
            progress = index / sample_count
            frequency = start_frequency + (end_frequency - start_frequency) * progress
            fade_in = min(1.0, index / (sample_rate * 0.01))
            fade_out = min(1.0, (sample_count - index) / (sample_rate * 0.03))
            amplitude = int(
                12000
                * fade_in
                * fade_out
                * math.sin(2 * math.pi * frequency * index / sample_rate)
            )
            for _ in range(channels):
                samples.append(amplitude)

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _disable(self, reason):
        self._sounds.clear()
        self._disabled = True
        print(f"Sound effects disabled: {reason}")

    def play(self, effect):
        if self._disabled:
            return

        sound = self._sounds.get(effect)
        if sound is None:
            return

        try:
            sound.play()
        except pygame.error as error:
            self._disable(str(error))
