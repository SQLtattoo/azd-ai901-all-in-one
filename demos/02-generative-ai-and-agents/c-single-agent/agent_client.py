"""
Module 2c — Lightweight client for a single Foundry agent.

Sends one prompt to an agent you created in the Foundry portal and prints the
reply. Pass --show-activity to prove when the agent searches connected knowledge
or calls an MCP tool. In azure-ai-projects 2.x you talk to an agent through an
OpenAI-compatible client and the Responses API; the agent supplies the model,
instructions, knowledge, and tools.

Run:
    python demos/02-generative-ai-and-agents/c-single-agent/agent_client.py "I want to start investing for my child's education in 10 years. Where do I begin?"
    python demos/02-generative-ai-and-agents/c-single-agent/agent_client.py --show-activity "What is the Summit Welcome Review, and how does Microsoft Foundry file search work?"
"""
import argparse
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME")


def parse_args():
    parser = argparse.ArgumentParser(description="Send a prompt to the configured Foundry agent.")
    parser.add_argument(
        "--show-activity",
        action="store_true",
        help="Print knowledge searches, MCP calls, and citations returned by the agent.",
    )
    parser.add_argument("prompt", nargs="*", help="Prompt to send to the agent.")
    return parser.parse_args()


def print_activity(response):
    """Print concise proof of server-side knowledge and tool use."""
    activity = []
    citations = []

    for item in response.output:
        item_type = getattr(item, "type", "")
        if item_type == "file_search_call":
            queries = getattr(item, "queries", None)
            detail = f" queries={queries}" if queries else ""
            activity.append(f"knowledge: file_search{detail}")
        elif item_type == "mcp_list_tools":
            names = ", ".join(tool.name for tool in getattr(item, "tools", []))
            activity.append(f"tool discovery: {getattr(item, 'server_label', 'mcp')} [{names}]")
        elif item_type == "mcp_call":
            server = getattr(item, "server_label", "mcp")
            name = getattr(item, "name", "unknown")
            activity.append(f"tool call: {server}.{name} args={getattr(item, 'arguments', '{}')}")

        for content in getattr(item, "content", []):
            for annotation in getattr(content, "annotations", []):
                annotation_type = getattr(annotation, "type", "")
                if annotation_type == "file_citation":
                    citations.append(getattr(annotation, "filename", "uploaded file"))
                elif annotation_type == "url_citation":
                    citations.append(getattr(annotation, "url", "web source"))

    print("=== Agent activity ===")
    if activity:
        for event in activity:
            print(event)
    else:
        print("No knowledge search or tool call was reported.")
    if citations:
        print(f"citations: {', '.join(dict.fromkeys(citations))}")
    print("======================\n")


def main():
    args = parse_args()
    prompt = " ".join(args.prompt).strip() or "I've just joined Contoso Private Bank — how do I get started?"

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
    if args.show_activity:
        print_activity(response)
    print(response.output_text)


if __name__ == "__main__":
    main()
