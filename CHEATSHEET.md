# AI-901 Learner Cheatsheet

**Microsoft Azure AI Fundamentals**  
Concepts, services, agents, and exam-ready distinctions

> **Important:** Exam objectives and Microsoft product terminology can change. Always check the [official AI-901 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-901) for the latest requirements.
>
> **Last verified against the English-language study guide:** 2026-09-02

> **Exam domains**
> - Identify AI concepts and capabilities: **40-45%**
> - Implement AI solutions by using Microsoft Foundry: **55-60%**

---

## 1. The big picture

| AI workload | What it does | Typical clue |
|---|---|---|
| Generative and agentic AI | Creates content. Agents can use instructions, knowledge, and tools to pursue a goal. | Generate, summarize, plan, call tools |
| Text analysis | Finds language, key phrases, entities, sentiment, or summaries. | Analyze unstructured text |
| Speech | Converts speech to text, text to speech, or supports spoken interaction. | Transcribe, synthesize, voice |
| Computer vision | Interprets or generates visual content. | Classify, detect, caption, generate |
| Information extraction | Extracts structured information from documents, images, audio, or video. | Fields, layout, key-value pairs |

### Fast distinctions

#### Generative AI vs. agent

- **Generative AI** produces content.
- **An agent** combines a model with instructions and can use knowledge or tools to pursue goals through multi-step action.

#### RAG vs. fine-tuning

- **Retrieval-augmented generation (RAG)** retrieves external knowledge at run time to ground a response.
- **Fine-tuning** changes model behavior through additional training.

#### User prompt vs. system prompt

- A **user prompt** states the immediate request.
- A **system prompt** sets persistent behavior, boundaries, role, and response expectations.

#### Embedding

A numerical vector representing semantic meaning. Embeddings are useful for similarity search and retrieval.

#### Hallucination

A plausible-sounding result that is unsupported or incorrect. Grounding, evaluation, and human review can reduce the risk.

---

## 2. Responsible AI

Microsoft's six Responsible AI principles:

| Principle | What it means |
|---|---|
| Fairness | Similar situations should receive similar treatment. Test for harmful bias. |
| Reliability and safety | The solution should operate consistently, handle unexpected inputs, and fail safely. |
| Privacy and security | Protect data, credentials, access, and system boundaries. |
| Inclusiveness | Design for people with varied abilities, backgrounds, and needs. |
| Transparency | Make AI use, limitations, and decision factors understandable. |
| Accountability | People and organizations remain responsible for AI outcomes. |

### Responsible generative AI loop

1. **Identify** potential harms.
2. **Measure** how often and how severely they occur.
3. **Mitigate** risks across the solution.
4. **Operate** responsibly, monitor, and improve.

---

## 3. Microsoft Foundry

Remember the basic flow:

> **Choose** a model or tool → **Deploy** it → **Build** the app or agent → **Evaluate** quality and safety → **Operate** and monitor

### Foundry resource vs. project

- A **Foundry resource** provides access to AI services.
- A **Foundry project** is a workspace within that resource.

### General-purpose model vs. specialized tool

- Use a **general-purpose model** for flexible, open-ended tasks.
- Use a **specialized Foundry Tool** for a supported task that benefits from a purpose-built API and structured output.

### Authentication

Applications commonly need:

- A service endpoint
- Credentials, such as an API key or Microsoft Entra ID token

Keep secrets outside source code, for example in environment variables or a `.env` file.

### Model deployment basics

Choose a model based on its capabilities, modalities, cost, availability, and deployment options. Review configuration parameters such as token limits, temperature, and output length because they affect behavior, quality, and cost.

---

## 4. Choose the capability by requirement

