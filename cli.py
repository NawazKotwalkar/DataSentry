"""DataSentry CLI — run audits without a server.

Usage:
    python cli.py audit data.csv
    python cli.py audit data.csv --rules config/rules.example.yaml --key-columns id
"""
from __future__ import annotations

import argparse
import json
import sys

import pandas as pd
import yaml

from engine.audit import run_audit


def _load_cost_config(path: str | None) -> dict | None:
    if not path:
        return None
    with open(path) as f:
        return yaml.safe_load(f)


def _load_rules(path: str | None) -> list[dict]:
    if not path:
        return []
    with open(path) as f:
        data = yaml.safe_load(f) if path.endswith((".yaml", ".yml")) else json.load(f)
    return data.get("rules", [])


def cmd_audit(args: argparse.Namespace) -> None:
    df = pd.read_csv(args.file)

    key_columns = args.key_columns.split(",") if args.key_columns else None
    rule_defs = _load_rules(args.rules)
    cost_config = _load_cost_config(args.cost_config)

    report = run_audit(
        df,
        key_columns=key_columns,
        rule_defs=rule_defs,
        cost_config=cost_config,
    )

    print(f"\nDataSentry Audit — {args.file}")
    print(f"Run at: {report.run_at}")
    print(f"Rows: {report.row_count}  Columns: {report.column_count}")
    print(f"\nHealth score: {report.score.dataset_score}/100")
    for component, value in report.score.component_scores.items():
        print(f"  {component:>16}: {value}")

    print(f"\nSeverity-weighted cost estimate: ${report.cost_estimate.total_cost:,.2f}")
    print("  (configurable heuristic — see config/cost_config.yaml — not a validated financial figure)")
    for component, value in report.cost_estimate.breakdown.items():
        if value:
            print(f"  {component:>20}: ${value:,.2f}")

    if report.issues:
        print(f"\nIssues found ({len(report.issues)}):")
        for issue in report.issues:
            col = f" [{issue['column']}]" if issue["column"] else ""
            print(f"  - {issue['type']}{col}: {issue['detail']}")
    else:
        print("\nNo issues found.")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(
                {
                    "run_at": report.run_at,
                    "row_count": report.row_count,
                    "column_count": report.column_count,
                    "score": report.score.dataset_score,
                    "component_scores": report.score.component_scores,
                    "total_cost": report.cost_estimate.total_cost,
                    "cost_breakdown": report.cost_estimate.breakdown,
                    "issues": report.issues,
                },
                f,
                indent=2,
                default=str,
            )
        print(f"\nFull JSON report written to {args.json}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="datasentry", description="DataSentry — data quality auditing engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Run a data quality audit against a CSV file")
    audit_parser.add_argument("file", help="Path to the CSV file to audit")
    audit_parser.add_argument("--rules", help="Path to a YAML/JSON rules config file", default=None)
    audit_parser.add_argument("--cost-config", help="Path to a YAML cost config file", default=None)
    audit_parser.add_argument("--key-columns", help="Comma-separated key columns for duplicate detection", default=None)
    audit_parser.add_argument("--json", help="Write full report to this JSON path", default=None)
    audit_parser.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
