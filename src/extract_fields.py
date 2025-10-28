import json
import logging
from pathlib import Path
from openai import OpenAI
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Extraction prompt for the LLM
EXTRACTION_PROMPT = """You are an expert aviation safety analyst. Extract key information from this AAIB aircraft accident report.

Return ONLY valid JSON with these exact fields (use null for missing data):
{
  "title": "Report title or aircraft incident description",
  "date": "Date of incident (YYYY-MM-DD format if possible)",
  "aircraft_type": "Aircraft make and model",
  "registration": "Aircraft registration number",
  "location": "Location of incident",
  "summary": "Brief 1-2 sentence summary of what happened",
  "cause": "Primary cause or contributing factors"
}

Report text:
"""


def extract_fields_with_llm(
    text: str, model: str | None = None, api_key: str | None = None
) -> dict:
    """
    Extract structured fields from report text using OpenAI API.

    Args:
        text: The report text to analyze
        model: OpenAI model to use (default: from config.OPENAI_MODEL)
        api_key: OpenAI API key (default: from config.OPENAI_API_KEY)

    Returns:
        Dictionary with extracted fields
    """
    if model is None:
        model = config.OPENAI_MODEL
    if api_key is None:
        api_key = config.OPENAI_API_KEY

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Truncate text if too long (keep first ~20k chars for context)
        truncated_text = text[:20000] if len(text) > 20000 else text

        logging.info(f"Sending {len(truncated_text)} chars to {model}...")

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured data from aviation accident reports.",
                },
                {"role": "user", "content": EXTRACTION_PROMPT + truncated_text},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        # Parse response
        result = json.loads(response.choices[0].message.content)
        logging.info(f"Successfully extracted fields: {list(result.keys())}")
        return result

    except Exception as e:
        logging.error(f"Error during LLM extraction: {e}")
        return {
            "title": None,
            "date": None,
            "aircraft_type": None,
            "registration": None,
            "location": None,
            "summary": None,
            "cause": None,
            "error": str(e),
        }


def extract_fields_dummy(text: str) -> dict:
    """
    Dummy extractor for proof-of-concept (no API needed).
    Returns mock data based on text length.

    Args:
        text: The report text (not actually used in dummy mode)

    Returns:
        Dictionary with mock extracted fields
    """
    logging.info("Using DUMMY extractor (no API calls)")

    # Simple heuristic: extract first line as title
    lines = text.strip().split("\n")
    first_line = lines[0] if lines else "Unknown Report"

    return {
        "title": first_line[:100],
        "date": "2024-01-15",
        "aircraft_type": "Example Aircraft Type",
        "registration": "G-ABCD",
        "location": "Example Location, UK",
        "summary": "This is a dummy extraction. Real data would come from LLM analysis.",
        "cause": "Dummy cause - replace with actual LLM when API key is configured",
    }


def process_text_files(
    text_dir: str | None = None,
    output_dir: str | None = None,
    use_llm: bool = False,
    model: str | None = None,
) -> list[dict]:
    """
    Process all text JSON files and extract structured fields.

    Args:
        text_dir: Directory containing extracted text JSON files (default: from config.TEXTS_DIR)
        output_dir: Directory to save extracted field JSON files (default: from config.EXTRACTED_DIR)
        use_llm: Whether to use real LLM (True) or dummy extractor (False)
        model: Which OpenAI model to use if use_llm=True (default: from config.OPENAI_MODEL)

    Returns:
        List of extracted records
    """
    if text_dir is None:
        text_dir = config.TEXTS_DIR
    if output_dir is None:
        output_dir = config.EXTRACTED_DIR
    if model is None:
        model = config.OPENAI_MODEL

    text_path = Path(text_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not text_path.exists():
        logging.error(f"Text directory does not exist: {text_path}")
        return []

    text_files = list(text_path.glob("*_text.json"))
    logging.info(f"Found {len(text_files)} text files in {text_path}")

    if use_llm and not config.has_openai_key():
        logging.warning("OPENAI_API_KEY not set! Falling back to dummy mode.")
        use_llm = False

    results = []

    for i, text_file in enumerate(text_files, 1):
        logging.info(f"[{i}/{len(text_files)}] Processing: {text_file.name}")

        # Load text data
        with open(text_file, "r", encoding="utf-8") as f:
            text_data = json.load(f)

        text = text_data.get("text", "")

        # Extract fields
        if use_llm:
            extracted = extract_fields_with_llm(text, model=model)
        else:
            extracted = extract_fields_dummy(text)

        # Add metadata
        extracted["source_pdf"] = text_data.get("pdf_name")
        extracted["text_length"] = len(text)

        # Save extracted fields
        output_filename = text_file.stem.replace("_text", "_extracted.json")
        output_file = output_path / output_filename

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(extracted, f, indent=2, ensure_ascii=False)

        logging.info(f"Saved extracted fields to: {output_file}")
        results.append(extracted)

    logging.info(f"Field extraction complete: {len(results)} reports processed")
    return results


if __name__ == "__main__":
    # Example: Process all text files with dummy extractor
    # Set use_llm=True to use real OpenAI API (requires OPENAI_API_KEY env var)

    results = process_text_files(use_llm=False)

    logging.info(f"\nExtracted fields from {len(results)} reports:")
    for result in results:
        logging.info(f"  Title: {result.get('title', 'N/A')}")
        logging.info(f"  Date: {result.get('date', 'N/A')}")
        logging.info(f"  Aircraft: {result.get('aircraft_type', 'N/A')}")
