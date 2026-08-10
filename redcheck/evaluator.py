import os
import json
import re
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
    Core evaluation engine for LLM outputs.
    Provides free smart lexical evaluation and API integrations for cloud providers.
    """

    STOPWORDS = {
        "is", "a", "an", "the", "in", "on", "at", "by", "for", "with", 
        "about", "against", "between", "into", "through", "during", 
        "before", "after", "above", "below", "to", "from", "up", "down", 
        "of", "and", "or", "and/or", "as", "was", "were", "be", "been", "being"
    }

    NEGATIONS = {"not", "no", "never", "without", "none", "cannot", "n't", "neither", "nor"}

    def __init__(
        self, 
        provider: str = "auto", 
        api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        
        self.openai_key = openai_api_key or api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_key = anthropic_api_key or api_key or os.getenv("ANTHROPIC_API_KEY")

        self.openai_client = None
        self.anthropic_client = None

        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Sets up API clients if explicitly provided or in environment."""
        if OPENAI_AVAILABLE and self.openai_key and self.provider in ["auto", "openai"]:
            self.openai_client = OpenAI(api_key=self.openai_key)

        if ANTHROPIC_AVAILABLE and self.anthropic_key and self.provider in ["auto", "anthropic"]:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)

    def evaluate_relevance(self, prompt: str, response: str) -> Dict[str, Any]:
        """Evaluates relevance using LLM APIs if available, otherwise local smart fallback."""
        if not prompt or not response:
            return {"score": 0.0, "status": "FLAGGED", "reason": "Empty prompt or response."}

        if self.provider == "anthropic" and self.anthropic_client:
            return self._evaluate_with_anthropic(prompt, response)

        if self.provider == "openai" and self.openai_client:
            return self._evaluate_with_openai(prompt, response)

        if self.provider == "auto":
            if self.anthropic_client:
                return self._evaluate_with_anthropic(prompt, response)
            if self.openai_client:
                return self._evaluate_with_openai(prompt, response)

        return self._evaluate_lexical(prompt, response)

    def evaluate_hallucination(self, context: str, response: str) -> Dict[str, Any]:
        """
        Smart local evaluation for hallucinations without needing paid APIs.
        Checks for word overlap, numerical mismatches, and negation conflicts.
        """
        if not context or not response:
            return {"score": 0.0, "status": "FAIL", "method": "hallucination_check"}

        context_words = {w for w in re.findall(r'\w+', context.lower()) if w not in self.STOPWORDS}
        response_words = {w for w in re.findall(r'\w+', response.lower()) if w not in self.STOPWORDS}

        if not response_words:
            return {"score": 0.0, "status": "FAIL", "method": "hallucination_check"}

        # 1. Comprobación de números/fechas (Extracción estricta)
        context_numbers = set(re.findall(r'\b\d+\b', context))
        response_numbers = set(re.findall(r'\b\d+\b', response))
        
        # Si la respuesta menciona números que NO están en el contexto -> ALUCINACIÓN
        if response_numbers and not response_numbers.issubset(context_numbers):
            return {
                "score": 0.10,
                "status": "FAIL",
                "method": "hallucination_check",
                "reason": f"Mismatch in numeric entities. Context: {context_numbers}, Response: {response_numbers}"
            }

        # 2. Comprobación de Negaciones (Conflicto de polaridad)
        context_negations = bool(set(re.findall(r'\w+', context.lower())).intersection(self.NEGATIONS))
        response_negations = bool(set(re.findall(r'\w+', response.lower())).intersection(self.NEGATIONS))

        # Si una tiene negación y la otra no -> Probable contradicción directa
        if context_negations != response_negations:
            return {
                "score": 0.0,
                "status": "FAIL",
                "method": "hallucination_check",
                "reason": "Direct negation/contradiction conflict detected."
            }

        # 3. Solapamiento Léxico Estándar
        overlap = response_words.intersection(context_words)
        score = round(len(overlap) / len(response_words), 2)
        status = "PASS" if score >= 0.6 else "FAIL"

        return {
            "score": score,
            "status": status,
            "method": "hallucination_check"
        }

    def _evaluate_lexical(self, prompt: str, response: str) -> Dict[str, Any]:
        """Local smart fallback evaluation for relevance."""
        prompt_words = set(re.findall(r'\w+', prompt.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))

        if not prompt_words:
            return {"score": 0.0, "status": "FAIL", "method": "lexical_fallback"}

        common = prompt_words.intersection(response_words)
        score = round(len(common) / len(prompt_words), 2)

        return {
            "score": score,
            "status": "PASS" if score >= 0.3 else "FLAGGED",
            "method": "lexical_fallback"
        }

    def _evaluate_with_openai(self, prompt: str, response: str) -> Dict[str, Any]:
        system_instructions = (
            "You are an expert AI Evaluator for RedCheck. "
            "Analyze if the given Response accurately answers the Prompt without hallucinations. "
            "Respond strictly in valid JSON format with keys: 'score' (float 0.0 to 1.0), "
            "'status' ('PASS' or 'FLAGGED'), and 'reason' (brief explanation)."
        )
        try:
            res = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": f"PROMPT: {prompt}\nRESPONSE: {response}"}
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
        system_instructions = (
            "You are an expert AI Evaluator for RedCheck. "
            "Analyze if the given Response accurately answers the Prompt without hallucinations. "
            "Respond strictly in valid JSON format with keys: 'score' (float 0.0 to 1.0), "
            "'status' ('PASS' or 'FLAGGED'), and 'reason' (brief explanation)."
        )
        try:
            res = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=system_instructions,
                messages=[{"role": "user", "content": f"PROMPT: {prompt}\nRESPONSE: {response}\nReturn JSON only."}]
            )
            result = json.loads(res.content[0].text)
            result["method"] = "llm_anthropic_claude"
            return result
        except Exception as e:
            fallback = self._evaluate_lexical(prompt, response)
            fallback["error"] = str(e)
            return fallback