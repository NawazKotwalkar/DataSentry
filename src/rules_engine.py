import pandas as pd
import numpy as np
from src.ingest import ingest

# Cost constants
COST_PER_NULL = 500
COST_PER_DUPLICATE = 50
COST_PER_OUTLIER = 300
COST_PER_NEGATIVE = 400


def check_nulls(df: pd.DataFrame) -> list:
    """Flag null values in any column."""
    results = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            cost = round(null_count * COST_PER_NULL)
            results.append({
                "rule": "Null Value Detected",
                "column": col,
                "issue_count": int(null_count),
                "estimated_cost_inr": cost,
                "severity": "HIGH" if cost > 10000 else "MEDIUM",
                "recommendation": f"Investigate {null_count} null values in '{col}'"
            })
    return results


def check_duplicates(df: pd.DataFrame) -> list:
    """Flag duplicate rows in any dataset."""
    results = []
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        cost = round(duplicate_count * COST_PER_DUPLICATE)
        results.append({
            "rule": "Duplicate Records Detected",
            "column": "ALL",
            "issue_count": int(duplicate_count),
            "estimated_cost_inr": cost,
            "severity": "HIGH" if duplicate_count > 100 else "MEDIUM",
            "recommendation": f"Remove {duplicate_count} duplicate records"
        })
    return results


def check_outliers(df: pd.DataFrame) -> list:
    """Auto-detect outliers using IQR on all numeric columns."""
    results = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)].shape[0]
        if outliers > 0:
            cost = round(outliers * COST_PER_OUTLIER)
            results.append({
                "rule": "Outlier Detected",
                "column": col,
                "issue_count": int(outliers),
                "estimated_cost_inr": cost,
                "severity": "HIGH" if cost > 10000 else "MEDIUM",
                "recommendation": f"{outliers} outliers in '{col}' — range [{round(lower,2)}, {round(upper,2)}]"
            })
    return results


def check_negative_values(df: pd.DataFrame) -> list:
    """Flag negative values in numeric columns where negatives are illogical."""
    results = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        # Skip columns that can logically be negative
        if any(word in col.lower() for word in ['id', 'index', 'code']):
            continue
        negatives = df[df[col] < 0].shape[0]
        if negatives > 0:
            cost = round(negatives * COST_PER_NEGATIVE)
            results.append({
                "rule": "Negative Value Detected",
                "column": col,
                "issue_count": int(negatives),
                "estimated_cost_inr": cost,
                "severity": "HIGH",
                "recommendation": f"{negatives} negative values in '{col}' — likely data entry errors"
            })
    return results


def check_high_cardinality(df: pd.DataFrame) -> list:
    """Flag text columns with suspiciously high unique value counts."""
    results = []
    text_cols = df.select_dtypes(include=['object']).columns

    for col in text_cols:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.9:
            results.append({
                "rule": "High Cardinality Detected",
                "column": col,
                "issue_count": int(df[col].nunique()),
                "estimated_cost_inr": 0,
                "severity": "MEDIUM",
                "recommendation": f"'{col}' has {round(unique_ratio*100, 1)}% unique values — possible free-text or ID column"
            })
    return results


def run_rules_engine(df: pd.DataFrame) -> dict:
    """Run all generic rules on any dataset."""
    all_issues = []
    all_issues.extend(check_nulls(df))
    all_issues.extend(check_duplicates(df))
    all_issues.extend(check_outliers(df))
    all_issues.extend(check_negative_values(df))
    all_issues.extend(check_high_cardinality(df))

    total_cost = sum(i["estimated_cost_inr"] for i in all_issues)
    critical = [i for i in all_issues if i["severity"] == "CRITICAL"]
    high = [i for i in all_issues if i["severity"] == "HIGH"]

    return {
        "total_issues": len(all_issues),
        "total_estimated_cost_inr": total_cost,
        "critical_issues": len(critical),
        "high_issues": len(high),
        "issues": all_issues
    }


if __name__ == "__main__":
    df, _ = ingest("data/raw/churn_dirty.csv")
    report = run_rules_engine(df)

    print("\n--- DataSentry Business Impact Report ---")
    print(f"Total Issues Found:{report['total_issues']}")
    print(f"Critical Issues:{report['critical_issues']}")
    print(f"High Severity:{report['high_issues']}")
    print(f"Total Cost (INR):₹{report['total_estimated_cost_inr']:,}")
    print("\nIssue Breakdown:")
    for issue in report["issues"]:
        print(f"\n  Rule:{issue['rule']}")
        print(f"  Column:{issue['column']}")
        print(f"  Count: {issue['issue_count']}")
        print(f"  Cost:₹{issue['estimated_cost_inr']:,}")
        print(f"  Severity:{issue['severity']}")
        print(f"  Action:{issue['recommendation']}")