from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pdfplumber
import re

app = FastAPI()

# ✅ Always resolve correct path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS_DIR = os.path.join(
    BASE_DIR,
    "Services",
    "documents"
)


# ---------- REQUEST MODEL ----------
class LoanRequest(BaseModel):
    loanNumber: str


# ---------- UTILITY FUNCTIONS ----------

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_details(text: str):
    result = {}

    # Name
    name_match = re.search(r"Name\s*[:\-]?\s*(.*)", text, re.IGNORECASE)
    if name_match:
        result["name"] = name_match.group(1).strip()

    # PAN
    pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    if pan_match:
        result["pan"] = pan_match.group(0)

    # CIBIL Score
    cibil_match = re.search(r"CIBIL\s*Score\s*[:\-]?\s*(\d{3})", text, re.IGNORECASE)
    if cibil_match:
        result["cibil_score"] = cibil_match.group(1)

    return result


# ---------- API ----------
@app.post("/verify-loan")
def verify_loan(data: LoanRequest):

    loan_folder = os.path.join(DOCUMENTS_DIR, data.loanNumber)

    # 🔴 Important safety check
    if not os.path.exists(loan_folder):
        raise HTTPException(
            status_code=404,
            detail=f"Loan folder not found: {loan_folder}"
        )

    results = []

    for file in os.listdir(loan_folder):
        if file.lower().endswith(".pdf"):
            file_path = os.path.join(loan_folder, file)

            text = extract_text_from_pdf(file_path)
            extracted = extract_details(text)

            results.append({
                "file": file,
                "extracted_data": extracted
            })

    return {
        "loanNumber": data.loanNumber,
        "documentsFound": len(results),
        "results": results
    }
