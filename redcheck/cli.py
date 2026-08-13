import argparse
import sys
from redcheck.batch import audit_csv_file

def main():
    parser = argparse.ArgumentParser(description="RedCheck CLI - Offline LLM Hallucination and Bias Auditor")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Comando audit para ficheros por lotes (CSV)
    audit_parser = subparsers.add_parser("audit", help="Audit a batch of responses from a CSV file")
    audit_parser.add_argument("--file", required=True, help="Path to the CSV benchmark file")
    audit_parser.add_argument("--output", help="Path to save the output JSON report")
    audit_parser.add_argument("--html", help="Path to save the visual HTML report")

    args = parser.parse_args()

    if args.command == "audit":
        try:
            print(f"[*] Running RedCheck offline audit on: {args.file}...")
            report = audit_csv_file(args.file, output_json=args.output, output_html=args.html)
            
            print("\n[+] Audit completed successfully!")
            print(f"    - Total Evaluated: {report['summary']['total_evaluated']}")
            print(f"    - Passed: {report['summary']['passed']}")
            print(f"    - Failed: {report['summary']['failed']}")
            print(f"    - Pass Rate: {report['summary']['pass_rate_percent']}%")
            
            if args.output:
                print(f"    - JSON Report saved to: {args.output}")
            if args.html:
                print(f"    - HTML Visual Report saved to: {args.html}")
                
        except Exception as e:
            print(f"[!] Error during audit: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
