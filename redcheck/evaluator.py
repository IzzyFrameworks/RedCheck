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
