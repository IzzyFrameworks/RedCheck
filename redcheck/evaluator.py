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
from redcheck import RedCheck

checker = RedCheck()

result = checker.evaluate_relevance(
    prompt="How do I configure an SMTP server?",
    response="You need a domain, DNS records, and an SMTP port."
)

print(result)
