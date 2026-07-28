"""
Demo 5A — Interpret an image with a multimodal Foundry model.

Sends an image (URL or local file) plus a question to the gpt-5.1 deployment and
prints a description and answer.

Run:
    python demos/05-computer-vision/vision_describe.py --image path/or/url
"""
import argparse
import base64
import mimetypes
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
MULTIMODAL_DEPLOYMENT = os.getenv("MULTIMODAL_DEPLOYMENT", "gpt-5.1")


def to_image_content(image):
    """Return an OpenAI image content part for either a URL or a local file."""
    if image.startswith("http://") or image.startswith("https://"):
        return {"type": "image_url", "image_url": {"url": image}}

    if not os.path.exists(image):
        sys.exit(f"Image not found: {image}")
    mime = mimetypes.guess_type(image)[0] or "image/jpeg"
    with open(image, "rb") as handle:
        data = base64.b64encode(handle.read()).decode("utf-8")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Image URL or local file path.")
    parser.add_argument(
        "--question",
        default="Describe this image, then list any text or notable objects you see.",
    )
    args = parser.parse_args()

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")

    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    client = project.get_openai_client()

    response = client.chat.completions.create(
        model=MULTIMODAL_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a precise visual assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": args.question},
                    to_image_content(args.image),
                ],
            },
        ],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
