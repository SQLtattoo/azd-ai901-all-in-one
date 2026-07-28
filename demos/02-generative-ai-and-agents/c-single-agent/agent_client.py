"""
Module 2c — Lightweight client for a single Foundry agent.

Sends one prompt to an agent you created in the Foundry portal and prints the
reply. In azure-ai-projects 2.x you talk to an agent through an OpenAI-compatible
client and the Responses API; the agent supplies the model and instructions.

Run:
    python demos/02-generative-ai-and-agents/c-single-agent/agent_client.py "I want to start investing for my child's education in 10 years. Where do I begin?"
"""
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME")


def main():
    prompt = " ".join(sys.argv[1:]).strip() or "I've just joined Contoso Private Bank — how do I get started?"

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")
    if not AGENT_NAME:
        sys.exit("AGENT_NAME is not set. Copy the agent's name from the Foundry portal into .env.")

    from azure.ai.projects import AIProjectClient

    # allow_preview=True is required to target an agent endpoint.
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )

    # An OpenAI client pointed at the agent; the agent supplies model + instructions.
    client = project.get_openai_client(agent_name=AGENT_NAME)

    # The Responses API runs the agent on the input and returns its reply.
    response = client.responses.create(input=prompt)
    print(response.output_text)


if __name__ == "__main__":
    main()
