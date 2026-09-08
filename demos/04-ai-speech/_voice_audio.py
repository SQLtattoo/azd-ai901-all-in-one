"""
Tiny audio helpers for voice_live_chat.py (OPTIONAL Voice Live demo).

Captures microphone PCM16 and plays back the model's PCM16 audio using pyaudio.
Kept intentionally small — this is teaching code, not a production audio stack.

Requires the preview packages (not in requirements.txt by default):
    pip install azure-ai-voicelive[aiohttp] pyaudio
"""
import asyncio
import base64
import os
import threading
from array import array

SAMPLE_RATE = 24000  # Voice Live uses 24 kHz PCM16 mono
CHANNELS = 1
CHUNK = 1024
NOISE_GATE_THRESHOLD = int(os.getenv("VOICE_LIVE_NOISE_GATE_THRESHOLD", "500"))
NOISE_GATE_RELEASE_CHUNKS = 3


class AudioPlayer:
    """Plays PCM16 audio deltas; stop() supports barge-in (cut playback)."""

    def __init__(self):
        import pyaudio

        self._pa = pyaudio.PyAudio()
        self._buffer = bytearray()
        self._buffer_lock = threading.Lock()
        self._noise_gate_release = 0
        self._pa_continue = pyaudio.paContinue
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            output=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._on_audio_requested,
        )

    def play(self, pcm16_bytes: bytes) -> None:
        with self._buffer_lock:
            self._buffer.extend(pcm16_bytes)

    def _on_audio_requested(self, _input_data, frame_count, _time_info, _status_flags):
        byte_count = frame_count * CHANNELS * 2
        with self._buffer_lock:
            audio = bytes(self._buffer[:byte_count])
            del self._buffer[:byte_count]
        audio = audio.ljust(byte_count, b"\x00")

        samples = array("h", audio)
        peak = max((abs(sample) for sample in samples), default=0)
        if peak >= NOISE_GATE_THRESHOLD:
            self._noise_gate_release = NOISE_GATE_RELEASE_CHUNKS
        elif self._noise_gate_release:
            self._noise_gate_release -= 1
        else:
            audio = b"\x00" * byte_count

        return audio, self._pa_continue

    def stop(self) -> None:
        # Drop any buffered audio so the user can interrupt the model.
        with self._buffer_lock:
            self._buffer.clear()
        self._noise_gate_release = 0

    def close(self) -> None:
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()


class MicStreamer:
    """Streams microphone PCM16 frames into the Voice Live connection."""

    def __init__(self, connection):
        import pyaudio

        self._connection = connection
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        self._task = None

    async def start(self) -> None:
        self._task = asyncio.create_task(self._pump())

    async def _pump(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            data = await loop.run_in_executor(
                None, self._stream.read, CHUNK, False
            )
            # Voice Live expects base64-encoded PCM16 audio.
            audio_b64 = base64.b64encode(data).decode("ascii")
            await self._connection.input_audio_buffer.append(audio=audio_b64)

    def close(self) -> None:
        if self._task:
            self._task.cancel()
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()
