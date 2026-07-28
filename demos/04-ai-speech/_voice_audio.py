"""
Tiny audio helpers for voice_live_chat.py (OPTIONAL Voice Live demo).

Captures microphone PCM16 and plays back the model's PCM16 audio using pyaudio.
Kept intentionally small — this is teaching code, not a production audio stack.

Requires the preview packages (not in requirements.txt by default):
    pip install azure-ai-voicelive[aiohttp] pyaudio
"""
import asyncio
import base64

SAMPLE_RATE = 24000  # Voice Live uses 24 kHz PCM16 mono
CHANNELS = 1
CHUNK = 1024


class AudioPlayer:
    """Plays PCM16 audio deltas; stop() supports barge-in (cut playback)."""

    def __init__(self):
        import pyaudio

        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            output=True,
        )

    def play(self, pcm16_bytes: bytes) -> None:
        self._stream.write(pcm16_bytes)

    def stop(self) -> None:
        # Drop any buffered audio so the user can interrupt the model.
        self._stream.stop_stream()
        self._stream.start_stream()

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
