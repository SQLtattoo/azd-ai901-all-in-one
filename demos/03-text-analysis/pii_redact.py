"""
Module 3 (Part B) — Detect and redact PII / financial information.

Sends a customer message to the same Foundry chat model and asks it to return
the text with any personal or financial data masked (e.g. [EMAIL], [ACCOUNT_NUMBER]),
plus a list of what it found. Shows text analysis used for data protection.

Run:
    python demos/03-text-analysis/pii_redact.py
    python demos/03-text-analysis/pii_redact.py "My card 4111 1111 1111 1111 was charged twice."
"""
import json
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
CHAT_DEPLOYMENT = os.getenv("CHAT_DEPLOYMENT", "gpt-5.1")

SAMPLE = (
    "Hi, this is Jordan Alvarez. My account 1234567890 is showing the wrong balance "
    "of $84,250.13. You can reach me at jordan.alvarez@example.com or +1 (415) 555-0132. "
    "My card 4111 1111 1111 1111 was also charged twice this month."
)

INSTRUCTIONS = (
    "You are a data-protection filter for a bank. Find every piece of personally "
    "identifiable information (PII) and financial information in the user's text: "
    "names, email addresses, phone numbers, postal addresses, national IDs, "
    "account numbers, card numbers, IBAN/sort codes, and monetary balances. "
    "Return ONLY compact JSON with keys: "
    "redacted_text (the original text with each sensitive span replaced by an "
    "uppercase tag in square brackets, e.g. [NAME], [EMAIL], [ACCOUNT_NUMBER], "
    "[CARD_NUMBER], [PHONE], [AMOUNT]), and "
    "entities (array of {category, masked} where masked shows only the last 2-4 "
    "characters, e.g. '****0132'). Do not add commentary."
)


def main():
    text = " ".join(sys.argv[1:]).strip() or SAMPLE

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")

    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()

    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content

    print("Original:\n ", text, "\n")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(raw)
        return

    print("Redacted:\n ", data.get("redacted_text", "(none)"), "\n")
    entities = data.get("entities", [])
    if entities:
        print("Detected:")
        for e in entities:
            print(f"  - {e.get('category', '?'):<16} {e.get('masked', '')}")


if __name__ == "__main__":
    main()
