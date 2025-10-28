import fitz  # PyMuPDF
import logging
from pathlib import Path
import json
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text as a single string
    """
    try:
        doc = fitz.open(pdf_path)
        text_content = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_content.append(page.get_text())

        doc.close()

        full_text = "\n".join(text_content)
        logging.info(f"Extracted {len(full_text)} characters from {pdf_path.name}")
        return full_text

    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""


def extract_texts_from_directory(
    pdf_dir: str | None = None, output_dir: str | None = None
) -> list[dict]:
    """
    Extract text from all PDFs in a directory and save as JSON sidecar files.

    Args:
        pdf_dir: Directory containing PDF files (default: from config.PDFS_DIR)
        output_dir: Directory to save extracted text JSON files (default: from config.TEXTS_DIR)

    Returns:
        List of dicts with 'pdf_path', 'text_path', and 'text' keys
    """
    if pdf_dir is None:
        pdf_dir = config.PDFS_DIR
    if output_dir is None:
        output_dir = config.TEXTS_DIR

    pdf_path = Path(pdf_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        logging.error(f"PDF directory does not exist: {pdf_path}")
        return []

    pdf_files = list(pdf_path.glob("*.pdf"))
    logging.info(f"Found {len(pdf_files)} PDF files in {pdf_path}")

    results = []

    for i, pdf_file in enumerate(pdf_files, 1):
        logging.info(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")

        # Extract text
        text = extract_text_from_pdf(pdf_file)

        if not text:
            logging.warning(f"No text extracted from {pdf_file.name}")
            continue

        # Save as JSON sidecar file
        text_filename = pdf_file.stem + "_text.json"
        text_path = output_path / text_filename

        data = {
            "pdf_name": pdf_file.name,
            "pdf_path": str(pdf_file.absolute()),
            "text_length": len(text),
            "text": text,
        }

        with open(text_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"Saved text to: {text_path}")

        results.append({"pdf_path": pdf_file, "text_path": text_path, "text": text})

    logging.info(f"Text extraction complete: {len(results)} files processed")
    return results


if __name__ == "__main__":
    # Extract text from all PDFs in .data/pdfs
    results = extract_texts_from_directory()

    logging.info(f"Extracted text from {len(results)} PDFs")
    for result in results:
        logging.info(
            f"  {result['pdf_path'].name} -> {result['text_path'].name} ({len(result['text'])} chars)"
        )