| Requirement | Best-fit capability | Memory hook |
|---|---|---|
| Detect the language of text | Azure Language | Language name, code, and confidence |
| Find people, places, or organizations | Named entity recognition | Entities have categories |
| Find the main concepts in text | Key phrase extraction | Themes, not entity types |
| Assess opinion in text | Sentiment analysis | Positive, neutral, or negative |
| Convert live audio to text | Real-time speech to text | Immediate transcription |
| Process long recordings later | Batch transcription | Asynchronous audio processing |
| Convert text to natural speech | Text to speech | Speech synthesis |
| Label an image | Image classification | What is in the image? |
| Locate objects in an image | Object detection | What and where? Bounding boxes |
| Extract structured data from content | Azure Content Understanding | Fields and structure across modalities |

### Commonly confused vision tasks

- **Image classification:** applies one or more labels to an image.
- **Object detection:** identifies objects and returns their locations using bounding boxes.
- **Image description or captioning:** produces natural-language information about an image.
- **Image generation:** creates new visual content from a prompt.

### Information extraction

Azure Content Understanding can extract structured information from:

- Documents and forms
- Images
- Audio
- Video

It goes beyond basic recognition by identifying useful structure and extracting fields across supported content types.

---

## 5. Transformer essentials

| Term | Meaning |
|---|---|
| Tokenization | Breaks input into smaller units that the model can process. |
| Embeddings | Map tokens or other content into vectors that capture semantic relationships. |
| Attention | Weights relationships among tokens or other input elements. |
| Encoder | Creates semantic representations of input. |
| Decoder | Generates output sequences. GPT-style models are decoder-based. |
| Multimodal model | Works across more than one modality, such as text and images or audio. |

---

## 6. Prompting checklist

Before submitting a prompt, check that you have:

- [ ] Stated the goal clearly
- [ ] Added relevant context
- [ ] Included constraints
- [ ] Specified the required output format
- [ ] Provided examples when useful
- [ ] Grounded the model with trusted data when needed
- [ ] Evaluated the result for accuracy, quality, and safety

---

## 7. Exam-day decision rules

1. Read the requirement first. Identify the workload before choosing the service.
2. Prefer the least complex managed capability that fully satisfies the requirement.
3. Watch the verb: **generate, analyze, transcribe, synthesize, detect, extract, classify**.
4. For a supported task that requires structured output, consider a specialized Foundry Tool.
5. For flexible generation, favor a general-purpose model.
6. Remember the implementation skills: prompts, model deployment, lightweight clients, agents, SDKs, REST APIs, and CLIs.

### Keyword shortcuts

| If the requirement says... | Think... |
|---|---|
| Generate content | Generative AI model |
| Complete a goal using tools | Agent |
| Analyze text | Azure Language or a general-purpose model |
| Find named items | Named entity recognition |
| Identify major concepts | Key phrase extraction |
| Convert speech into text | Speech to text |
| Convert text into speech | Text to speech |
| Label an image | Image classification |
| Find objects and their locations | Object detection |
| Extract structured fields | Content Understanding |

---

## 8. Quick self-test

1. **Which capability identifies company addresses in text?**  
   Named entity recognition.

2. **Which capability processes many recorded calls asynchronously?**  
   Batch transcription.

3. **Which vision task returns object coordinates?**  
   Object detection with bounding boxes.

4. **How can you provide current organizational knowledge without retraining the model?**  
   Use retrieval and grounding, commonly through RAG.

5. **What should you build when the system must pursue a goal through multi-step reasoning and tool use?**  
   An agent.

6. **Which Foundry Tool extracts structured fields from forms, images, audio, or video?**  
   Azure Content Understanding.

7. **Which Responsible AI principle applies when users are not told that they are interacting with AI?**  
   Transparency.

8. **Which Responsible AI principle applies when nobody owns the monitoring and correction process?**  
   Accountability.

---

## Official study resources

- [AI-901 study guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-901)
- [AI-901 exam page](https://learn.microsoft.com/en-us/credentials/certifications/exams/ai-901/)
- [AI concepts learning path](https://aka.ms/mslearn-ai-concepts-lp)
- [AI apps and agents learning path](https://aka.ms/mslearn-get-started-ai-apps-agents-lp)

> Use this cheatsheet as a revision aid, not as a substitute for the current official study guide.
