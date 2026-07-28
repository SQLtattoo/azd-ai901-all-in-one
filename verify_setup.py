"""
verify_setup.py — pre-class connectivity check for the AI-901 demos.

Checks that:
  1. Required environment variables are set (.env loaded).
  2. Azure credentials work (az login / managed identity).
  3. The chat deployment answers a one-line prompt through the Foundry project.

Run:
    python verify_setup.py

Exit code 0 = ready to go. Non-zero = something to fix first.
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

CHECK = "[ OK ]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def check_env():
    """Verify the essential .env values are present."""
    required = {
        "FOUNDRY_PROJECT_ENDPOINT": os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        "CHAT_DEPLOYMENT": os.getenv("CHAT_DEPLOYMENT"),
    }
    optional = {
        "AGENT_NAME": os.getenv("AGENT_NAME"),
        "SPEECH_REGION": os.getenv("SPEECH_REGION"),
        "CONTENT_UNDERSTANDING_ENDPOINT": os.getenv("CONTENT_UNDERSTANDING_ENDPOINT"),
    }

    ok = True
    print("1) Environment variables")
    for name, value in required.items():
        if value and "<" not in value:
            print(f"   {CHECK} {name}")
        else:
            print(f"   {FAIL} {name} is missing or still a placeholder")
            ok = False
    for name, value in optional.items():
        state = CHECK if (value and "<" not in value) else WARN
        print(f"   {state} {name} (optional)")
    return ok


def check_credential():
    """Verify DefaultAzureCredential can obtain a token."""
    print("2) Azure credential (az login / managed identity)")
    try:
        from azure.identity import DefaultAzureCredential

        DefaultAzureCredential().get_token("https://ai.azure.com/.default")
        print(f"   {CHECK} Got an access token")
        return True
    except Exception as error:  # noqa: BLE001 - report any auth failure to the user
        print(f"   {FAIL} Could not get a token: {error}")
        print("        Fix: run `az login` in this terminal, then retry.")
        return False


def check_chat():
    """Verify the chat deployment responds through the Foundry project."""
    print("3) Chat deployment round-trip")
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    deployment = os.getenv("CHAT_DEPLOYMENT", "gpt-5.1")
    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.projects import AIProjectClient

        project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
        client = project.get_openai_client()
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Reply with the single word: ready"}],
            max_completion_tokens=256,
        )
        reply = (response.choices[0].message.content or "").strip()
        print(f"   {CHECK} Model '{deployment}' replied: {reply!r}")
        return True
    except Exception as error:  # noqa: BLE001 - surface the real error to the user
        print(f"   {FAIL} Chat call failed: {error}")
        print("        Check: deployment name matches the portal, and the project endpoint is correct.")
        return False


def main():
    print("AI-901 demo setup check\n" + "=" * 30)
    env_ok = check_env()
    if not env_ok:
        print("\nFix the .env values above, then re-run. Skipping live calls.")
        sys.exit(1)

    cred_ok = check_credential()
    chat_ok = check_chat() if cred_ok else False

    print("\n" + "=" * 30)
    if env_ok and cred_ok and chat_ok:
        print("READY — everything checks out. ✅")
        sys.exit(0)
    print("NOT READY — resolve the [FAIL] items above.")
    sys.exit(1)


if __name__ == "__main__":
    main()
