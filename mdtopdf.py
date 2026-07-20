import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import markdown2
from bs4 import BeautifulSoup
import io

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

        # Create a PDF using reportlab
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Use Helvetica (built-in Unicode font in newer reportlab versions)
        c.setFont("Helvetica", 12)

        # Split text into lines and write to PDF
        y = 750  # Starting y position
        for line in text.split('\n'):
            c.drawString(50, y, line)
            y -= 15  # Move to the next line

        c.save()
        pdf_bytes = buffer.getvalue()

        # Provide download link for the PDF
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="converted.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
