# RedCheck 🛡️

Lightweight evaluation engine for LLM outputs, hallucination detection, and relevance verification.

## Installation

```bash
pip install redcheck
```

## Quick Start

```python
from redcheck import RedCheck

checker = RedCheck()

result = checker.evaluate_relevance(
    prompt="How do I configure an SMTP server?",
    response="You need a domain, DNS records, and an SMTP port."
)

print(result)
```
