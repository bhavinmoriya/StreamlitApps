import streamlit as st
from markdown_pdf import convert

st.set_page_config(page_title="Markdown to PDF Converter", page_icon="📄")
st.title("Markdown to PDF Converter")
st.write("Upload a Markdown file, and download it as a PDF.")

uploaded_file = st.file_uploader("Choose a Markdown file", type=["md", "markdown"])

if uploaded_file is not None:
    try:
        # Read the uploaded file
        markdown_content = uploaded_file.read().decode("utf-8")

        # Convert Markdown to PDF
        pdf_bytes = convert(markdown_content)

        # Provide download link for the PDF
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name="converted.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
