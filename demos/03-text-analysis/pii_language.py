"""
Module 3 (Part C) — PII detection & redaction with the Azure AI Language service.

Uses the purpose-built Azure AI Language PII API (via azure-ai-textanalytics),
which returns a guaranteed `redacted_text` plus typed entities with confidence
scores. Contrast with Part B, which does the same job with the Foundry chat model.

Run:
    python demos/03-text-analysis/pii_language.py
    python demos/03-text-analysis/pii_language.py "Call me on +1 (415) 555-0132."
"""
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

LANGUAGE_ENDPOINT = os.getenv("LANGUAGE_ENDPOINT")

SAMPLE = (
    "Hi, this is Jordan Alvarez. My account 1234567890 is showing the wrong balance "
    "of $84,250.13. You can reach me at jordan.alvarez@example.com or +1 (415) 555-0132. "
    "My card 4111 1111 1111 1111 was also charged twice this month."
)


def main():
    text = " ".join(sys.argv[1:]).strip() or SAMPLE

    if not LANGUAGE_ENDPOINT:
        sys.exit(
            "LANGUAGE_ENDPOINT is not set. Add it to .env "
            "(https://<your-resource>.cognitiveservices.azure.com/) and run `az login`."
        )

    try:
        from azure.ai.textanalytics import TextAnalyticsClient
    except ModuleNotFoundError:
        sys.exit('azure-ai-textanalytics is not installed. Run: pip install "azure-ai-textanalytics>=5.3"')

    client = TextAnalyticsClient(endpoint=LANGUAGE_ENDPOINT, credential=DefaultAzureCredential())

    result = client.recognize_pii_entities([text], language="en")
    doc = result[0]
    if doc.is_error:
        sys.exit(f"Language service error: {doc.error.code} — {doc.error.message}")

    print("Original:\n ", text, "\n")
    print("Redacted:\n ", doc.redacted_text, "\n")
    if doc.entities:
        print("Detected:")
        for e in doc.entities:
            print(f"  - {e.category:<22} {e.text!r}  (confidence {e.confidence_score:.2f})")


if __name__ == "__main__":
    main()
