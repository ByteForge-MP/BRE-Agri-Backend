import os
import re


def extract_data_html(text):

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    dpd_blocks = []
    current_block = {}
    dpd_mode = False
    dpd_line_count = 0
    previous_line = None

    customer_name = None
    credit_score_overall = None
    cibil_file_fetch_date = None

    inside_consumer_info = False

    for i, line in enumerate(lines):

        if "CONSUMER INFORMATION" in line:
            inside_consumer_info = True
            continue

        if inside_consumer_info and "NAME" in line:
            if i + 1 < len(lines):
                customer_name = lines[i + 1]
                inside_consumer_info = False
            continue

        if "SCORING FACTORS" in line:
            if i + 2 < len(lines):
                credit_score_overall = lines[i + 2]

        if "MEMBER REFERENCE NUMBER" in line:
            if i + 3 < len(lines):
                cibil_file_fetch_date = lines[i + 3]

        if "DAYS PAST DUE" in line and "ASSET" in line:
            dpd_mode = True
            dpd_line_count = 0
            current_block = {}
            previous_line = None
            continue

        if dpd_mode:
            dpd_line_count += 1

            if dpd_line_count > 72:
                if current_block:
                    dpd_blocks.append(current_block)
                dpd_mode = False
                current_block = {}
                continue

            key_match = re.search(r"[A-Z]{2,}", line)

            if key_match and previous_line:
                current_block[key_match.group()] = previous_line

            previous_line = line

    if current_block:
        dpd_blocks.append(current_block)

    return {
        "customer_name": customer_name,
        "credit_score_overall": credit_score_overall,
        "cibil_file_fetch_date": cibil_file_fetch_date,
        "dpd_blocks": dpd_blocks
    }
