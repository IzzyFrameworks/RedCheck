import re
from typing import Dict, Any, List, Set

class RedCheck:
    def __init__(self, provider: str = "local", api_key: str = None):
        self.provider = provider
        self.api_key = api_key
        
        # Palabras de polaridad (Español + Inglés)
        self.negation_words: Set[str] = {
            "not", "never", "no", "without", "none", "neither", "nor",
            "no", "nunca", "jamas", "jamás", "sin", "tampoco", "ningun", "ningún", "ninguna"
        }

    def _extract_numbers(self, text: str) -> Set[str]:
        return set(re.findall(r'\b\d+(?:\.\d+)?\b', text))

    def _extract_entities(self, text: str) -> Set[str]:
        # Extrae palabras con mayúscula inicial (Nombres propios, Organizaciones)
        words = re.findall(r'\b[A-Z][a-zA-Z0-9_-]+\b', text)
        return {w.lower() for w in words}

    def _check_polarity(self, text: str) -> Set[str]:
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return words.intersection(self.negation_words)

    def evaluate_hallucination(self, context: str, response: str) -> Dict[str, Any]:
        # 1. Validación de Entidades Numéricas / Fechas
        context_nums = self._extract_numbers(context)
        response_nums = self._extract_numbers(response)
        num_mismatches = response_nums - context_nums
        
        # 2. Control de Polaridad y Negación
        context_negs = self._check_polarity(context)
        response_negs = self._check_polarity(response)
        polarity_conflict = len(context_negs) != len(response_negs)

        # 3. Detección de Entidades / Nombres Propios
        context_entities = self._extract_entities(context)
        response_entities = self._extract_entities(response)
        entity_mismatches = response_entities - context_entities

        # 4. Cálculo del Índice de Fidelidad Factual (Score 0.0 a 1.0)
        score = 1.0
        reasons = []

        if num_mismatches:
            score -= 0.4
            reasons.append(f"Incongruencia numérica/fechas detectada: {list(num_mismatches)}")

        if polarity_conflict:
            score -= 0.4
            reasons.append("Conflicto de polaridad/negación entre contexto y respuesta")

        if entity_mismatches:
            score -= 0.3
            reasons.append(f"Entidades no fundamentadas o alteradas: {list(entity_mismatches)}")

        score = max(0.0, round(score, 2))
        status = "PASS" if score >= 0.7 else "FAIL"
        reason_str = " | ".join(reasons) if reasons else "Verificación factual correcta"

        return {
            "status": status,
            "factuality_score": score,
            "reason": reason_str,
            "metrics": {
                "numeric_mismatches": list(num_mismatches),
                "polarity_conflict": polarity_conflict,
                "unsupported_entities": list(entity_mismatches)
            }
        }
