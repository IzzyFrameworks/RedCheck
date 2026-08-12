<p align="center">
  <img src="assets/logo.png" alt="RedCheck Logo" width="180"/>
</p>

# RedCheck 🔍

Lightweight evaluation engine for LLM outputs and hallucination detection.

---

## 💾 Installation

```bash
pip install redcheck
```

---

## ⚡ Quickstart

### 1. Local Evaluation (Offline & Free)

> **No API keys required/Users/nikki/redcheck* RedCheck evaluates text directly on your machine.

```python
from redcheck import RedCheck

evaluator = RedCheck()

context = "The product was released in 2024 and includes free support."
response = "The product was released in 1990 without support."

result = evaluator.evaluate_hallucination(context=context, response=response)

print(f"Status: {result['status']}")
print(f"Reason: {result['reason']}")
```

---

### 2. Using Cloud LLMs (Optional)

If you want to leverage external models like OpenAI or Anthropic for complex semantic reasoning, simply pass your API key:

```python
from redcheck import RedCheck

evaluator = RedCheck(provider="openai", api_key="your-openai-api-key")

result = evaluator.evaluate_hallucination(
    context="Python 3.12 introduces improved error messages.",
    response="Python 3.12 has worse error messages."
)

print(result)
```

> **Note:** If your Cloud API key runs out of quota (Error 429), RedCheck automatically switches to the **Smart Local Engine** to prevent pipeline crashes.

---

## ⚙️ How the Local Engine Works

RedCheck's local engine uses a multi-stage validation rule set:

| Feature | Description | Example |
| :--- | :--- | :--- |
| **Numeric & Date Check** | Extracts and verifies numbers/years between context and response. | `2020` vs `2024` ➔ **FAIL** |
| **Polarity & Negation** | Scans for polarity flippers (*not, never, no, without*). | `"is active"` vs `"is not active"` ➔ **FAIL** |
| **Text Similarity** | Computes baseline lexical alignment. | Low overlap ➔ **FAIL** |

---

## 🛣️ Roadmap & SaaS Version

We are actively developing **RedCheck SaaS Premium**:

* 📊 **Real-time Dashboard:** Monitor hallucinations, latency, and token costs.
* 🗝️ **Centralized Key & Token Management:** Manage usage across teams.
* 📈 **Historical Metrics & Analytics:** Track model performance over time.

---

## 📄 License

RedCheck is open-source software licensed under the **MIT License**.
