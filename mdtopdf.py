import streamlit as st
import markdown2
import pdfkit
import os
from tempfile import NamedTemporaryFile

# Set page title and description
st.set_page_config(page_title="Markdown to PDF Converter", page_icon="📄")
st.title("Markdown to PDF Converter")
st.write("Upload a Markdown file, and download it as a PDF.")

# File uploader
uploaded_file = st.file_uploader("Choose a Markdown file", type=["md", "markdown"])

if uploaded_file is not None:
    # Read the uploaded file
    markdown_content = uploaded_file.read().decode("utf-8")

    # Convert Markdown to HTML
    html_content = markdown2.markdown(markdown_content)

    # Create a temporary HTML file for pdfkit
    with NamedTemporaryFile(delete=False, suffix=".html") as temp_html:
        temp_html.write(html_content.encode("utf-8"))
        temp_html_path = temp_html.name

    # Convert HTML to PDF
    pdf_path = "output.pdf"
    pdfkit.from_file(temp_html_path, pdf_path)

    # Clean up the temporary HTML file
    os.unlink(temp_html_path)

    # Provide download link for the PDF
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name="converted.pdf",
            mime="application/pdf",
        )

    # Clean up the PDF file
    os.unlink(pdf_path)
