import sys
import argparse
from redcheck.batch import BatchAuditor

def main():
    parser = argparse.ArgumentParser(
        description="RedCheck CLI: El motor definitivo de auditoría y testeo masivo de LLMs."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando 'audit'
    audit_parser = subparsers.add_add_parser if hasattr(subparsers, 'add_add_parser') else subparsers.add_parser
    audit_parser("audit", help="Audita un archivo CSV de pruebas por lotes.")
    audit_parser.add_argument(
        "--file", "-f", 
        required=True, 
        help="Ruta al archivo CSV con los casos de prueba (id, context, response)"
    )
    audit_parser.add_argument(
        "--output", "-o", 
        default="redcheck_report.json", 
        help="Ruta de salida para el informe JSON (por defecto: redcheck_report.json)"
    )

    args = parser.parse_args()

    if args.command == "audit":
        print(f"🚀 Iniciando auditoría masiva con RedCheck usando: {args.file}...")
        try:
            auditor = BatchAuditor()
            results = auditor.audit_csv(args.file)
            
            passed = sum(1 for r in results if r["status"] == "PASS")
            failed = sum(1 for r in results if r["status"] == "FAIL")
            
            for r in results:
                print(f"[{r['id']}] Status: {r['status']}")
                print(f"  Reason: {r['reason']}\n")
                
            auditor.export_report(results, args.output)
            print(f"\n✨ Resumen de auditoría: {passed} aprobados, {failed} fallos detectados.")
        except Exception as e:
            print(f"❌ Error durante la auditoría: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
