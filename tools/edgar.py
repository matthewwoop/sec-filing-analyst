import requests

EDGAR_HEADERS = {"User-Agent": "scooby@protonmail.com"}
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_BASE_URL = "https://data.sec.gov/submissions"
ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"

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
        }
        for form, date, acc in zip(
            recent["form"],
            recent["filingDate"],
            recent["accessionNumber"]
        )
        if form in target_forms
    ]

    if not filings:
        raise ValueError(f"No {target_forms} filings found for CIK {cik}")
    
    latest = sorted(filings, key=lambda x: x["filing_date"], reverse=True)[0]
    latest["company_name"] = company_name
    latest["cik"] = cik

    return latest