import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
import tempfile
import re

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def convert_date(short_date):
    day, month, year = short_date.split('.')
    year = '20' + year if int(year) < 50 else '19' + year
    return f"{day}.{month}.{year}"

def extract_data_from_image(image):
    text = pytesseract.image_to_string(image, lang='deu')

    name_match = re.search(r'Name.*?:\s*([A-ZÄÖÜ][a-zäöüß]+),\s*([A-ZÄÖÜ][a-zäöüß]+)', text)
    zeitraum_match = re.search(r'(\d{2}\.\d{2}\.\d{2})\s*[–-]\s*(\d{2}\.\d{2}\.\d{2})', text)

    if name_match and zeitraum_match:
        nachname = name_match.group(1)
        vorname = name_match.group(2)
        start = convert_date(zeitraum_match.group(1))
        ende = convert_date(zeitraum_match.group(2))
        return f"VO {start} - {ende} {nachname}, {vorname}.pdf"
    return None

def process_pdf(uploaded_pdf):
    images = convert_from_bytes(uploaded_pdf.read())
    if not images:
        return None, None

    filename = extract_data_from_image(images[0])
    if not filename:
        return None, None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_pdf.getvalue())
        tmp_path = tmp_file.name

    return filename, tmp_path

st.title("🩺 Verordnungs-Umbenenner")
st.write("Lade Verordnungen (PDFs) hoch, sie werden automatisch umbenannt.")

st.code("VO 01.05.2025 - 31.12.2025 Nachname, Vorname.pdf")

uploaded_files = st.file_uploader("PDFs hochladen", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_pdf in uploaded_files:
        filename, path = process_pdf(uploaded_pdf)
        if filename:
            with open(path, "rb") as f:
                st.download_button(
                    label=f"📥 {filename}",
                    data=f,
                    file_name=filename,
                    mime="application/pdf"
                )
        else:
            st.error(f"⚠️ Konnte keine Daten aus {uploaded_pdf.name} lesen.")
