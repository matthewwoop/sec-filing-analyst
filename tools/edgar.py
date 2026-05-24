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