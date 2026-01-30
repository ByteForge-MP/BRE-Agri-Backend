from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pdfplumber
from bs4 import BeautifulSoup

from services.html_reader import extract_data_html
from services.pdf_reader import extract_data_pdf

app = FastAPI()

# ----------------------------------
# CORS Configuration
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (modify for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# ----------------------------------
# Paths
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS_DIR = os.path.join(
    BASE_DIR,
    "Services",
    "documents"
)

# ----------------------------------
# Request Model
# ----------------------------------
class LoanRequest(BaseModel):
    loanNumber: str


# ----------------------------------
# PDF Reader
# ----------------------------------
def extract_text_from_pdf(file_path: str):
    return extract_data_pdf(file_path)


# ----------------------------------
# HTML Reader
# ----------------------------------
def extract_text_from_html(file_path: str):
    with open(file_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        text = soup.get_text("\n", strip=True)

    return extract_data_html(text)


# ----------------------------------
# API Endpoint
# ----------------------------------
@app.post("/verify-loan")
def verify_loan(data: LoanRequest):

    loan_folder = os.path.join(DOCUMENTS_DIR, data.loanNumber)

    if not os.path.exists(loan_folder):
        # Create the missing loan folder and return 200 so the client
        # knows the folder was created and can proceed to upload files.
        os.makedirs(loan_folder, exist_ok=True)

        return {
            "loanNumber": data.loanNumber,
            "documentsFound": 0,
            "results": [],
            "message": f"Loan folder not found. Created folder {loan_folder} to proceed."
        }

    results = []

    for file in os.listdir(loan_folder):

        file_path = os.path.join(loan_folder, file)

        # ---- PDF ----
        if file.lower().endswith(".pdf"):
            extracted = extract_text_from_pdf(file_path)

            results.append({
                "file": file,
                "type": "pdf",
                "extracted_data": extracted
            })

        # ---- HTML ----
        elif file.lower().endswith(".html"):
            extracted = extract_text_from_html(file_path)

            results.append({
                "file": file,
                "type": "html",
                "extracted_data": extracted
            })

    return {
        "loanNumber": data.loanNumber,
        "documentsFound": len(results),
        "results": results
    }
