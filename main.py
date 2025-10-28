import requests
from pprint import pprint


def getreports(resultstoget: int):
    """Fetch AAIB reports from GOV.UK search API."""
    search_url = "https://www.gov.uk/api/search.json"
    headers = {"Accept": "application/json"}
    results = []
    start = 0
    per_page = min(1500, max(1, resultstoget))
    while len(results) < resultstoget:
        count = min(per_page, resultstoget - len(results))
        params = {
            "filter_format": "aaib_report",
            "order": "-public_timestamp",
            "start": start,
            "count": count,
            "fields": "link",
        }

        r = requests.get(search_url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        items = r.json().get("results", [])
        if not items:
            break

        results.extend(items)
        start += len(items)

        if len(items) < count:
            break

    return results[:resultstoget]


def getpdflinks(link: str):
    """Fetch PDF links for a specific AAIB report."""
    content_url = f"https://www.gov.uk/api/content{link}"
    headers = {"Accept": "application/json"}

    r = requests.get(content_url, headers=headers, timeout=30)
    r.raise_for_status()

    data = r.json()
    attachments = data.get("details", {}).get("attachments", [])

    pdf_links = [
        attachment["url"]
        for attachment in attachments
        if attachment.get("content_type") == "application/pdf"
        and "abbreviations" not in attachment["url"].lower()
    ]

    return pdf_links


if __name__ == "__main__":
    numreports = 5
    reports = getreports(numreports)
    for report in reports:
        details = getpdflinks(report["link"])
        pprint(details)
