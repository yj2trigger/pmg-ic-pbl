from __future__ import annotations

import asyncio
import os
import tempfile
import threading

import edge_tts
import pygame


class VoiceService:
    VOICE = "ko-KR-SunHiNeural"

    def __init__(self) -> None:
        pygame.mixer.init()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def speak(self, text: str) -> None:
        pygame.mixer.music.stop()
        asyncio.run_coroutine_threadsafe(self._generate_and_play(text), self._loop)

    def stop(self) -> None:
        pygame.mixer.music.stop()

    async def _generate_and_play(self, text: str) -> None:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tmp = f.name
        try:
            await edge_tts.Communicate(text, self.VOICE).save(tmp)
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass