import json
import logging
from pathlib import Path
import pandas as pd
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_extracted_fields(extracted_dir: str | None = None) -> list[dict]:
    """
    Load all extracted field JSON files from directory.

    Args:
        extracted_dir: Directory containing extracted field JSON files (default: from config.EXTRACTED_DIR)

    Returns:
        List of dictionaries with extracted fields
    """
    if extracted_dir is None:
        extracted_dir = config.EXTRACTED_DIR

    extracted_path = Path(extracted_dir)

    if not extracted_path.exists():
        logging.error(f"Extracted data directory does not exist: {extracted_path}")
        return []

    json_files = list(extracted_path.glob("*_extracted.json"))
    logging.info(f"Found {len(json_files)} extracted field files in {extracted_path}")

    records = []

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                records.append(data)
        except Exception as e:
            logging.error(f"Error loading {json_file}: {e}")

    logging.info(f"Loaded {len(records)} records")
    return records


def aggregate_to_dataframe(records: list[dict]) -> pd.DataFrame:
    """
    Convert list of extracted field dictionaries to pandas DataFrame.

    Args:
        records: List of dictionaries with extracted fields

    Returns:
        pandas DataFrame with normalized columns
    """
    if not records:
        logging.warning("No records to aggregate")
        return pd.DataFrame()

    # Define expected columns in desired order
    columns = [
        "title",
        "date",
        "aircraft_type",
        "registration",
        "location",
        "summary",
        "cause",
        "source_pdf",
        "text_length",
    ]

    # Create DataFrame
    df = pd.DataFrame(records)

    # Ensure all expected columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = None

    # Reorder columns
    df = df[columns]

    logging.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df


def export_to_excel(df: pd.DataFrame, output_file: str | None = None) -> None:
    """
    Export DataFrame to Excel file.

    Args:
        df: pandas DataFrame to export
        output_file: Path to output Excel file (default: from config.OUTPUT_EXCEL)
    """
    if output_file is None:
        output_file = config.OUTPUT_EXCEL

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_excel(output_path, index=False, engine="openpyxl")
        logging.info(f"Exported {len(df)} records to Excel: {output_path}")
    except Exception as e:
        logging.error(f"Error exporting to Excel: {e}")


def export_to_csv(df: pd.DataFrame, output_file: str | None = None) -> None:
    """
    Export DataFrame to CSV file.

    Args:
        df: pandas DataFrame to export
        output_file: Path to output CSV file (default: from config.OUTPUT_CSV)
    """
    if output_file is None:
        output_file = config.OUTPUT_CSV

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df.to_csv(output_path, index=False, encoding="utf-8")
        logging.info(f"Exported {len(df)} records to CSV: {output_path}")
    except Exception as e:
        logging.error(f"Error exporting to CSV: {e}")


def aggregate_data(
    extracted_dir: str | None = None,
    output_excel: str | None = None,
    output_csv: str | None = None,
) -> pd.DataFrame:
    """
    Main aggregation function: load extracted fields, create DataFrame, and export.

    Args:
        extracted_dir: Directory containing extracted field JSON files (default: from config.EXTRACTED_DIR)
        output_excel: Path to output Excel file (default: from config.OUTPUT_EXCEL)
        output_csv: Path to output CSV file (default: from config.OUTPUT_CSV)

    Returns:
        pandas DataFrame with aggregated data
    """
    logging.info("Starting data aggregation...")

    # Load all extracted records
    records = load_extracted_fields(extracted_dir)

    if not records:
        logging.error("No records found to aggregate")
        return pd.DataFrame()

    # Create DataFrame
    df = aggregate_to_dataframe(records)

    # Export to both formats
    export_to_excel(df, output_excel)
    export_to_csv(df, output_csv)

    logging.info("Data aggregation complete!")
    return df


if __name__ == "__main__":
    # Aggregate all extracted data
    df = aggregate_data()

    if not df.empty:
        logging.info(f"\nDataFrame summary:")
        logging.info(f"  Shape: {df.shape}")
        logging.info(f"  Columns: {list(df.columns)}")
        logging.info(f"\nFirst few records:")
        print(df.head().to_string())
