import streamlit as st
import markdown2
from weasyprint import HTML
import os
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="Markdown to PDF Converter", page_icon="📄")
st.title("Markdown to PDF Converter")
st.write("Upload a Markdown file, and download it as a PDF.")

uploaded_file = st.file_uploader("Choose a Markdown file", type=["md", "markdown"])

if uploaded_file is not None:
    markdown_content = uploaded_file.read().decode("utf-8")
    html_content = markdown2.markdown(markdown_content)

    # Create a temporary HTML file
    with NamedTemporaryFile(delete=False, suffix=".html", mode="w+") as temp_html:
        temp_html.write(html_content)
        temp_html_path = temp_html.name

    # Convert HTML to PDF using weasyprint
    pdf_path = "output.pdf"
    HTML(temp_html_path).write_pdf(pdf_path)

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
