# redcheck/evaluator.py
import re
from typing import Dict, Any, List

class RedCheck:
    def __init__(self):
        # Basic stopwords for lexical noise filtering (English & Spanish)
        self.stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "el", "la", "los", "las", "y", "o", "pero", "en", "de", "a", "por"}

    def _extract_numbers(self, text: str) -> set:
        return set(re.findall(r'\b\d+\b', text))

    def _extract_years(self, text: str) -> set:
        return set(re.findall(r'\b(19\d{2}|20\d{2})\b', text))

    def _check_negation(self, text: str) -> bool:
        negations = {"not", "never", "no", "without", "ningún", "ninguno", "jamás", "nunca", "sin"}
        words = set(re.findall(r'\b\w+\b', text.lower()))
        return not words.isdisjoint(negations)

    def _calculate_lexical_overlap(self, context: str, response: str) -> float:
        ctx_words = set(re.findall(r'\b\w+\b', context.lower())) - self.stopwords
        res_words = set(re.findall(r'\b\w+\b', response.lower())) - self.stopwords
        
        if not ctx_words:
            return 0.0
        
        intersection = ctx_words.intersection(res_words)
        overlap = len(intersection) / len(ctx_words)
        return round(overlap * 100, 2)

    def _calculate_business_impact(self, reasons: List[str]) -> Dict[str, Any]:
        """
        Translates technical failure heuristics into financial and business risk metrics.
        This is the core differentiator for executive dashboards and ROI justification.
        """
        if not reasons or "No factual contradictions or polarity conflicts found offline." in reasons:
            return None

        # Heuristic classification based on failure reasons
        joined_reasons = " ".join(reasons).lower()
        
        if "unmatched numbers" in joined_reasons:
            return {
                "severity": "HIGH",
                "category": "pricing_or_metric_hallucination",
                "risk_usd": 50.0  # Default baseline risk for unauthorized number generation
            }
        elif "temporal hallucination" in joined_reasons:
            return {
                "severity": "MEDIUM",
                "category": "temporal_inconsistency",
                "risk_usd": 20.0
            }
        elif "polarity conflict" in joined_reasons:
            return {
                "severity": "CRITICAL",
                "category": "logic_inversion_error",
                "risk_usd": 100.0 # High risk due to negation mismatch (e.g., saying "is safe" instead of "is not safe")
            }
        
        return {
            "severity": "LOW",
            "category": "general_deviation",
            "risk_usd": 10.0
        }

    def evaluate_hallucination(self, context: str, response: str) -> Dict[str, Any]:
        # 1. Key entity extraction
        ctx_nums = self._extract_numbers(context)
        res_nums = self._extract_numbers(response)
        
        ctx_years = self._extract_years(context)
        res_years = self._extract_years(response)

        # 2. Negation and Polarity analysis
        ctx_neg = self._check_negation(context)
        res_neg = self._check_negation(response)

        reasons = []
        status = "PASS"

        # Strict numeric collision check
        if ctx_nums and res_nums:
            if not res_nums.issubset(ctx_nums):
                foreign_nums = res_nums - ctx_nums
                if foreign_nums:
                    status = "FAIL"
                    reasons.append(f"Unmatched numbers detected: {list(foreign_nums)}")

        # Temporal/Year collision check
        if ctx_years and res_years:
            if not res_years.issubset(ctx_years):
                status = "FAIL"
                reasons.append(f"Temporal hallucination detected. Context years: {list(ctx_years)}, Response years: {list(res_years)}")

        # Polarity inversion check via negation
        if ctx_neg != res_neg:
            status = "FAIL"
            reasons.append("Polarity conflict detected: negation mismatch between context and response.")

        # 3. Quantitative lexical coverage metrics
        coverage_score = self._calculate_lexical_overlap(context, response)

        # 4. Generate business impact metrics if failure occurs
        final_reasons = reasons if reasons else ["No factual contradictions or polarity conflicts found offline."]
        business_impact = self._calculate_business_impact(final_reasons) if status == "FAIL" else None

        return {
            "status": status,
            "lexical_coverage_percent": coverage_score,
            "reasons": final_reasons,
            "business_impact": business_impact
        }
