"""
Module 4 (OPTIONAL) — Let the MODEL call an MCP tool (keyless, runnable).

Companion to speech_agent_mcp.py. The hosted Azure Speech MCP Server (Part B)
is Preview and *key-auth only*, so an Entra-only tenant (disableLocalAuth=true)
cannot connect it. To still show the objective "the model autonomously calls an
MCP tool", this points your Foundry model at the documented, keyless Microsoft
Learn MCP server. Same pattern, different tool.

Note: a *named* Foundry agent has its tools fixed server-side, so you cannot
pass tools=[...] per request against an agent. Here we call the model
deployment directly via the Responses API, where per-request tools ARE allowed.

Run:
    python demos/04-ai-speech/agent_mcp_tool.py "What is Azure AI Speech used for?"
"""
import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
CHAT_DEPLOYMENT = os.getenv("CHAT_DEPLOYMENT", "gpt-5.1")
# Documented, keyless (no API key) MCP server. Override via .env if you like.
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://learn.microsoft.com/api/mcp")
MCP_SERVER_LABEL = os.getenv("MCP_SERVER_LABEL", "microsoft_learn")


def main():
    prompt = " ".join(sys.argv[1:]).strip() or "Search Microsoft Learn: what is Azure AI Speech used for?"

    if not PROJECT_ENDPOINT:
        sys.exit("FOUNDRY_PROJECT_ENDPOINT is not set. Fill in .env and run `az login`.")

    from azure.ai.projects import AIProjectClient

    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    # Keyless, OpenAI-compatible client bound to the Foundry project.
    client = project.get_openai_client()

    # Register the MCP server as a tool. The model decides *when* to call it.
    # require_approval="never" keeps the demo one-shot; switch to "always" to
    # show a human-in-the-loop approval step before the tool runs.
    response = client.responses.create(
        model=CHAT_DEPLOYMENT,
        instructions=(
            "You MUST answer using the Microsoft Learn MCP tool to look up official "
            "documentation. Base your answer on what the tool returns and end with a "
            "'Sources:' list of the documentation URLs you used."
        ),
        input=prompt,
        tools=[
            {
                "type": "mcp",
                "server_label": MCP_SERVER_LABEL,
                "server_url": MCP_SERVER_URL,
                "require_approval": "never",
            }
        ],
    )

    # --- Proof the MCP tool was actually used (not just parametric memory) ---
    discovered = [i for i in response.output if getattr(i, "type", "") == "mcp_list_tools"]
    calls = [i for i in response.output if getattr(i, "type", "") == "mcp_call"]

    print("=== MCP tool activity ===")
    for d in discovered:
        names = ", ".join(t.name for t in getattr(d, "tools", []))
        print(f"discovered on '{d.server_label}': {names}")
    if calls:
        for c in calls:
            print(f"called    : {c.server_label}.{c.name}  args={c.arguments}")
            if getattr(c, "error", None):
                print(f"  error   : {c.error}")
            else:
                preview = (c.output or "").strip().replace("\n", " ")
                print(f"  returned: {preview[:200]}{'...' if len(preview) > 200 else ''}")
    else:
        print("NONE — the model answered from its own knowledge, not the docs.")
    print("=========================\n")

    print(response.output_text)


if __name__ == "__main__":
    main()
