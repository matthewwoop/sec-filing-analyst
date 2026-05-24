import re
import requests

EDGAR_HEADERS = {"User-Agent": "scooby@protonmail.com"}
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_BASE_URL = "https://data.sec.gov/submissions"
ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"

MAX_FILING_CHARS = 80_000

SECTION_PATTERNS = [
    r"item\s+1a[\.\s]+risk factors",
    r"item\s+7[\.\s]+management",
    r"item\s+8[\.\s]+financial statements",
]

def get_cik(ticker: str) -> str:
    response = requests.get(SEC_TICKERS_URL, headers=EDGAR_HEADERS)
    response.raise_for_status()

    data = response.json()
    ticker_upper = ticker.upper()

    for entry in data.values():
        if entry["ticker"] == ticker_upper:
            return str(entry["cik_str"]).zfill(10)
        
    raise ValueError(f"Ticker '{ticker_upper}' not found in SEC company list")

def get_latest_filing(cik: str, form_type: str = "latest") -> dict:
    url = f"{SUBMISSIONS_BASE_URL}/CIK{cik}.json"
    response = requests.get(url, headers=EDGAR_HEADERS)
    response.raise_for_status()

    data = response.json()
    company_name = data["name"]
    recent = data["filings"]["recent"]

    target_forms = ["10-K", "10-Q"] if form_type == "latest" else [form_type]

    filings = [
        {
            "form_type": form,
            "filing_date": date,
            "accession_number": acc,
            "primary_document": primary_doc
        }
        for form, date, acc, primary_doc in zip(
            recent["form"],
            recent["filingDate"],
            recent["accessionNumber"],
            recent["primaryDocument"]
        )
        if form in target_forms
    ]

    if not filings:
        raise ValueError(f"No {target_forms} filings found for CIK {cik}")
    
    latest = sorted(filings, key=lambda x: x["filing_date"], reverse=True)[0]
    latest["company_name"] = company_name
    latest["cik"] = cik

    return latest

def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&#\d+;", " ", text)       # numeric entities
    text = re.sub(r"&[a-zA-Z]+;", " ", text)  # named entities
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def extract_sections(text: str) -> str:
    for pattern in SECTION_PATTERNS:
        matches = [m for m in re.finditer(pattern, text, re.IGNORECASE)]
        if matches:
            start = matches[-1].start()
            return text[start : start + MAX_FILING_CHARS]
    return text[:MAX_FILING_CHARS]

def get_filing_text(filing: dict) -> dict:
    acc_no_dashes = filing["accession_number"].replace("-", "")
    cik_int = int(filing["cik"])
    primary_doc = filing["primary_document"]

    doc_url = f"{ARCHIVES_BASE_URL}/{cik_int}/{acc_no_dashes}/{primary_doc}"

    response = requests.get(doc_url, headers=EDGAR_HEADERS)
    response.raise_for_status()

    raw_text = strip_html(response.text)
    filing_text = extract_sections(raw_text)

    return {
        "company_name": filing["company_name"],
        "form_type": filing["form_type"],
        "filing_date": filing["filing_date"],
        "accession_number": filing["accession_number"],
        "filing_text": filing_text,
    }