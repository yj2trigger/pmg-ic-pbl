# ──────────────────────────────────────────────────────────────────────────────
# voice_service.py — TTS 서비스 (edge-tts + pygame, 백그라운드 실행)
# [역할]  텍스트를 한국어 음성으로 변환해 비동기 재생. GUI 블로킹 없음.
# [선택 섹션]
#   - asyncio 이벤트 루프를 별도 데몬 스레드에서 영구 실행 → speak() 는 fire-and-forget
#   - 임시 mp3 파일 생성 → 재생 완료 후 자동 삭제
# [의존성]
#   import  : edge_tts (MS Azure TTS), pygame.mixer, asyncio, threading, tempfile
#   사용하는 곳 : main_window.py → 화면 전환 이벤트에서 speak() / stop() 호출
# ──────────────────────────────────────────────────────────────────────────────
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
        # 이벤트 루프를 데몬 스레드에서 시작. 앱 종료 시 자동 소멸.
        pygame.mixer.init()
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def speak(self, text: str) -> None:
        # 현재 재생 즉시 중단 후 새 음성 비동기 시작. 호출: main_window.py.
        # 경계: 연속 호출 시 이전 음성은 잘리고 새 음성으로 교체됨.
        pygame.mixer.music.stop()
        asyncio.run_coroutine_threadsafe(self._generate_and_play(text), self._loop)

    def stop(self) -> None:
        # 현재 재생 중인 음성 즉시 중단. 호출: main_window.py (화면 이탈 등).
        pygame.mixer.music.stop()

    async def _generate_and_play(self, text: str) -> None:
        # edge-tts 로 mp3 생성 → pygame 재생 → 재생 완료 후 임시 파일 삭제.
        # finally 에서 삭제하므로 재생 중 예외 발생해도 임시 파일 잔류 방지.
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