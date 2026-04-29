import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    'CustomerID', 'Age', 'Gender', 'Tenure', 'Usage Frequency',
    'Support Calls', 'Payment Delay', 'Subscription Type',
    'Contract Length', 'Total Spend', 'Last Interaction', 'Churn'
    ]

EXPECTED_DTYPES = {
    'CustomerID': 'int64',
    'Age': 'int64',
    'Tenure': 'int64',
    'Total Spend': 'int64',
    'Churn': 'int64'
}

MIN_ROW_THRESHOLD = 100

def load_data(file_path:str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully from {file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def validate_schema(df: pd.DataFrame) -> dict:
    issues = []

    missing_cols = [cols for cols in EXPECTED_COLUMNS if cols not in df.columns]
    extra_cols = [cols for cols in df.columns if cols not in EXPECTED_COLUMNS]

    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
        logger.warning(f"Missing columns: {missing_cols}")
    if extra_cols:
        issues.append(f"Extra columns: {extra_cols}")
        logger.warning(f"Extra columns: {extra_cols}")
    
    if len(df) < MIN_ROW_THRESHOLD:
        issues.append(f"Row count below threshold: {len(df)} rows")
        logger.warning(f"Row count below threshold: {len(df)} rows")

    for cols, expected_dtype in EXPECTED_DTYPES.items():
        if cols in df.columns:
            actual_dtype = df[cols].dtype
            if actual_dtype != expected_dtype:
                issues.append(f"Column '{cols}' has dtype {actual_dtype}, expected {expected_dtype}")
                logger.warning(f"Column '{cols}' has dtype {actual_dtype}, expected {expected_dtype}")
    return {
        "timestamp": datetime.now().isoformat(),
        "rows": len(df),
        "columns": len(df.columns),
        "issues": issues,
        "passed": len(issues) == 0
    }

def ingest(filepath: str) -> tuple[pd.DataFrame, dict]:
    logger.info(f"Starting data ingestion for file: {filepath}")
    df = load_data(filepath)
    validation = validate_schema(df)
    
    if validation['passed']:
        logger.info("Data ingestion successful with no issues.")
    else:
        logger.warning(f"Schema validation failed with {len(validation['issues'])} issues")
    return df, validation

if __name__ == "__main__":
    df, report = ingest("data/raw/churn.csv")
    print("\n--- Ingestion Report ---")
    print(f"Rows loaded:{report['rows']}")
    print(f"Columns:{report['columns']}")
    print(f"Status:{'PASSED' if report['passed'] else 'FAILED'}")
    print(f"Issues:{report['issues'] if report['issues'] else 'None'}")
    