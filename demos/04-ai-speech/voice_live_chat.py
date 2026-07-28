"""
Module 4 (OPTIONAL) — Real-time voice with the Azure Speech Voice Live SDK.

Unlike speech_chat.py (separate STT -> model -> TTS calls, turn-based), Voice Live
is a single real-time, bidirectional speech-to-speech session: audio streams in
and out over one connection, with built-in turn detection and barge-in (you can
interrupt mid-sentence). You don't stitch STT + LLM + TTS yourself.

This is an OPTIONAL, PREVIEW demo. It needs a microphone + speakers and two extra
packages that are NOT in requirements.txt by default:

    pip install "azure-ai-voicelive[aiohttp]" pyaudio

Run:
    python demos/04-ai-speech/voice_live_chat.py
    # speak; press Ctrl+C to stop.
"""
import asyncio
import base64
import os
import signal
import sys

from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
VOICE_LIVE_ENDPOINT = os.getenv("VOICE_LIVE_ENDPOINT") or PROJECT_ENDPOINT
VOICE_LIVE_MODEL = os.getenv("VOICE_LIVE_MODEL", "gpt-realtime")
VOICE_NAME = os.getenv("VOICE_LIVE_VOICE", "en-US-AvaMultilingualNeural")

INSTRUCTIONS = (
    "You are Aria, a warm, concise voice concierge for Contoso Private Bank. "
    "Answer in one or two spoken-friendly sentences. General information only; "
    "defer decisions to a licensed advisor."
)


async def run():
    # Imported lazily so the rest of Module 4 works without the preview packages.
    from azure.ai.voicelive.aio import connect
    from azure.ai.voicelive.models import (
        AudioEchoCancellation,
        AudioNoiseReduction,
        AzureStandardVoice,
        InputAudioFormat,
        Modality,
        OutputAudioFormat,
        RequestSession,
        ServerVad,
    )
    from azure.identity.aio import DefaultAzureCredential

    from _voice_audio import AudioPlayer, MicStreamer  # tiny local helper (pyaudio)

    credential = DefaultAzureCredential()

    # One websocket session carries audio both ways.
    async with connect(
        endpoint=VOICE_LIVE_ENDPOINT,
        credential=credential,
        model=VOICE_LIVE_MODEL,
    ) as connection:
        # Configure the session: speech in, audio+text out, server-side turn
        # detection (this is what gives natural turn-taking and barge-in).
        session = RequestSession(
            modalities=[Modality.TEXT, Modality.AUDIO],
            instructions=INSTRUCTIONS,
            voice=AzureStandardVoice(name=VOICE_NAME),
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,
            turn_detection=ServerVad(threshold=0.5, prefix_padding_ms=300, silence_duration_ms=500),
            input_audio_echo_cancellation=AudioEchoCancellation(),
            input_audio_noise_reduction=AudioNoiseReduction(),
        )
        await connection.session.update(session=session)

        player = AudioPlayer()
        mic = MicStreamer(connection)
        print("Voice Live session ready — speak now (Ctrl+C to stop).")
        await mic.start()

        # Pump server events: play audio deltas, handle barge-in, print text.
        async for event in connection:
            etype = event.type
            if etype == "response.audio.delta":
                # delta is base64-encoded PCM16 audio.
                player.play(base64.b64decode(event.delta))
            elif etype == "input_audio_buffer.speech_started":
                player.stop()  # barge-in: user started talking, cut playback
            elif etype == "response.audio_transcript.done":
                print(f"aria > {event.transcript}")
            elif etype == "error":
                print(f"error > {event.error}", file=sys.stderr)


def main():
    if not VOICE_LIVE_ENDPOINT:
        sys.exit("VOICE_LIVE_ENDPOINT (or FOUNDRY_PROJECT_ENDPOINT) is not set. Fill in .env and run `az login`.")
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nStopped.")
    except ModuleNotFoundError as e:
        sys.exit(
            f"Missing preview dependency: {e.name}. "
            'Install with: pip install "azure-ai-voicelive[aiohttp]" pyaudio'
        )


if __name__ == "__main__":
    # Ctrl+C should exit cleanly on Windows too.
    signal.signal(signal.SIGINT, signal.default_int_handler)
    main()
