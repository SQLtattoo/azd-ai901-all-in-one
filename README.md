# AI-901 Demos — Microsoft Azure AI Fundamentals

Hands-on demos for delivering **AI-901** (the replacement for AI-900, retired June 30, 2026).
The exam is reorganized around **Microsoft Foundry** and is far more hands-on than AI-900.

> Certification: *Microsoft Certified: Azure AI Fundamentals* · Exam **AI-901** · Course **AI-901T00: Introduction to AI in Azure**
> Skills measured (as of April 15, 2026):
> 1. **Identify AI concepts and capabilities** (40–45%) — concepts
> 2. **Implement AI solutions by using Microsoft Foundry** (55–60%) — hands-on

---

## Demo map — aligned to the 6 course modules

Folders are numbered to match the course modules, so you always know which demo belongs
where. Modules 1 and 2a are done in the Foundry portal; everything else is Python you can
run from your terminal.

| Course module | Demo | What it shows |
|---|---|---|
| **1 — Get started with AI** | *Portal* — create a project, deploy your first model | AI workload types & Foundry basics |
| **2 — Generative AI & agents** | *Portal* — Chat playground | Prompt engineering & generation parameters |
| | [demos/02-generative-ai-and-agents/b-foundry-sdk-chat](demos/02-generative-ai-and-agents/b-foundry-sdk-chat) | Python chat client using the Foundry SDK |
| | [demos/02-generative-ai-and-agents/c-single-agent](demos/02-generative-ai-and-agents/c-single-agent) | Build & call a single agent |
| **3 — Text analysis** | [demos/03-text-analysis](demos/03-text-analysis) | Sentiment, key phrases, entities & PII detection |
| **4 — AI speech** | [demos/04-ai-speech](demos/04-ai-speech) | Speech-to-text → chat → text-to-speech |
| **5 — Computer vision** | [demos/05-computer-vision](demos/05-computer-vision) | Multimodal image understanding + image generation |
| **6 — Information extraction** | [demos/06-information-extraction](demos/06-information-extraction) | Extract fields from a document with Content Understanding |
| **Responsible AI** *(cross-cutting)* | [demos/responsible-ai](demos/responsible-ai) | Content filters & safety in Foundry |

Every script has a docstring at the top with its exact run command and what to expect.

---

## Prerequisites

- An **Azure subscription** with access to **Microsoft Foundry** (formerly Azure AI Foundry).
- **Python 3.10+**.
- **Azure CLI** signed in (`az login`) — the demos use keyless auth (`DefaultAzureCredential`) by default.
- **Azure Developer CLI** (`azd`) if you want to provision the infrastructure automatically (recommended).

## Provision Azure resources (recommended)

The `infra/` folder contains Bicep that stands up everything the demos need in one shot:
a **Microsoft Foundry account**, a **project**, model deployments (`gpt-5.1`, `gpt-image-1`,
`text-embedding-3-small`), and the **keyless RBAC** roles for your user. A postprovision
hook then writes your `.env` automatically.

```powershell
# From the repo root
azd auth login
azd up
```

> 💸 **This costs real money.** `azd up` creates four model deployments
> (`gpt-5.1`, `gpt-image-1`, `text-embedding-3-small`, `gpt-realtime`) on a
> pay-as-you-go Foundry account, and they bill for as long as they exist — not
> just while you're running a demo. Run `azd down --purge` as soon as you're done.
> Use a disposable subscription, not a shared or production one.

`azd up` will prompt for an **environment name** and a **location**. Pick a region that
supports gpt-5.1, gpt-image-1, **and** Content Understanding — e.g. **swedencentral**,
**westus**, or **australiaeast**. When it finishes, `.env` is populated for you.

