"""
Module 4 (OPTIONAL) — Let an AGENT do the speaking via an MCP tool.

Unlike speech_chat.py (which calls the Azure Speech SDK directly in a fixed
pipeline), here speech synthesis is exposed to a Foundry *agent* as an MCP tool.
The agent decides to call it during its run — synthesis becomes a tool the agent
uses, not a step we hardcode.

PREVIEW + GOVERNANCE CAVEAT (read this to learners):
The hosted "Azure Speech MCP Server" in the Foundry Add-Tools catalog is Preview
and currently *key-auth only* (Bearer API Key + X-Blob-Container-Url). Accounts
that enforce Entra-only auth (disableLocalAuth=true) cannot connect it — the
key-based tool is blocked by design. That is least-privilege governance working
as intended, and it is why this script is "explain-only" in a hardened tenant.
For a keyless demo of the *same* pattern that runs live, use the companion:
agent_mcp_tool.py (points the agent at the documented Microsoft Learn MCP).

This is an OPTIONAL, preview-oriented demo. It needs:
  - an agent (reuse the Module 2c agent; set AGENT_NAME in .env)
  - the Azure Speech Foundry Tools MCP server URL in SPEECH_MCP_URL
    (only obtainable in a tenant that allows key-based auth)

Run:
    python demos/04-ai-speech/speech_agent_mcp.py "Welcome me to Contoso Private Bank out loud."
"""
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("AGENT_NAME")
SPEECH_MCP_URL = os.getenv("SPEECH_MCP_URL")  # Azure Speech Foundry Tools MCP endpoint


def main():
    prompt = " ".join(sys.argv[1:]).strip() or "Say a warm one-sentence welcome out loud."

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")
    if not AGENT_NAME:
        sys.exit("AGENT_NAME is not set. Reuse the Module 2c agent name in .env.")
    if not SPEECH_MCP_URL:
        sys.exit(
            "SPEECH_MCP_URL is not set.\n"
            "The hosted Azure Speech MCP Server (Foundry catalog) is Preview and\n"
            "*key-auth only*. This account has disableLocalAuth=true (Entra-only),\n"
            "so the key-based tool cannot be connected \u2014 governance blocks it by design.\n"
            "Run the keyless companion instead:\n"
            "    python demos/04-ai-speech/agent_mcp_tool.py \"What is Azure AI Speech used for?\""
        )

    from azure.ai.projects import AIProjectClient

    # allow_preview=True is required to target an agent endpoint.
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
        allow_preview=True,
    )

    # OpenAI-compatible client pointed at the agent (supplies model + instructions).
    client = project.get_openai_client(agent_name=AGENT_NAME)

    # Register the Speech MCP server as a tool. The agent can now call speech
    # synthesis autonomously as part of its run.
    response = client.responses.create(
        input=prompt,
        tools=[
            {
                "type": "mcp",
                "server_label": "azure-speech",
                "server_url": SPEECH_MCP_URL,
                "require_approval": "never",
            }
        ],
    )

    print(response.output_text)


if __name__ == "__main__":
    main()
