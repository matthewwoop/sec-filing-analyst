import json

from prompts import EXTRACTION_PROMPT
from providers import ModelProvider


EXPECTED_KEYS = {
    "company_name", "ticker", "form_type", "period_of_report",
    "risk_factors", "management_commentary"
}

def extract_filing(filing: dict, provider: ModelProvider) -> dict:
    user_message = f"""
Ticker: {filing['ticker']}
Company: {filing['company_name']}
Form Type: {filing['form_type']}
Filing Date: {filing['filing_date']}

Filing Text:
{filing['filing_text']}
""".strip()
    
    raw = provider.complete(system=EXTRACTION_PROMPT, user_message=user_message)
    return parse_extraction(raw)

def parse_extraction(raw: str) -> dict:
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failure: {e}", "raw": raw}

    if set(parsed.keys()) <= {"error", "raw"}:
        return parsed
    
    # normalize unexpected keys - keep only schema fields
    normalized = {k: parsed.get(k) for k in EXPECTED_KEYS}
    return normalized


if __name__ == "__main__":
    from tools.edgar import get_cik, get_latest_filing, get_filing_text
    from providers import get_provider

    provider = get_provider("local")

    cik = get_cik("NVDA")
    filing = get_latest_filing(cik)
    filing["ticker"] = "NVDA"
    result = get_filing_text(filing)
    result["ticker"] = "NVDA"

    print(result["filing_text"][:2000])

    extraction = extract_filing(result, provider)

    import pprint
    pprint.pprint(extraction)