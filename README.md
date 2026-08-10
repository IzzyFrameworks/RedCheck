# RedCheck 🛡️

[![PyPI version](https://img.shields.io/pypi/v/redcheck.svg)](https://pypi.org/project/redcheck/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lightweight evaluation engine for LLM outputs, hallucination detection, and relevance verification using OpenAI, Anthropic Claude, or lexical fallbacks.

## Installation

```bash
pip install redcheck
```

To update to the latest version:

```bash
pip install --upgrade redcheck
```

## Quick Start

```python
from redcheck import RedCheck

# Auto-detects OpenAI or Anthropic API keys
checker = RedCheck()

result = checker.evaluate_relevance(
    prompt="How do I configure an SMTP server?",
    response="You need a domain, DNS records, and an SMTP port."
)

print(result)
```
