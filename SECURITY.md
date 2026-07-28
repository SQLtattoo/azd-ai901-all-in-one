# Security Policy

## Scope

This repository contains **teaching demos** for the AI-901 course. It is sample
code intended to be run by an instructor or learner against **their own**
disposable Azure subscription. It is not production software and carries no
service-level or support commitment.

## Reporting a vulnerability

If you find a security issue in this sample code — for example a leaked
credential, an insecure default in the Bicep templates, or a dependency
advisory — please open a
[GitHub security advisory](https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository rather than a public issue.

For a vulnerability in an **Azure service or a Microsoft product** (not this
sample code), report it to the Microsoft Security Response Center at
<https://msrc.microsoft.com/create-report> instead.

## Security notes for anyone running these demos

- **Never commit `.env`.** It is covered by `.gitignore`, along with `.azure/`
  and common certificate/key extensions. The generated `.env` contains your
  Foundry project endpoint and full Azure resource IDs (including your
  subscription ID).
- **The demos are keyless by default.** They authenticate with
  `DefaultAzureCredential` (your `az login` identity). `infra/` deploys the
  Foundry account with `disableLocalAuth = true`, so shared keys are switched
  off. Only set that parameter to `false` if you specifically need the preview
  key-auth Speech MCP tool, and turn it back on afterwards.
- **The deployed account is reachable from the public internet.**
  `publicNetworkAccess` is `Enabled` so learners can run the scripts from their
  own machines. This is a classroom convenience — restrict it with network ACLs
  or a private endpoint for anything else.
- **RBAC is scoped to the account**, and grants the deploying user the Cognitive
  Services OpenAI User, Cognitive Services User, Azure AI Developer, and Azure
  AI User roles. Review these before running `azd up` in a shared subscription.
- **Tear down after class.** `azd down --purge` removes the resource group and
  purges the soft-deleted Foundry account so it stops incurring cost.
- **`demos/responsible-ai/safety_demo.py` contains a deliberately policy-violating
  prompt.** It is a test fixture whose only purpose is to make an Azure content
  filter return a 400 in front of a class. It is expected to be blocked and
  never produces harmful output.
