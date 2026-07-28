"""
Demo 6 — Extract structured fields from a document with Azure AI
Content Understanding (preview).

Submits a file to an analyzer, polls the async operation, and prints the result.

Run:
    python demos/06-information-extraction/analyze_document.py \
        --analyzer prebuilt-invoice --file assets/sample-invoice.pdf

Note: Content Understanding is in preview; confirm the analyzer id and
api-version for your resource (CONTENT_UNDERSTANDING_API_VERSION in .env).
"""
import argparse
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

ENDPOINT = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT", "").rstrip("/")
API_VERSION = os.getenv("CONTENT_UNDERSTANDING_API_VERSION", "2025-11-01")

# Content Understanding GA (2025-11-01) uses the :analyzeBinary operation for
# raw file uploads; the :analyze operation now expects a JSON `inputs` body.


def bearer_token():
    return DefaultAzureCredential().get_token(
        "https://cognitiveservices.azure.com/.default"
    ).token


def field_value(field):
    """Reduce a Content Understanding field object to a readable value."""
    if not isinstance(field, dict):
        return field
    ftype = field.get("type")
    if ftype == "array":
        return [field_value(item) for item in field.get("valueArray", [])]
    if ftype == "object":
        return {k: field_value(v) for k, v in field.get("valueObject", {}).items()}
    if ftype == "currency":
        cur = field.get("valueCurrency", {})
        amount = cur.get("amount")
        code = cur.get("currencyCode", "")
        return f"{amount} {code}".strip() if amount is not None else None
    # Fall back to whatever value* key is present.
    for key in ("valueString", "valueNumber", "valueInteger", "valueDate",
                "valueTime", "valueBoolean", "content"):
        if key in field:
            return field[key]
    return None


def print_summary(result):
    contents = result.get("contents") or []
    if not contents:
        print("(no contents returned)")
        return
    for i, content in enumerate(contents):
        if len(contents) > 1:
            print(f"\n--- content #{i + 1} ---")
        fields = content.get("fields") or {}
        if not fields:
            print("(no fields extracted)")
            continue
        for name, field in fields.items():
            value = field_value(field)
            conf = field.get("confidence")
            conf_str = f"  ({conf:.0%})" if isinstance(conf, (int, float)) else ""
            if isinstance(value, list):
                print(f"{name}:{conf_str}")
                for j, row in enumerate(value):
                    if isinstance(row, dict):
                        parts = ", ".join(f"{k}={v}" for k, v in row.items() if v is not None)
                        print(f"  [{j + 1}] {parts}")
                    else:
                        print(f"  [{j + 1}] {row}")
            elif isinstance(value, dict):
                print(f"{name}:{conf_str}")
                for k, v in value.items():
                    if v is not None:
                        print(f"  {k}: {v}")
            else:
                print(f"{name}: {value}{conf_str}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyzer", default="prebuilt-invoice", help="Analyzer id.")
    parser.add_argument("--file", required=True, help="Path to the document to analyze.")
    parser.add_argument("--raw", action="store_true", help="Print the full JSON result.")
    args = parser.parse_args()

    if not ENDPOINT:
        sys.exit("CONTENT_UNDERSTANDING_ENDPOINT is not set. Fill in .env and run `az login`.")
    if not os.path.exists(args.file):
        sys.exit(f"File not found: {args.file}")

    headers = {
        "Authorization": f"Bearer {bearer_token()}",
        "Content-Type": "application/octet-stream",
    }
    analyze_url = (
        f"{ENDPOINT}/contentunderstanding/analyzers/{args.analyzer}:analyzeBinary"
        f"?api-version={API_VERSION}"
    )

    # 1) Submit the file.
    with open(args.file, "rb") as handle:
        submit = requests.post(analyze_url, headers=headers, data=handle.read(), timeout=60)
    if submit.status_code not in (200, 201, 202):
        sys.exit(f"Submit failed ({submit.status_code}): {submit.text}")

    operation_location = submit.headers.get("Operation-Location")
    if not operation_location:
        # Some versions return the result inline.
        inline = submit.json()
        if args.raw:
            print(json.dumps(inline, indent=2))
        else:
            print_summary(inline.get("result", inline))
        return

    # 2) Poll until the operation completes.
    poll_headers = {"Authorization": f"Bearer {bearer_token()}"}
    for _ in range(30):
        time.sleep(2)
        poll = requests.get(operation_location, headers=poll_headers, timeout=60).json()
        status = poll.get("status", "").lower()
        if status in ("succeeded", "failed"):
            if status == "failed":
                sys.exit(f"Analyze failed: {json.dumps(poll, indent=2)}")
            # 3) Print extracted fields.
            result = poll.get("result", poll)
            if args.raw:
                print(json.dumps(result, indent=2))
            else:
                print_summary(result)
            return

    sys.exit("Timed out waiting for the analyze operation to complete.")


if __name__ == "__main__":
    main()
