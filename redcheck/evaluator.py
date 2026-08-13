import re
from datetime import datetime

class RedCheck:
    def __init__(self):
        # Palabras vacías básicas en inglés/español para filtrar ruido léxico
        self.stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "el", "la", "los", "las", "y", "o", "pero", "en", "de", "a", "por"}

    def _extract_numbers(self, text):
        return set(re.findall(r'\b\d+\b', text))

    def _extract_years(self, text):
        return set(re.findall(r'\b(19\d{2}|20\d{2})\b', text))

    def _check_negation(self, text):
        negations = {"not", "never", "no", "without", "ningún", "ninguno", "jamás", "nunca", "sin"}
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return not words.isdisjoint(negations)

    def _calculate_lexical_overlap(self, context, response):
        ctx_words = set(re.findall(r'\b\w+\b', context.lower())) - self.stopwords
        res_words = set(re.findall(r'\b\w+\b', response.lower())) - self.stopwords
        
        if not ctx_words:
            return 0.0
        
        intersection = ctx_words.intersection(res_words)
        overlap = len(intersection) / len(ctx_words)
        return round(overlap * 100, 2)

    def evaluate_hallucination(self, context: str, response: str) -> dict:
        # 1. Extracción de entidades clave
        ctx_nums = self._extract_numbers(context)
        res_nums = self._extract_numbers(response)
        
        ctx_years = self._extract_years(context)
        res_years = self._extract_years(response)

        # 2. Análisis de Negación y Polaridad
        ctx_neg = self._check_negation(context)
        res_neg = self._check_negation(response)

        reasons = []
        status = "PASS"

        # Comprobación de colisión numérica estricta
        if ctx_nums and res_nums:
            if not res_nums.issubset(ctx_nums):
                foreign_nums = res_nums - ctx_nums
                if foreign_nums:
                    status = "FAIL"
                    reasons.append(f"Unmatched numbers detected: {list(foreign_nums)}")

        # Comprobación de colisión de años/fechas
        if ctx_years and res_years:
            if not res_years.issubset(ctx_years):
                status = "FAIL"
                reasons.append(f"Temporal hallucination detected. Context years: {list(ctx_years)}, Response years: {list(res_years)}")

        # Comprobación de inversión de polaridad por negación
        if ctx_neg != res_neg:
            status = "FAIL"
            reasons.append("Polarity conflict detected: negation mismatch between context and response.")

        # 3. Métricas cuantitativas de cobertura léxica
        coverage_score = self._calculate_lexical_overlap(context, response)

        return {
            "status": status,
            "lexical_coverage_percent": coverage_score,
            "reasons": reasons if reasons else ["No factual contradictions or polarity conflicts found offline."]
        }
