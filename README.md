Markdown<div align="center">

  <img src="assets/logo.png" alt="RedCheck Logo" width="180" />

  # 🔴 RedCheck

  **Local-first, fast, and lightweight hallucination detection for LLM applications.**

  [![PyPI version](https://badge.fury.io/py/redcheck.svg)](https://badge.fury.io/py/redcheck)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

</div>

---

## ⚡ What is RedCheck?

**RedCheck** is an evaluation framework designed to catch hallucinations, factual contradictions, and polarity mismatches in LLM-generated responses. 

Starting from **v0.3.5**, RedCheck features an **intelligent offline local engine** that validates facts, dates, numbers, and negation constraints without requiring paid external API keys.

---

## ✨ Key Features

* **🧠 Smart Local Engine (100% Free & Offline):**
  * **Strict Entity Matching:** Detects numerical and date discrepancies (e.g., comparing `1990` vs `2024`).
  * **Polarity Conflict Detection:** Flags contradictions introduced by negation keywords (`not`, `never`, `without`, `no`).
* **☁️ Optional Cloud LLMs:** Seamlessly plug in **OpenAI** or **Anthropic** API keys for hybrid/advanced evaluations when needed.
* **⚡ High Performance:** Zero latency overhead when running in local mode.
* **🛡️ Fallback Resilient:** Automatically falls back to the smart local engine if API rate limits (e.g., HTTP 429) or connection issues occur.

---

## 🚀 Quickstart

### 1. Installation

```bash
pip install redcheck
2. Local Evaluation (Offline & Free)No API keys required! RedCheck evaluates text directly on your machine.Pythonfrom redcheck import RedCheck

evaluator = RedCheck()

context = "The product was released in 2024 and includes free support."
response = "The product was released in 1990 without support."

result = evaluator.evaluate_hallucination(context=context, response=response)

print(f"Status: {result['status']}") # Output: FAIL
print(f"Reason: {result['reason']}") # Output: Detected entity or polarity mismatch
🔌 Using Cloud LLMs (Optional)If you want to leverage external models like OpenAI or Anthropic for complex semantic reasoning, simply pass your API key:OpenAI IntegrationPythonfrom redcheck import RedCheck

evaluator = RedCheck(provider="openai", api_key="your-openai-api-key")

result = evaluator.evaluate_hallucination(
    context="Python 3.12 introduces improved error messages.",
    response="Python 3.12 has worse error messages."
)

print(result)
Note: If your Cloud API key runs out of quota (Error 429), RedCheck automatically switches to the Smart Local Engine to prevent pipeline crashes.⚙️ How the Local Engine WorksRedCheck's local engine uses a multi-stage validation rule set:FeatureDescriptionExampleNumeric & Date CheckExtracts and verifies numbers/years between context and response.2020 vs 2024 ➔ FAILPolarity & NegationScans for polarity flippers (not, never, no, without)."is active" vs "is not active" ➔ FAILText SimilarityComputes baseline lexical alignment.Low overlap ➔ FAIL🛣️ Roadmap & SaaS VersionWe are actively developing RedCheck SaaS Premium:📊 Real-time Dashboard: Monitor hallucinations, latency, and token costs.🗝️ Centralized Key & Token Management.📈 Historical Metrics & Analytics.Stay tuned for updates!📄 LicenseRedCheck is open-source software licensed under the MIT License.
