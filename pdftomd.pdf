import streamlit as st
import pdfplumber
import json
import os

st.set_page_config(page_title="PDF to Markdown/JSON Converter", page_icon="📄")
st.title("PDF to Markdown/JSON Converter")
st.write("Upload a PDF file to convert it to Markdown or JSON.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        # Create output directory
        output_dir = "output/parsed_pdf"
        os.makedirs(output_dir, exist_ok=True)

        # Extract text from PDF
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # Save as Markdown
        markdown_path = os.path.join(output_dir, "output.md")
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Save as JSON
        json_path = os.path.join(output_dir, "output.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"text": text}, f, indent=4)

        # Provide download links
        with open(markdown_path, "rb") as f:
            st.download_button(
                label="Download Markdown",
                data=f,
                file_name="output.md",
                mime="text/markdown",
            )

        with open(json_path, "rb") as f:
            st.download_button(
                label="Download JSON",
                data=f,
                file_name="output.json",
                mime="application/json",
            )

        st.success("Conversion complete!")

    except Exception as e:
        st.error(f"An error occurred: {e}")
