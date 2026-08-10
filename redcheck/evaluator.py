class RedCheck:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def evaluate_relevance(self, prompt: str, response: str) -> dict:
        """
        Evalúa si la respuesta entregada tiene relación con el prompt.
        Retorna un score entre 0.0 y 1.0.
        """
        if not prompt or not response:
            return {"score": 0.0, "reason": "Prompt o respuesta vacíos."}
        
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        common = prompt_words.intersection(response_words)
        score = len(common) / max(len(prompt_words), 1)
        
        return {
            "score": round(min(score, 1.0), 2),
            "status": "PASS" if score > 0.2 else "FLAGGED"
        }

checker = RedCheck()

result = checker.evaluate_relevance(
    prompt="How do I configure an SMTP server?",
    response="You need a domain, DNS records, and an SMTP port."
)

print(result)
import os
import json
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class RedCheck:
    """
    Core evaluation engine for LLM outputs, hallucination detection,
    and response quality verification using OpenAI or Anthropic models.
    """

    def __init__(
        self, 
        provider: str = "auto", 
        api_key: Optional[str] = None
    ):
        """
        Initialize RedCheck evaluator.
        
        :param provider: 'openai', 'anthropic', or 'auto' (selects based on available API keys)
        :param api_key: Explicit API key string (optional)
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.openai_client = None
        self.anthropic_client = None

        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Sets up API clients depending on environment keys and provider settings."""
        openai_key = self.api_key if self.provider == "openai" else os.getenv("OPENAI_API_KEY")
        anthropic_key = self.api_key if self.provider == "anthropic" else os.getenv("ANTHROPIC_API_KEY")

        if OPENAI_AVAILABLE and (openai_key or self.api_key) and self.provider in ["auto", "openai"]:
            self.openai_client = OpenAI(api_key=openai_key or self.api_key)

        if ANTHROPIC_AVAILABLE and (anthropic_key or self.api_key) and self.provider in ["auto", "anthropic"]:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key or self.api_key)

    def evaluate_relevance(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Evaluates whether the response accurately answers the prompt.
        Prioritizes Anthropic/OpenAI if configured, falling back to lexical matching.
        """
        if not prompt or not response:
            return {"score": 0.0, "status": "FLAGGED", "reason": "Empty prompt or response."}

        # Try Anthropic Claude evaluation
        if self.provider == "anthropic" and self.anthropic_client:
            return self._evaluate_with_anthropic(prompt, response)

        # Try OpenAI GPT evaluation
        if self.provider == "openai" and self.openai_client:
            return self._evaluate_with_openai(prompt, response)

        # Auto-detect available provider
        if self.provider == "auto":
            if self.anthropic_client:
                return self._evaluate_with_anthropic(prompt, response)
            if self.openai_client:
                return self._evaluate_with_openai(prompt, response)

        # Fallback if no LLM clients are active
        return self._evaluate_lexical(prompt, response)

    def _evaluate_lexical(self, prompt: str, response: str) -> Dict[str, Any]:
        """Fallback evaluation based on lexical overlap."""
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())

        common = prompt_words.intersection(response_words)
        score = len(common) / max(len(prompt_words), 1)
        final_score = round(min(score, 1.0), 2)

        return {
            "score": final_score,
            "status": "PASS" if final_score > 0.2 else "FLAGGED",
            "method": "lexical_fallback"
        }

    def _evaluate_with_openai(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluates using OpenAI GPT-4o-mini."""
        system_instructions = (
            "You are an expert AI Evaluator for RedCheck. "
            "Analyze if the given Response accurately answers the Prompt without hallucinations. "
            "Respond strictly in valid JSON format with keys: 'score' (float 0.0 to 1.0), "
            "'status' ('PASS' or 'FLAGGED'), and 'reason' (brief explanation)."
        )
        user_content = f"PROMPT: {prompt}\nRESPONSE: {response}"

        try:
            res = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0
            )
            result = json.loads(res.choices[0].message.content)
            result["method"] = "llm_openai_gpt4o_mini"
            return result
        except Exception as e:
            fallback = self._evaluate_lexical(prompt, response)
            fallback["error"] = str(e)
            return fallback

    def _evaluate_with_anthropic(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluates using Anthropic Claude 3.5 Sonnet."""
        system_instructions = (
            "You are an expert AI Evaluator for RedCheck. "
            "Analyze if the given Response accurately answers the Prompt without hallucinations. "
            "Respond strictly in valid JSON format with keys: 'score' (float 0.0 to 1.0), "
            "'status' ('PASS' or 'FLAGGED'), and 'reason' (brief explanation)."
        )
        user_content = f"PROMPT: {prompt}\nRESPONSE: {response}\nReturn JSON only."

        try:
            res = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=system_instructions,
                messages=[{"role": "user", "content": user_content}]
            )
            raw_text = res.content[0].text
            result = json.loads(raw_text)
            result["method"] = "llm_anthropic_claude"
            return result
        except Exception as e:
            fallback = self._evaluate_lexical(prompt, response)
            fallback["error"] = str(e)
            return fallback
        import os
import re

class RedCheck:
    def __init__(self, openai_api_key=None, anthropic_api_key=None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

    def evaluate_relevance(self, prompt: str, response: str) -> dict:
        """
        Evaluates whether the response is relevant to the provided prompt.
        """
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))

        if not prompt_words:
            return {"score": 0.0, "status": "FAIL", "method": "lexical_fallback"}

        overlap = prompt_words.intersection(response_words)
        score = round(len(overlap) / len(prompt_words), 2)
        status = "PASS" if score >= 0.3 else "FAIL"

        return {
            "score": score,
            "status": status,
            "method": "lexical_fallback"
        }

    def evaluate_hallucination(self, context: str, response: str) -> dict:
        """
        Evaluates potential hallucinations by checking response factual overlap against a reference context.
        High score (~1.0) = High fidelity / No hallucination detected.
        Low score (~0.0) = Likely hallucination.
        """
        context_words = set(re.findall(r'\w+', context.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))

        if not response_words:
            return {"score": 0.0, "status": "FAIL", "method": "hallucination_check"}

        overlap = response_words.intersection(context_words)
        score = round(len(overlap) / len(response_words), 2)
        status = "PASS" if score >= 0.4 else "FAIL"

        return {
            "score": score,
            "status": status,
            "method": "hallucination_check"
        }
    from redcheck import RedCheck

def test_relevance():
    checker = RedCheck()
    res = checker.evaluate_relevance("What time is it?", "It is 3 PM")
    assert "score" in res
    assert "status" in res

def test_hallucination():
    checker = RedCheck()
    context = "The cat is black and lives in the house."
    
    # Faithful response
    res_faithful = checker.evaluate_hallucination(context, "The black cat lives in the house.")
    assert res_faithful["status"] == "PASS"

    # Hallucinated response
    res_hallucinated = checker.evaluate_hallucination(context, "The green dog flies over the ocean.")
    assert res_hallucinated["status"] == "FAIL"