"""
AAIB Report Collector - Main Pipeline

End-to-end pipeline for collecting, processing, and extracting structured data
from UK Air Accidents Investigation Branch (AAIB) reports.

Pipeline stages:
1. Fetch report links from GOV.UK API
2. Download PDFs to .data/pdfs
3. Extract text from PDFs to .data/texts
4. Extract structured fields using LLM to .data/extracted
5. Aggregate to Excel/CSV in .data/
"""

import logging
import argparse
from pathlib import Path

# Import config first
from src.config import config

# Import all pipeline modules
from src.fetch_links import fetch_report_links, fetch_pdf_urls
from src.download_pdfs import download_pdfs
from src.extract_text import extract_texts_from_directory
from src.extract_fields import process_text_files
from src.aggregate_data import aggregate_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run_pipeline(
    num_reports: int | None = None,
    use_llm: bool = False,
    llm_model: str | None = None,
    skip_download: bool = False,
    skip_extraction: bool = False,
):
    """
    Run the complete AAIB data collection pipeline.

    Args:
        num_reports: Number of reports to fetch and process (default: from config.NUM_REPORTS)
        use_llm: Whether to use real LLM API (requires OPENAI_API_KEY)
        llm_model: Which OpenAI model to use if use_llm=True (default: from config.OPENAI_MODEL)
        skip_download: Skip PDF download (use existing PDFs)
        skip_extraction: Skip text extraction (use existing text files)
    """
    # Use config defaults if not specified
    if num_reports is None:
        num_reports = config.NUM_REPORTS
    if llm_model is None:
        llm_model = config.OPENAI_MODEL

    logging.info("=" * 70)
    logging.info("AAIB REPORT COLLECTOR - PIPELINE START")
    logging.info("=" * 70)
    logging.info("Configuration:")
    logging.info(f"  Reports to process: {num_reports}")
    logging.info(f"  Use LLM: {use_llm} (model: {llm_model if use_llm else 'N/A'})")
    logging.info(
        f"  OpenAI API Key: {'✓ Set' if config.has_openai_key() else '✗ Not set'}"
    )
    logging.info(f"  Skip download: {skip_download}")
    logging.info(f"  Skip extraction: {skip_extraction}")
    logging.info("=" * 70)

    # Stage 1: Fetch report links
    logging.info("\n[STAGE 1/5] Fetching report links from GOV.UK API...")
    report_links = fetch_report_links(num_reports)
    logging.info(f"Found {len(report_links)} report links")

    if not report_links:
        logging.error("No report links found. Exiting.")
        return

    # Stage 2: Fetch PDF URLs and download PDFs
    if not skip_download:
        logging.info("\n[STAGE 2/5] Fetching PDF URLs and downloading...")
        pdf_urls = []
        for i, report in enumerate(report_links, 1):
            logging.info(
                f"Fetching PDFs for report {i}/{len(report_links)}: {report['link']}"
            )
            urls = fetch_pdf_urls(report["link"])
            pdf_urls.extend(urls)

        logging.info(f"Found {len(pdf_urls)} PDF URLs")

        if pdf_urls:
            downloaded_files = download_pdfs(pdf_urls)
            logging.info(f"Downloaded {len(downloaded_files)} PDFs")
        else:
            logging.warning("No PDF URLs found")
    else:
        logging.info("\n[STAGE 2/5] Skipping PDF download (using existing files)")

    # Stage 3: Extract text from PDFs
    if not skip_extraction:
        logging.info("\n[STAGE 3/5] Extracting text from PDFs...")
        text_results = extract_texts_from_directory()
        logging.info(f"Extracted text from {len(text_results)} PDFs")
    else:
        logging.info("\n[STAGE 3/5] Skipping text extraction (using existing files)")

    # Stage 4: Extract structured fields using LLM
    logging.info("\n[STAGE 4/5] Extracting structured fields...")
    if use_llm:
        logging.info("Using OpenAI API for field extraction")
    else:
        logging.info("Using DUMMY extractor (no API calls)")

    extracted_records = process_text_files(use_llm=use_llm, model=llm_model)
    logging.info(f"Extracted fields from {len(extracted_records)} reports")

    # Stage 5: Aggregate to Excel/CSV
    logging.info("\n[STAGE 5/5] Aggregating data to Excel/CSV...")
    df = aggregate_data()

    # Final summary
    logging.info("\n" + "=" * 70)
    logging.info("PIPELINE COMPLETE!")
    logging.info("=" * 70)
    logging.info(f"Total reports processed: {len(df) if not df.empty else 0}")
    logging.info("Output files:")
    logging.info(f"  - {config.OUTPUT_EXCEL}")
    logging.info(f"  - {config.OUTPUT_CSV}")
    logging.info("Intermediate data:")
    logging.info(f"  - {config.PDFS_DIR}/       (downloaded PDFs)")
    logging.info(f"  - {config.TEXTS_DIR}/      (extracted text JSON files)")
    logging.info(f"  - {config.EXTRACTED_DIR}/  (structured field JSON files)")
    logging.info("=" * 70)


def main():
    """Command-line interface for the pipeline."""
    parser = argparse.ArgumentParser(
        description="AAIB Report Collector - Automated data extraction pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Configuration can be set via .env file or command-line arguments.
Current config from .env:
{config.get_summary()}

Examples:
  # Process reports using config defaults from .env
  python main.py

  # Process 5 reports with dummy extractor (no API needed)
  python main.py --num-reports 5

  # Process 20 reports with OpenAI (requires OPENAI_API_KEY in .env)
  python main.py --num-reports 20 --use-llm

  # Use existing PDFs and texts, just re-run field extraction
  python main.py --skip-download --skip-extraction --use-llm
        """,
    )

    parser.add_argument(
        "-n",
        "--num-reports",
        type=int,
        default=None,
        help=f"Number of reports to fetch and process (default: {config.NUM_REPORTS} from .env)",
    )

    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use OpenAI API for field extraction (requires OPENAI_API_KEY env var)",
    )

    parser.add_argument(
        "--llm-model",
        type=str,
        default=None,
        help=f"OpenAI model to use (default: {config.OPENAI_MODEL} from .env)",
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help=f"Skip PDF download stage (use existing PDFs in {config.PDFS_DIR})",
    )

    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help=f"Skip text extraction stage (use existing text files in {config.TEXTS_DIR})",
    )

    args = parser.parse_args()

    # Run the pipeline
    run_pipeline(
        num_reports=args.num_reports,
        use_llm=args.use_llm,
        llm_model=args.llm_model,
        skip_download=args.skip_download,
        skip_extraction=args.skip_extraction,
    )


if __name__ == "__main__":
    main()
