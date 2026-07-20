import streamlit as st
from fpdf import FPDF
import markdown2
from bs4 import BeautifulSoup

st.set_page_config(page_title="Markdown to PDF Converter", page_icon="📄")
st.title("Markdown to PDF Converter")
st.write("Upload a Markdown file, and download it as a PDF.")

uploaded_file = st.file_uploader("Choose a Markdown file", type=["md", "markdown"])

if uploaded_file is not None:
    try:
        # Read the uploaded file
        markdown_content = uploaded_file.read().decode("utf-8")

        # Convert Markdown to HTML
        html_content = markdown2.markdown(markdown_content)

        # Extract text from HTML (strips formatting)
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()

        # Create a PDF using fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Split text into lines and write to PDF
        for line in text.split('\n'):
            pdf.cell(0, 10, line, ln=True)

        # Save PDF to bytes
        pdf_bytes = pdf.output(dest="S")

        # Provide download link for the PDF
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="converted.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
