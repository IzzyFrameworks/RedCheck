from redcheck.batch import BatchAuditor

auditor = BatchAuditor()
results = auditor.audit_csv("benchmark_sample.csv")

for r in results:
    print(f"[{r['id']}] Status: {r['status']}")
    print(f"  Reason: {r['reason']}\n")

auditor.export_report(results)
