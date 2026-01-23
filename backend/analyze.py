
# ##analyze.py
# import pandas as pd
# import pdfplumber
# import math
# from backend.llm import call_llm


# # -------------------------------
# # JSON SANITIZER (CRITICAL)
# # -------------------------------

# def clean_for_json(obj):
#     if isinstance(obj, dict):
#         return {k: clean_for_json(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [clean_for_json(v) for v in obj]
#     elif isinstance(obj, float):
#         if math.isnan(obj) or math.isinf(obj):
#             return None
#         return obj
#     else:
#         return obj


# # -------------------------------
# # PDF TEXT EXTRACTION
# # -------------------------------

# def extract_text_from_pdf(upload_file):
#     upload_file.file.seek(0)

#     text = ""
#     with pdfplumber.open(upload_file.file) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"

#     return text


# # -------------------------------
# # FACT EXTRACTION FROM TABLES
# # -------------------------------

# def extract_facts_from_df(df, filename):
#     facts = []

#     # Normalize column names
#     df.columns = [str(c).strip() for c in df.columns]

#     # Detect vendor column
#     vendor_col = None
#     for col in df.columns:
#         if "vendor" in col.lower():
#             vendor_col = col
#             break

#     if vendor_col is None:
#         return facts

#     for _, row in df.iterrows():
#         vendor = row.get(vendor_col)
#         if not vendor or pd.isna(vendor):
#             continue

#         for col in df.columns:
#             if col == vendor_col:
#                 continue

#             val = row.get(col)

#             if isinstance(val, (int, float)) and not pd.isna(val):
#                 facts.append({
#                     "entity_type": "vendor",
#                     "entity_name": str(vendor).strip(),
#                     "attribute": col.lower().strip(),
#                     "value": float(val),
#                     "source": filename
#                 })

#     return facts


# # -------------------------------
# # MAIN ANALYSIS FUNCTION
# # -------------------------------

# async def analyze_files(files):
#     summaries = []
#     facts = []

#     for f in files:
#         filename = f.filename
#         name = filename.lower()

#         try:
#             # ---------------- CSV ----------------
#             if name.endswith(".csv"):
#                 f.file.seek(0)
#                 df = pd.read_csv(f.file)
#                 df = df.where(pd.notnull(df), None)

#                 summaries.append({
#                     "filename": filename,
#                     "type": "csv",
#                     "rows": int(len(df)),
#                     "columns": list(df.columns),
#                     "sample": df.head(3).to_dict(orient="records")
#                 })

#                 try:
#                     facts.extend(extract_facts_from_df(df, filename))
#                 except Exception:
#                     pass  # never let facts break analysis

#             # ---------------- EXCEL ----------------
#             elif name.endswith(".xls") or name.endswith(".xlsx"):
#                 f.file.seek(0)

#                 # Always read first sheet only (robust default)
#                 df = pd.read_excel(f.file, sheet_name=0)
#                 df = df.where(pd.notnull(df), None)

#                 summaries.append({
#                     "filename": filename,
#                     "type": "excel",
#                     "rows": int(len(df)),
#                     "columns": list(df.columns),
#                     "sample": df.head(3).to_dict(orient="records")
#                 })

#                 try:
#                     facts.extend(extract_facts_from_df(df, filename))
#                 except Exception:
#                     pass

#             # ---------------- PDF ----------------
#             elif name.endswith(".pdf"):
#                 text = extract_text_from_pdf(f)

#                 if len(text.strip()) < 100:
#                     summaries.append({
#                         "filename": filename,
#                         "type": "pdf",
#                         "error": "No extractable text found (likely scanned PDF)"
#                     })
#                 else:
#                     summaries.append({
#                         "filename": filename,
#                         "type": "pdf",
#                         "text_preview": text[:1500]
#                     })

#                 # No facts from PDFs yet (by design)

#             # ---------------- UNSUPPORTED ----------------
#             else:
#                 summaries.append({
#                     "filename": filename,
#                     "type": "unsupported",
#                     "error": "Unsupported file type"
#                 })

