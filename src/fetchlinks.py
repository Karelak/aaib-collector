import requests
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def fetch_report_links(total_reports: int):
    search_url = "https://www.gov.uk/api/search.json"
    headers = {"Accept": "application/json"}
    report_links = []
    start = 0
    per_page = min(1500, max(1, total_reports))
    while len(report_links) < total_reports:
        count = min(per_page, total_reports - len(report_links))
        params = {
            "filter_format": "aaib_report",
            "order": "-public_timestamp",
            "start": start,
            "count": count,
            "fields": "link",
        }
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        items = response.json().get("results", [])
        if not items:
            break
        report_links.extend(items)
        start += len(items)
        if len(items) < count:
            break
    return report_links[:total_reports]


def fetch_pdf_urls(report_link: str):
    content_url = f"https://www.gov.uk/api/content{report_link}"
    headers = {"Accept": "application/json"}
    while True:
        try:
            response = requests.get(content_url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            attachments = data.get("details", {}).get("attachments", [])
            return [
                a["url"]
                for a in attachments
                if a.get("content_type") == "application/pdf"
                and "abbreviations" not in a["url"].lower()
            ]
        except Exception as e:
            logging.error(
                f"Error fetching {content_url}: {e}. Retrying in 3 seconds..."
            )
            time.sleep(3)


if __name__ == "__main__":
    pdfs = []
    for report in fetch_report_links(50):
        pdf_urls = fetch_pdf_urls(report["link"])
        pdfs.extend(pdf_urls)
    logging.info("PDF URLs collected:")
    for url in pdfs:
        logging.info(url)
