import csv
import json
import os
from redcheck.evaluator import RedCheck

def audit_csv_file(file_path: str, output_json: str = None, output_html: str = None):
    checker = RedCheck()
    results = []
    
    passed_count = 0
    failed_count = 0

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The benchmark file '{file_path}' does not exist.")

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_id = row.get("id", "unknown")
            context = row.get("context", "")
            response = row.get("response", "")

            evaluation = checker.evaluate_hallucination(context, response)
            
            if evaluation["status"] == "PASS":
                passed_count += 1
            else:
                failed_count += 1

            results.append({
                "id": row_id,
                "context": context,
                "response": response,
                "evaluation": evaluation
            })

    summary = {
        "total_evaluated": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate_percent": round((passed_count / len(results)) * 100, 2) if results else 0.0
    }

    report = {
        "summary": summary,
        "details": results
    }

    # Guardar en JSON si se solicita
    if output_json:
        with open(output_json, mode='w', encoding='utf-8') as f_json:
            json.dump(report, f_json, indent=4, ensure_ascii=False)

    # Guardar en HTML si se solicita (¡Nuestro nuevo informe visual!)
    if output_html:
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RedCheck Audit Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        .container {{ max-width: 1000px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .summary-box {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ background: #334155; padding: 20px; border-radius: 8px; flex: 1; text-align: center; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #94a3b8; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #475569; font-size: 14px; }}
        th {{ background: #0f172a; color: #38bdf8; }}
        .badge-pass {{ background: #065f46; color: #34d399; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        .badge-fail {{ background: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        .reasons {{ font-size: 12px; color: #cbd5e1; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ RedCheck Audit Report</h1>
        <p>Generated automatically by RedCheck Offline Evaluation Engine.</p>
        
        <div class="summary-box">
            <div class="card">
                <h3>Total Evaluated</h3>
                <p>{summary['total_evaluated']}</p>
            </div>
            <div class="card">
                <h3>Passed</h3>
                <p style="color: #34d399;">{summary['passed']}</p>
            </div>
            <div class="card">
                <h3>Failed</h3>
                <p style="color: #f87171;">{summary['failed']}</p>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <p style="color: #38bdf8;">{summary['pass_rate_percent']}%</p>
            </div>
        </div>

        <h2>Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Lexical Coverage</th>
                    <th>Context & Response / Details</th>
                </tr>
            </thead>
            <tbody>
"""
        for item in results:
            status = item["evaluation"]["status"]
            badge_class = "badge-pass" if status == "PASS" else "badge-fail"
            coverage = item["evaluation"]["lexical_coverage_percent"]
            reasons = "<br>".join(item["evaluation"]["reasons"])
            
            html_content += f"""
                <tr>
                    <td><strong>{item['id']}</strong></td>
                    <td><span class="{badge_class}">{status}</span></td>
                    <td>{coverage}%</td>
                    <td>
                        <div><strong>Context:</strong> {item['context']}</div>
                        <div><strong>Response:</strong> {item['response']}</div>
                        <div class="reasons"><strong>Analysis:</strong> {reasons}</div>
                    </td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        with open(output_html, mode='w', encoding='utf-8') as f_html:
            f_html.write(html_content)

    return report
