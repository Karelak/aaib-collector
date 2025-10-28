import requests
import logging
from pathlib import Path
import time
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def download_pdf(
    url: str, output_dir: Path, retry_delay: int = 3, max_retries: int = 3
) -> Path | None:
    """
    Download a single PDF from the given URL to the output directory.

    Args:
        url: The PDF URL to download
        output_dir: Directory to save the PDF
        retry_delay: Seconds to wait between retries
        max_retries: Maximum number of retry attempts

    Returns:
        Path to the downloaded PDF, or None if download failed
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract filename from URL
    filename = url.split("/")[-1]
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    output_path = output_dir / filename

    # Skip if already downloaded
    if output_path.exists():
        logging.info(f"Already exists: {filename}")
        return output_path

    # Retry logic
    for attempt in range(max_retries):
        try:
            logging.info(f"Downloading: {url}")
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()

            # Write in chunks for large files
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logging.info(f"Saved: {output_path}")
            return output_path

        except Exception as e:
            logging.error(
                f"Error downloading {url} (attempt {attempt + 1}/{max_retries}): {e}"
            )
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to download {url} after {max_retries} attempts")
                return None


def download_pdfs(pdf_urls: list[str], output_dir: str | None = None) -> list[Path]:
    """
    Download multiple PDFs from a list of URLs.

    Args:
        pdf_urls: List of PDF URLs to download
        output_dir: Directory to save PDFs (default: from config.PDFS_DIR)

    Returns:
        List of Paths to successfully downloaded PDFs
    """
    if output_dir is None:
        output_dir = config.PDFS_DIR

    output_path = Path(output_dir)
    downloaded_files = []

    logging.info(f"Starting download of {len(pdf_urls)} PDFs to {output_path}")

    for i, url in enumerate(pdf_urls, 1):
        logging.info(f"[{i}/{len(pdf_urls)}] Processing: {url}")
        result = download_pdf(url, output_path)
        if result:
            downloaded_files.append(result)

    logging.info(
        f"Download complete: {len(downloaded_files)}/{len(pdf_urls)} successful"
    )
    return downloaded_files


if __name__ == "__main__":
    # Example usage - download a sample PDF
    test_urls = [
        "https://assets.publishing.service.gov.uk/media/example.pdf",
    ]

    downloaded = download_pdfs(test_urls)
    logging.info(f"Downloaded {len(downloaded)} files:")
    for path in downloaded:
        logging.info(f"  {path}")
