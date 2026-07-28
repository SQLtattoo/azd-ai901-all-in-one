"""
Module 5 — Generate an image from a text prompt.

Calls the image deployment (gpt-image-1) in your Microsoft Foundry resource and
saves the PNG under output/.

Run:
    python demos/05-computer-vision/image_generate.py "a watercolor postcard of Seattle at sunset"
"""
import base64
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
IMAGE_DEPLOYMENT = os.getenv("IMAGE_DEPLOYMENT", "gpt-image-1")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def _account_openai_base_url():
    """Account-level /openai/v1 route.

    Image generation is served at the account scope, not the project-scoped path
    (`.../api/projects/<proj>/openai/v1`) that get_openai_client() uses by default
    — calling images there returns 404. Chat/Responses work at either scope.
    """
    root = (AZURE_OPENAI_ENDPOINT or PROJECT_ENDPOINT).split("/api/projects/")[0].rstrip("/")
    return f"{root}/openai/v1"


def get_client():
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    # Keyless bearer auth from get_openai_client(), but pointed at the account-level
    # base_url so /images/generations resolves.
    return project.get_openai_client(base_url=_account_openai_base_url())


def main():
    prompt = " ".join(sys.argv[1:]).strip() or "a watercolor postcard of Seattle at sunset"
    client = get_client()

    # gpt-image-1 always returns base64 image data, so no response_format arg
    # is passed (unlike dall-e-3, it rejects that parameter).
    result = client.images.generate(
        model=IMAGE_DEPLOYMENT,
        prompt=prompt,
        size="1024x1024",
        n=1,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"image_{datetime.now():%Y%m%d_%H%M%S}.png")
    with open(filename, "wb") as handle:
        handle.write(base64.b64decode(result.data[0].b64_json))
    print(f"Prompt : {prompt}")
    print(f"Saved  : {filename}")


if __name__ == "__main__":
    main()
