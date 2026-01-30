import pdfplumber


def extract_data_pdf(file_path):
    keys = [
        "Date & Time of CIR generation",
        "CUST ID",
        "CIBIL Score/CIR",
        "Term Loan - Krishi Tatkal Rin Rs.",
        "Date & Time of loan application",
        "Date & Time of acceptance of loan"
    ]

    next_line_key = "KCC A/C No Sanction Limit (Rs.) 0/5 Bal as on date (Rs.)"

    results = {key: None for key in keys + [next_line_key]}

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for idx, line in enumerate(lines):
                for key in keys + [next_line_key]:

                    if key in line and results[key] is None:
                        value = line.split(key, 1)[-1].strip(" :")
                        results[key] = value

                        if key == next_line_key and idx + 1 < len(lines):
                            next_line_value = lines[idx + 1].strip()
                            results[key] += " " + next_line_value

    key_name_mapping = {
        "Date & Time of CIR generation": [
            "cibil_fetch_date",
            "cibil_fetch_time",
            "cibil_fetch_time_indicator"
        ],
        "CUST ID": ["cust_id"],
        "CIBIL Score/CIR": ["curr_cibil_score"],
        "Term Loan - Krishi Tatkal Rin Rs.": [
            "sanctioned_limit",
            "roi",
            "loan_account_no"
        ],
        "Date & Time of loan application": [
            "loan_application_date",
            "loan_application_time",
            "loan_application_indicator"
        ],
        "Date & Time of acceptance of loan": [
            "loan_acceptance_date",
            "loan_acceptance_time",
            "loan_acceptance_indicator"
        ],
        "KCC A/C No Sanction Limit (Rs.) 0/5 Bal as on date (Rs.)": [
            "kcc_acc_no",
            "kcc_limit",
            "outstanding_balance"
        ]
    }

    mapped_results = {}

    for pdf_key, new_keys in key_name_mapping.items():
        value = results.get(pdf_key)

        if value:
            parts = value.split()
            for i, new_key in enumerate(new_keys):
                mapped_results[new_key] = parts[i] if i < len(parts) else None
        else:
            for new_key in new_keys:
                mapped_results[new_key] = None

    return mapped_results

