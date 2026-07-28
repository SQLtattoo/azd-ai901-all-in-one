"""
Module 3 — Text analysis with a Foundry chat model.

Returns sentiment, key phrases, and entities as structured JSON from a single
prompt, showing that a multimodal model covers the classic text-analysis tasks.

Run:
    python demos/03-text-analysis/text_analysis.py
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
    "I booked the Contoso lakeside cabin for a weekend in Bend, Oregon. "
    "Check-in was slow and the wifi dropped constantly, but the views were stunning "
    "and the staff at the front desk were wonderful."
)

INSTRUCTIONS = (
    "You are a text-analytics engine. For the user's text, return ONLY compact JSON with keys: "
    'sentiment (one of positive/neutral/negative), confidence (0-1), '
    "key_phrases (array of strings), entities (array of {text, category}), "
    "summary (one sentence). Do not add commentary."
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
    print("Input:\n ", text, "\n")
    try:
        print(json.dumps(json.loads(raw), indent=2))
    except json.JSONDecodeError:
        print(raw)


if __name__ == "__main__":
    main()
