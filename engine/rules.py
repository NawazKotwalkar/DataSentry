"""Applies user-defined validation rules loaded from YAML/JSON config.

Supported rule types:
  not_null:      column must have no nulls
  unique:        column must have no duplicate values
  min_value:     numeric column must be >= value
  max_value:     numeric column must be <= value
  allowed_values: column values must be within a given set
  regex:         column values must match a regex pattern
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


@dataclass
class RuleViolation:
    rule_name: str
    column: str
    rule_type: str
    violation_count: int
    violation_pct: float
    examples: list[Any] = field(default_factory=list)


def load_rules(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(text)
    elif path.suffix == ".json":
        data = json.loads(text)
    else:
        raise ValueError(f"Unsupported rules file extension: {path.suffix}")
    return data.get("rules", [])


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 2) if total else 0.0


def apply_rule(df: pd.DataFrame, rule: dict[str, Any]) -> RuleViolation:
    name = rule.get("name", rule.get("column", "unnamed_rule"))
    column = rule["column"]
    rule_type = rule["type"]

    if column not in df.columns:
        return RuleViolation(name, column, rule_type, violation_count=len(df), violation_pct=100.0,
                              examples=["column not found"])

    series = df[column]
    total = len(series)

    if rule_type == "not_null":
        mask = series.isna()
    elif rule_type == "unique":
        mask = series.duplicated(keep=False)
    elif rule_type == "min_value":
        mask = series < rule["value"]
    elif rule_type == "max_value":
        mask = series > rule["value"]
    elif rule_type == "allowed_values":
        allowed = set(rule["values"])
        mask = ~series.isin(allowed)
    elif rule_type == "regex":
        pattern = re.compile(rule["pattern"])
        non_null = series.dropna().astype(str)
        mask = ~non_null.str.match(pattern)
        mask = mask.reindex(series.index, fill_value=False)
    else:
        raise ValueError(f"Unknown rule type: {rule_type}")

    violations = series[mask]
    return RuleViolation(
        rule_name=name,
        column=column,
        rule_type=rule_type,
        violation_count=int(mask.sum()),
        violation_pct=_pct(int(mask.sum()), total),
        examples=violations.head(3).tolist(),
    )


def apply_rules(df: pd.DataFrame, rules: list[dict[str, Any]]) -> list[RuleViolation]:
    return [apply_rule(df, rule) for rule in rules]
