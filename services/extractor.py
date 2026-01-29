import re

def extract_details(text: str):
    result = {}

    # Name
    name_match = re.search(r"Name\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    # CIBIL Score
    cibil_match = re.search(r"CIBIL\s*Score\s*[:\-]?\s*(\d{3})", text, re.IGNORECASE)
    if cibil_match:
        result["cibil_score"] = cibil_match.group(1)

    # PAN
    pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", text)
    if pan_match:
        result["pan"] = pan_match.group(0)

    return result
