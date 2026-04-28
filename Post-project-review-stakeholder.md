# LAB | Post-project review — stakeholders & real-world scope

**Javier Portero Aylagas – Daria Bystrova – Julian Granados – Carlos Martínez Boto**

---

## Part 1: Project snapshot

### 1.1 What problem was meant to be solved
The project aims to make text-based information more accessible and easier to engage with. It combines written content from one or more sources (PDF, URL, and free text) into a concise text and provides an audio version presented as a conversation between two speakers. This enables users to quickly understand, review, and discuss new topics in a more flexible way.

### 1.2 Who the intended user or beneficiary is
The tool is designed for anyone with an OpenAI API key who wants to generate podcast-style audio from text. This includes students, researchers, and the general public. It was primarily developed for personal use and learning purposes rather than for professional content creators, as the generated audio still requires refinement to reach publishable quality.

### 1.3 What was actually built or delivered (MVP level)
A minimum viable product (MVP) that converts text into audio using a pipeline of multiple AI model calls was developed. The system makes three distinct LLM calls:

1. A summary/combination call to process and merge the raw source inputs  
2. A script generation call to rewrite the summary as a natural two-speaker podcast conversation  
3. Repeated text-to-speech calls to convert each line of dialogue into audio  

Steps 1 and 2 both use a large language model (GPT-4o), while step 3 uses a separate speech synthesis model (OpenAI TTS). The system includes a simple user interface and supports different types of input data. At this stage, the focus was on validating the core workflow.

---

## Part 2: Stakeholder impact

| Stakeholder        | Role / relationship to project | What they need | Risk if ignored | Influence / interest |
|------------------|------------------------------|----------------|-----------------|----------------------|
| Users            | Final users                  | A functioning UI, OpenAI subscription | Lack of interest from final user | High interest / Low influence |
| OpenAI           | LLM model provider           | Compensation through token usage | Need to change providers, decreased project quality, price volatility | Low interest / High influence |
| Team Members     | Developers, internal QA, marketers | Reliable LLM, funding, time, defined scope, technical knowledge, equipment | Failed project, inability to ship/maintain product, liability risks | High interest / High influence |
| Legal / Data Privacy | Legal advisors            | Terms and conditions, compliant implementation | Legal penalties, liability risks | Low influence / Low interest |
| Content Owners   | Owners of input content      | Proper usage, truthful outputs, compensation if commercial | Legal and reputational risks | Low influence / High interest |
| IT / Infrastructure | Technical support layer   | Hardware, subscriptions, funding, legal clarity | Collapse of technical base | High influence / Low interest |

---

## Part 3: From demo to “real project”

### 3.1 Operations
Currently, there is no monitoring, logging persistence, or incident handling beyond console prints.  
In production, structured logging, health checks, alerting, and clear ownership of failures would be required. Retry mechanisms for external API calls may also be necessary.

### 3.2 Security & compliance
The project loads API keys from environment variables but does not enforce access control or user isolation.  
A production version would require proper secret management (e.g., vaults), authentication, and restrictions on external inputs to prevent abuse.

### 3.3 Data lifecycle
Data is temporarily stored in local folders (`data/`, `outputs/`) and overwritten per run without retention policies.  
In production, retention, deletion rules, and handling of sensitive content must be defined and enforced.

### 3.4 Scope beyond demo
The system assumes valid inputs, reachable URLs, and successful API responses.  
A production system must handle:
- Broken PDFs  
- Invalid HTML parsing  
- API failures and timeouts  
- Multilingual input  
- Fallback behavior when stages fail  

### 3.5 Handoff / maintainability
The current system is modular but lacks formal documentation.  
In production, documentation, usage guidelines, and clear ownership boundaries are required.

---

## Part 4: Revision brief

### Before
The project was framed as a tool converting text, PDFs, and URLs into a podcast. The focus was on getting the pipeline working end-to-end with a functional UI and LLM/TTS integration.

Assumptions:
- Single user on a local machine  
- Only team members interact with the code  
- API reliability  
- One successful run = success  

### After
After considering stakeholders and production constraints, the scope changes:

- Include legal, infrastructure, and content ownership considerations  
- Reframe as a structured content-processing pipeline  
- Define clear system boundaries:
  - reliable ingestion  
  - controlled API usage  
  - defined output expectations  

Adjustments:
- Narrow MVP scope (fewer input types, stricter validation)  
- Add:
  - error handling  
  - logging  
  - data handling policies  

Goal shifts from **demo success** to **system viability beyond demo**.