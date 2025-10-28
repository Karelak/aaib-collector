# AAIB Report Collector

Automated collection, parsing, and structured summarization of UK Air Accidents Investigation Branch (AAIB) reports.

## Overview

This system:

1. Fetches AAIB report metadata from GOV.UK API
2. Downloads PDF reports
3. Extracts text using PyMuPDF
4. Extracts structured fields using LLM (OpenAI API or dummy mode)
5. Exports to Excel/CSV for analysis

## Quick Start

### Installation

```bash
# Install dependencies
pip install -e .

# Copy the example .env file and configure it
cp .env.example .env
# Edit .env with your settings (OpenAI API key, number of reports, etc.)
```

### Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o

# Data Collection Settings
NUM_REPORTS=10

# Directory Configuration (optional - defaults provided)
DATA_DIR=.data
PDFS_DIR=.data/pdfs
TEXTS_DIR=.data/texts
EXTRACTED_DIR=.data/extracted
OUTPUT_EXCEL=.data/aaib_reports.xlsx
OUTPUT_CSV=.data/aaib_reports.csv
```

### Basic Usage (Dummy Mode - No API Key Required)

```bash
# Process reports using settings from .env (with dummy extractor)
python main.py

# Override number of reports from command line
python main.py --num-reports 5
```

### Advanced Usage (With OpenAI API)

```bash
# Set your OpenAI API key in .env file first
# Then run with LLM enabled:
python main.py --use-llm

# Process specific number of reports with LLM
python main.py --num-reports 20 --use-llm

# Use a different model
python main.py --use-llm --llm-model gpt-4o-mini
```

## Command-Line Options

```
python main.py [options]

Options:
  -n, --num-reports N      Number of reports to process (default: from .env NUM_REPORTS)
  --use-llm               Use OpenAI API for extraction (requires OPENAI_API_KEY in .env)
  --llm-model MODEL       OpenAI model to use (default: from .env OPENAI_MODEL)
  --skip-download         Skip PDF download (use existing PDFs)
  --skip-extraction       Skip text extraction (use existing texts)
```

All settings can be configured in `.env` file and optionally overridden via command-line arguments.

## 📊 Output Format

The pipeline generates structured data with these fields:

| Field           | Description                           |
| --------------- | ------------------------------------- |
| `title`         | Report title or incident description  |
| `date`          | Date of incident (YYYY-MM-DD)         |
| `aircraft_type` | Aircraft make and model               |
| `registration`  | Aircraft registration number          |
| `location`      | Location of incident                  |
| `summary`       | Brief summary of what happened        |
| `cause`         | Primary cause or contributing factors |
| `source_pdf`    | Source PDF filename                   |
| `text_length`   | Length of extracted text              |

## 🧩 Module Usage

Each module can be run independently:

```python
# Configuration is automatically loaded from .env
from src.config import config

# Fetch report links
from src.fetch_links import fetch_report_links, fetch_pdf_urls
reports = fetch_report_links(config.NUM_REPORTS)
pdf_urls = fetch_pdf_urls(reports[0]["link"])

# Download PDFs (uses config.PDFS_DIR by default)
from src.download_pdfs import download_pdfs
files = download_pdfs(pdf_urls)

# Extract text (uses config.PDFS_DIR and config.TEXTS_DIR)
from src.extract_text import extract_texts_from_directory
texts = extract_texts_from_directory()

# Extract fields (uses config.TEXTS_DIR, config.EXTRACTED_DIR, config.OPENAI_MODEL)
from src.extract_fields import process_text_files
fields = process_text_files(use_llm=False)  # or use_llm=True

# Aggregate to Excel (uses config.EXTRACTED_DIR, config.OUTPUT_EXCEL, config.OUTPUT_CSV)
from src.aggregate_data import aggregate_data
df = aggregate_data()
```

## 🔑 Environment Variables (.env file)

All configuration is managed through a `.env` file:

| Variable         | Description                       | Default                   |
| ---------------- | --------------------------------- | ------------------------- |
| `OPENAI_API_KEY` | OpenAI API key for LLM extraction | (required for --use-llm)  |
| `OPENAI_MODEL`   | OpenAI model to use               | `gpt-4o`                  |
| `NUM_REPORTS`    | Number of reports to process      | `10`                      |
| `DATA_DIR`       | Base data directory               | `.data`                   |
| `PDFS_DIR`       | PDF downloads directory           | `.data/pdfs`              |
| `TEXTS_DIR`      | Extracted text directory          | `.data/texts`             |
| `EXTRACTED_DIR`  | Extracted fields directory        | `.data/extracted`         |
| `OUTPUT_EXCEL`   | Excel output file path            | `.data/aaib_reports.xlsx` |
| `OUTPUT_CSV`     | CSV output file path              | `.data/aaib_reports.csv`  |

## 📦 Dependencies

- `python-dotenv` - Environment variable management
- `requests` - HTTP requests for API calls
- `pymupdf` (fitz) - PDF text extraction
- `pandas` - Data manipulation
- `openpyxl` - Excel file creation
- `openai` - OpenAI API client

## 🛠️ Development

```bash
# Run individual modules (make sure .env is configured)
cd src
python fetch_links.py       # Test link fetching
python download_pdfs.py     # Test PDF download
python extract_text.py      # Test text extraction
python extract_fields.py    # Test field extraction (dummy mode)
python aggregate_data.py    # Test data aggregation
```

## 📝 License

MIT
