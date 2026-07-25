import pandas as pd
from src.ingest import ingest


def calculate_completeness(df: pd.DataFrame) -> float:
    
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    return round((1 - missing_cells / total_cells) * 100, 2)


def calculate_uniqueness(df: pd.DataFrame) -> float:
    
    duplicate_rows = df.duplicated().sum()
    return round((1 - duplicate_rows / len(df)) * 100, 2)


def calculate_validity(df: pd.DataFrame) -> float:
    
    issues = 0
    total_checks = 0

    checks = {
        'Age': (18, 65),
        'Tenure': (1, 60),
        'Usage Frequency': (1, 30),
        'Support Calls': (0, 10),
        'Payment Delay': (0, 30),
        'Total Spend': (100, 1000),
        'Last Interaction': (1, 30)
    }

    for col, (min_val, max_val) in checks.items():
        if col in df.columns:
            total_checks += len(df)
            issues += df[(df[col] < min_val) | (df[col] > max_val)].shape[0]

    if total_checks == 0:
        return 100.0

    return round((1 - issues / total_checks) * 100, 2)


def calculate_consistency(df: pd.DataFrame) -> float:

    issues = 0
    total = len(df)

    if all(col in df.columns for col in ['Churn', 'Support Calls', 'Payment Delay']):
        suspicious = df[
            (df['Churn'] == 0) &
            (df['Support Calls'] > 8) &
            (df['Payment Delay'] > 25)
        ].shape[0]
        issues += suspicious

    return round((1 - issues / total) * 100, 2)


def calculate_quality_score(df: pd.DataFrame) -> dict:
    
    completeness = calculate_completeness(df)
    uniqueness = calculate_uniqueness(df)
    validity = calculate_validity(df)
    consistency = calculate_consistency(df)

    overall = round(
        (completeness * 0.45) +
        (uniqueness   * 0.25) +
        (validity     * 0.20) +
        (consistency  * 0.10),
        2
    )

    if overall >= 99:
        status = "HEALTHY"
    elif overall >= 95:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "overall_score": overall,
        "status": status,
        "dimensions": {
            "completeness": completeness,
            "uniqueness": uniqueness,
            "validity": validity,
            "consistency": consistency
        }
    }


if __name__ == "__main__":
    df, _ = ingest("data/raw/churn.csv")
    report = calculate_quality_score(df)

    print("\n--- DataSentry Quality Report ---")
    print(f"Overall Score:  {report['overall_score']} / 100")
    print(f"Status:         {report['status']}")
    print("\nDimension Breakdown:")
    for dimension, score in report['dimensions'].items():
        print(f"  {dimension.capitalize():<15} {score}")