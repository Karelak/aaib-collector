"""
Configuration management for AAIB Collector.
Loads settings from .env file using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)


class Config:
    """Central configuration class for AAIB Collector."""

    # OpenAI API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Data Collection Settings
    NUM_REPORTS: int = int(os.getenv("NUM_REPORTS", "10"))

    # Directory Configuration
    DATA_DIR: str = os.getenv("DATA_DIR", ".data")
    PDFS_DIR: str = os.getenv("PDFS_DIR", ".data/pdfs")
    TEXTS_DIR: str = os.getenv("TEXTS_DIR", ".data/texts")
    EXTRACTED_DIR: str = os.getenv("EXTRACTED_DIR", ".data/extracted")
    OUTPUT_EXCEL: str = os.getenv("OUTPUT_EXCEL", ".data/aaib_reports.xlsx")
    OUTPUT_CSV: str = os.getenv("OUTPUT_CSV", ".data/aaib_reports.csv")

    @classmethod
    def has_openai_key(cls) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != "sk-your-api-key-here")

    @classmethod
    def get_summary(cls) -> str:
        """Get a formatted summary of current configuration."""
        return f"""
Configuration Summary:
  OpenAI API Key: {"✓ Set" if cls.has_openai_key() else "✗ Not set"}
  OpenAI Model: {cls.OPENAI_MODEL}
  Number of Reports: {cls.NUM_REPORTS}
  Data Directory: {cls.DATA_DIR}
  PDFs Directory: {cls.PDFS_DIR}
  Texts Directory: {cls.TEXTS_DIR}
  Extracted Directory: {cls.EXTRACTED_DIR}
  Output Excel: {cls.OUTPUT_EXCEL}
  Output CSV: {cls.OUTPUT_CSV}
        """.strip()


# Singleton instance
config = Config()
