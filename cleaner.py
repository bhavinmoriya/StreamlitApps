import streamlit as st
import pikepdf
import os
from io import BytesIO

# App title
st.title("🧹 PDF Cleaner")
st.write("Remove hyperlinks, annotations, form fields, and JavaScript from a PDF.")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    # Save the uploaded file temporarily
    input_path = "temp_input.pdf"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Clean the PDF
    output_path = "temp_output.pdf"
    try:
        with pikepdf.Pdf.open(input_path) as pdf:
            # Remove JavaScript
            if "/JavaScript" in pdf.Root:
                del pdf.Root.JavaScript

            # Remove AcroForm (fillable form fields)
            if "/AcroForm" in pdf.Root:
                del pdf.Root.AcroForm

            # Remove annotations (including hyperlinks)
            for page in pdf.pages:
                if "/Annots" in page:
                    del page.Annots

            # Save the cleaned PDF
            pdf.save(output_path)

        # Success message
        st.success("PDF cleaned successfully!")

        # Download button
        with open(output_path, "rb") as f:
            cleaned_pdf = f.read()
        st.download_button(
            label="⬇️ Download Cleaned PDF",
            data=cleaned_pdf,
            file_name="cleaned_output.pdf",
            mime="application/pdf",
        )

    except Exception as e:
        st.error(f"Error cleaning PDF: {e}")

    # Clean up temporary files
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
