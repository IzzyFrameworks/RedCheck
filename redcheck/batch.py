import csv
import json
from pathlib import Path
from .evaluator import RedCheck

class BatchAuditor:
    """
    Motor de auditoría masiva (Batch Testing) para RedCheck.
    Permite evaluar cientos de prompts, contextos y respuestas en masa
    de forma completamente local y offline. El 'Excel' de los tests de LLM.
    """
    def __init__(self):
        self.evaluator = RedCheck()

    def audit_csv(self, file_path: str) -> list:
        results = []
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"No se encuentra el archivo de benchmark: {file_path}")

        with open(path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                context = row.get("context", "")
                response = row.get("response", "")
                test_id = row.get("id", "UNKNOWN")

                evaluation = self.evaluator.evaluate_hallucination(context=context, response=response)
                
                results.append({
                    "id": test_id,
                    "status": evaluation["status"],
                    "factuality_score": evaluation["factuality_score"],
                    "reason": evaluation["reason"],
                    "metrics": evaluation["metrics"]
                })
        
        return results

    def export_report(self, results: list, output_path: str = "redcheck_report.json"):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"📊 Informe de auditoría masiva exportado con éxito a: {output_path}")