> One thing is **not** provisioned: the agent used by the single-agent demo (Module 2c).
> Agents are created in the Foundry portal — see
> [step 4 of the walkthrough](#4-module-2c--create-and-call-an-agent). The generated `.env`
> defaults to `AGENT_NAME=wealth-concierge`; name your agent to match.

To tear it all down afterwards:

```powershell
azd down --purge
```

### Showcasing the chat model

`gpt-5.1` is the default chat/multimodal model — one deployment serves both **chat** and
**vision** (it accepts text and image input), and it's a current, generally available model.
Because `gpt-5.1` is a **reasoning model**, two things differ from older GPT-4o-style models:

- It does **not** accept `temperature`; use `reasoning_effort` (defaults to `none`) and
  `verbosity` instead. The demos pass neither, so they use the defaults.
- It uses `max_completion_tokens`, not `max_tokens`.

To pin a different model, override the params before deploying — no code changes required:

```powershell
azd env set CHAT_MODEL_NAME <model>
azd env set CHAT_MODEL_VERSION <version>   # check the Foundry model catalog
azd up
```

The Bicep params live in [infra/main.bicep](infra/main.bicep) (`chatModelName` /
`chatModelVersion`). Before you run the demos, check three things:

1. **Region + quota** — confirm the model is available in your chosen region and you have
   quota (Foundry portal → *Model catalog* / *Quotas*).
2. **API parameters** — reasoning models (like `gpt-5.1`) reject `temperature` and
   `max_tokens`. If you switch to a non-reasoning model and want deterministic JSON in
   the text-analysis demo, you can re-add `temperature=0` in
   [demos/03-text-analysis/text_analysis.py](demos/03-text-analysis/text_analysis.py).
3. **Vision** — this is the important one (see below).

#### What about vision?

Demo 5 sends an **image** into `chat.completions`, so `MULTIMODAL_DEPLOYMENT` must point at
a **vision-capable** model. `gpt-5.1` accepts text *and* image input, so the single
deployment serves both chat and vision — `CHAT_DEPLOYMENT` and `MULTIMODAL_DEPLOYMENT` point
at the same `gpt-5.1` deployment.

If you ever switch `CHAT_DEPLOYMENT` to a **text-only** model, deploy a separate
vision-capable model and point `MULTIMODAL_DEPLOYMENT` at that one instead. The current Bicep
deploys a single chat deployment used for both; to add a second, add another
`Microsoft.CognitiveServices/accounts/deployments` resource in
[infra/resources.bicep](infra/resources.bicep) (chain it with `dependsOn`) and output its
name.

Either way, `gpt-image-1` still handles **image generation** (Module 5's second script) — that's
separate from vision *input* and unaffected by the chat model choice.

## Setup (Python)

```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you did **not** use `azd`, create `.env` manually:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` with your Foundry **project endpoint** and **deployment names**.
Every script loads `.env` automatically.

### Verify your setup

```powershell
az login
python verify_setup.py
```

`verify_setup.py` checks your `.env`, confirms Azure auth works, and does a one-line chat
round-trip. Exit code `0` means you're ready to go.

---

## Walkthrough — run the demos in order

Each step stands alone, but they build a story: **portal → code → agent → modalities
(text, speech, vision) → extraction → responsible AI**. Activate your virtual environment
and run everything from the repo root.

### 1. Module 1 — deploy your first model *(portal)*

Go to <https://ai.azure.com> and create a **project**. Open the **Model catalog**, find
**gpt-5.1**, and click **Deploy** — name the deployment `gpt-5.1` so it matches `.env`.
On the deployment's **Details** tab, note the **endpoint** and **deployment name**: those
are exactly the two values every later demo uses.

*If you ran `azd up`, this is already done for you — open the project and look around instead.*

**Takeaway:** a *model* in the catalog becomes a *deployment* you call by name.

### 2. Module 2a — prompt engineering *(portal)*

Open **Playground → Chat** and pick your `gpt-5.1` deployment. Paste a system prompt:

```text
You are "Aria", a concise concierge for Contoso Private Bank. Answer in <= 3 sentences.
Give general information only — no personalized investment, tax, or legal advice; refer
clients to a licensed advisor for decisions. Never invent products, rates, or figures.
```

Ask: `I'm a new client — how should I prepare for my first wealth review?` Then change the
system prompt and resend, and open the parameters panel to adjust generation settings.
Finally, click **View code** — that generated snippet is the next step.

**Takeaway:** system prompt = standing instructions and guardrails; user prompt = the
request. Same model, very different behaviour, no redeploy.

### 3. Module 2b — chat from Python

```powershell
python demos/02-generative-ai-and-agents/b-foundry-sdk-chat/chat_client.py
```

An interactive REPL. Type a message, press Enter, type `exit` to quit. This is the
playground's *View code* turned into a real client, authenticating with your `az login`
identity — no API key anywhere.

**Takeaway:** the Foundry SDK gives you an OpenAI-compatible client from a project endpoint.

### 4. Module 2c — create and call an agent

First create the agent in the portal: **Foundry → your project → Agents → New agent**.
Name it `wealth-concierge` (matching `AGENT_NAME` in `.env`), pick your `gpt-5.1`
deployment, and give it instructions — the Aria system prompt from step 2 works well. Test
it in the portal's agent playground, then call the *same* agent from code:

```powershell
python demos/02-generative-ai-and-agents/c-single-agent/agent_client.py "I want to start investing for my child's education in 10 years. Where do I begin?"
```

**Takeaway:** an agent packages model + instructions + tools server-side, so the client
sends only the user's message.

### 5. Module 3 — text analysis & PII

```powershell
python demos/03-text-analysis/text_analysis.py          # sentiment, key phrases, entities as JSON
python demos/03-text-analysis/pii_redact.py             # redaction via the chat model
python demos/03-text-analysis/pii_language.py           # PII detection via Azure AI Language
```

Each accepts your own text as an argument, e.g.
`python demos/03-text-analysis/pii_language.py "Call me on +1 (415) 555-0132."`

**Takeaway:** two valid routes to the same outcome — a generative model you prompt, and a
purpose-built Language service with a fixed schema.

### 6. Module 4 — speech

```powershell
python demos/04-ai-speech/speech_chat.py                        # mic in, speech out
python demos/04-ai-speech/speech_chat.py --text "What is Azure AI Foundry?"   # no mic needed
```

Speech-to-text → chat completion → text-to-speech, all keyless. Two optional extras live in
the same folder: `agent_mcp_tool.py` (an agent calling the Microsoft Learn MCP server) and
`voice_live_chat.py` (preview real-time speech-to-speech; needs the extra packages listed
in `requirements.txt`).

**Takeaway:** speech is a modality wrapped around the same chat call.

### 7. Module 5 — computer vision

```powershell
python demos/05-computer-vision/vision_describe.py --image demos/05-computer-vision/assets/sample.png
python demos/05-computer-vision/image_generate.py "a watercolor postcard of Seattle at sunset"
```

The first sends an **image into** a multimodal model; the second generates an image with
`gpt-image-1` and saves it under `demos/05-computer-vision/output/`.

**Takeaway:** vision *input* and image *generation* are different capabilities — and
different deployments.

### 8. Module 6 — information extraction

```powershell
python demos/06-information-extraction/analyze_document.py --analyzer prebuilt-invoice --file demos/06-information-extraction/assets/sample-invoice.pdf
```

Submits the sample invoice to Content Understanding, polls the async operation, and prints
the extracted fields with confidence scores. Add `--raw` for the full JSON.

**Takeaway:** extraction returns *structured, typed fields with confidence* — not prose.

### 9. Responsible AI — watch a content filter fire

```powershell
python demos/responsible-ai/safety_demo.py
```

Sends one benign prompt (succeeds) and one deliberately policy-violating prompt (blocked
with a `400` and a `content_filter` code). Being blocked **is** the successful result.

**Takeaway:** guardrails are enforced by the platform, not just by your prompt.

### 10. Clean up

```powershell
azd down --purge
```

Do this as soon as you're finished — the deployments bill for as long as they exist.

---

## Auth model

The scripts default to **keyless** auth via `DefaultAzureCredential` (uses your `az login`
identity or a managed identity). The Bicep deploys the Foundry account with
`disableLocalAuth = true`, so shared API keys are switched **off** — Entra ID is the only
way in. If you need the preview key-auth Speech MCP tool (Module 4, Part B), redeploy with
`azd env set` / a parameter override of `disableLocalAuth=false`, then turn it back on.

> ⚠️ Never commit real keys or `.env`. Both `.env` and `.azure/` are already in `.gitignore`.
> Note that a generated `.env` contains your project endpoint and full Azure resource IDs
> (including your subscription ID).

See [SECURITY.md](SECURITY.md) for the full security notes and how to report an issue.

## SDK / preview note

Foundry SDKs and features (agents, Content Understanding) evolve quickly and some are in
**preview**. If an API behaves differently for you, check the version pins in
`requirements.txt` and the inline notes at the top of each script. The equivalent steps are
always available in the Foundry portal if a package version drifts.

## License & disclaimer

Licensed under the [MIT License](LICENSE).

This is **personal, community-maintained training material** — it is not an official
Microsoft product, is not endorsed by or affiliated with Microsoft, and comes with no
warranty or support. Views expressed here are my own. Microsoft, Azure, Microsoft Foundry,
and related names are trademarks of the Microsoft group of companies; they are used here
only to describe the services the demos call.

The sample data (Contoso Private Bank, Northwind Traders, the invoice, the PII example
text) is entirely fictitious. Any resemblance to real people, organisations, or records is
coincidental.

