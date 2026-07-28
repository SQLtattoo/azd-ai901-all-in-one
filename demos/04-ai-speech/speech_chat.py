"""
Module 4 — Speak to the model, hear it answer.

Pipeline: Azure Speech speech-to-text -> Foundry chat model -> Azure Speech
text-to-speech. Use --text to skip the microphone and demo synthesis only.

Run:
    python demos/04-ai-speech/speech_chat.py
    python demos/04-ai-speech/speech_chat.py --text "What is Azure AI Foundry?"
"""
import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
CHAT_DEPLOYMENT = os.getenv("CHAT_DEPLOYMENT", "gpt-5.1")
SPEECH_REGION = os.getenv("SPEECH_REGION", "eastus")
SPEECH_KEY = os.getenv("SPEECH_KEY")  # optional; keyless preferred
SPEECH_RESOURCE_ID = os.getenv("SPEECH_RESOURCE_ID")  # required for keyless (AAD)


def get_speech_config():
    import azure.cognitiveservices.speech as speechsdk

    if SPEECH_KEY:
        return speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

    # Keyless: AAD token from your az login identity for the Speech resource.
    # The Speech SDK expects the token as "aad#<resourceId>#<token>".
    if not SPEECH_RESOURCE_ID:
        sys.exit(
            "Keyless Speech needs SPEECH_RESOURCE_ID (the Cognitive Services account "
            "resource ID) in .env \u2014 or set SPEECH_KEY for a quick classroom demo."
        )
    from azure.identity import DefaultAzureCredential

    token = DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default")
    auth_token = f"aad#{SPEECH_RESOURCE_ID}#{token.token}"
    return speechsdk.SpeechConfig(auth_token=auth_token, region=SPEECH_REGION)


def recognize_from_mic():
    import azure.cognitiveservices.speech as speechsdk

    speech_config = get_speech_config()
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    print("Speak now...")
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"Speech recognition canceled: {details.reason}."
        if details.error_details:
            msg += f" {details.error_details}"
        sys.exit(msg)
    sys.exit(f"No speech recognized ({result.reason}).")


def ask_model(prompt):
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()
    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Answer in two short spoken-friendly sentences."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def speak(text):
    import azure.cognitiveservices.speech as speechsdk

    speech_config = get_speech_config()
    speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = f"Speech synthesis canceled: {details.reason}."
        if details.error_details:
            msg += f" {details.error_details}"
        sys.exit(msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Skip the mic and use this text as the prompt.")
    args = parser.parse_args()

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")

    prompt = args.text or recognize_from_mic()
    print(f"you said > {prompt}")

    answer = ask_model(prompt)
    print(f"model    > {answer}")
    speak(answer)


if __name__ == "__main__":
    main()
