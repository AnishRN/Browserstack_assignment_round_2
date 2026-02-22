from fpdf import FPDF
import os
import time
import unicodedata


def sanitize_text(text):
    """Remove or replace characters that can't be encoded in Latin-1"""
    if text is None:
        return ""
    # Convert to string if not already
    text = str(text)
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    # Encode to latin-1, replacing problematic characters
    text = text.encode('latin-1', 'replace').decode('latin-1')
    return text


def generate_analysis_pdf(articles, translations, analysis):
    pdf = FPDF()
    pdf.set_auto_page_break(True, 10)

    pdf.add_page()
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, "El Pais Article Report", ln=True)

    pdf.set_font("Arial", size=12)

    for art, trans in zip(articles, translations):
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"Title: {sanitize_text(art['title'])}")
        pdf.multi_cell(0, 8, f"Translated: {sanitize_text(trans)}")
        pdf.multi_cell(0, 8, f"Author: {sanitize_text(art['author'])}")
        pdf.multi_cell(0, 8, f"Date: {sanitize_text(art['date'])}")
        pdf.ln(3)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Word Analysis", ln=True)

    pdf.set_font("Arial", size=12)
    if analysis and analysis.get("repeated"):
        for w, c in analysis["repeated"].items():
            pdf.multi_cell(0, 8, f"{sanitize_text(w)}: {c}")

    path = f"report_{int(time.time())}.pdf"
    pdf.output(path)
    return path