#         except Exception as e:
#             summaries.append({
#                 "filename": filename,
#                 "type": "error",
#                 "error": str(e)
#             })

#     # ---------------- LLM ANALYSIS ----------------
#     analysis = await call_llm(summaries, facts)

#     result = {
#         "vendor_data": summaries,
#         "facts": facts,
#         "analysis": analysis
#     }

#     return clean_for_json(result)

# backend/analyze.py

import pandas as pd
import pdfplumber
import math
from typing import List
from fastapi import UploadFile

from backend.llm import call_llm


# -------------------------------
# JSON SANITIZER (CRITICAL)
# -------------------------------

def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    else:
        return obj


# -------------------------------
# PDF TEXT EXTRACTION
# -------------------------------

def extract_text_from_pdf(upload_file: UploadFile) -> str:
    upload_file.file.seek(0)

    text = ""
    with pdfplumber.open(upload_file.file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# -------------------------------
# FACT EXTRACTION FROM TABLES
# -------------------------------

def extract_facts_from_df(df: pd.DataFrame, filename: str) -> list:
    facts = []

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    # Detect vendor column
    vendor_col = None
    for col in df.columns:
        if "vendor" in col.lower():
            vendor_col = col
            break

    if vendor_col is None:
        return facts

    for _, row in df.iterrows():
        vendor = row.get(vendor_col)

        if not vendor or pd.isna(vendor):
            continue

        for col in df.columns:
            if col == vendor_col:
                continue

            val = row.get(col)

            if isinstance(val, (int, float)) and not pd.isna(val):
                facts.append({
                    "entity_type": "vendor",
                    "entity_name": str(vendor).strip(),
                    "attribute": col.lower().strip(),
                    "value": float(val),
                    "source": filename
                })

    return facts


# -------------------------------
# MAIN ANALYSIS FUNCTION
# -------------------------------

async def analyze_files(files: List[UploadFile]) -> dict:
    summaries = []
    facts = []

    for f in files:
        filename = f.filename
        name = filename.lower()

        try:
            # ---------------- CSV ----------------
            if name.endswith(".csv"):
                f.file.seek(0)
                df = pd.read_csv(f.file)
                df = df.where(pd.notnull(df), None)

                summaries.append({
                    "filename": filename,
                    "type": "csv",
                    "rows": int(len(df)),
                    "columns": list(df.columns),
                    "sample": df.head(3).to_dict(orient="records")
                })

                try:
                    facts.extend(extract_facts_from_df(df, filename))
                except Exception:
                    pass  # facts must never break analysis

            # ---------------- EXCEL ----------------
            elif name.endswith(".xls") or name.endswith(".xlsx"):
                f.file.seek(0)
                df = pd.read_excel(f.file, sheet_name=0)
                df = df.where(pd.notnull(df), None)

                summaries.append({
                    "filename": filename,
                    "type": "excel",
                    "rows": int(len(df)),
                    "columns": list(df.columns),
                    "sample": df.head(3).to_dict(orient="records")
                })

                try:
                    facts.extend(extract_facts_from_df(df, filename))
                except Exception:
                    pass

            # ---------------- PDF ----------------
            elif name.endswith(".pdf"):
                text = extract_text_from_pdf(f)

                if len(text.strip()) < 100:
                    summaries.append({
                        "filename": filename,
                        "type": "pdf",
                        "error": "No extractable text found (likely scanned PDF)"
                    })
                else:
                    summaries.append({
                        "filename": filename,
                        "type": "pdf",
                        "text_preview": text[:1500]
                    })

            # ---------------- UNSUPPORTED ----------------
            else:
                summaries.append({
                    "filename": filename,
                    "type": "unsupported",
                    "error": "Unsupported file type"
                })

        except Exception as e:
            summaries.append({
                "filename": filename,
                "type": "error",
                "error": str(e)
            })

    # ---------------- LLM ANALYSIS ----------------
    analysis = await call_llm(summaries, facts)

    result = {
        "vendor_data": summaries,
        "facts": facts,
        "analysis": analysis
    }

    return clean_for_json(result)
