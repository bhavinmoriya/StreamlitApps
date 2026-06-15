import streamlit as st
import pikepdf
import os
import zipfile
from io import BytesIO

# App title
st.title("🧹 PDF Cleaner (Batch Mode)")
st.write("Upload multiple PDFs to remove hyperlinks, annotations, form fields, and JavaScript.")

# File uploader (allow multiple files)
uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    # Create a temporary directory for cleaned files
    temp_dir = "temp_cleaned_pdfs"
    os.makedirs(temp_dir, exist_ok=True)

    # Clean each PDF
    cleaned_files = []
    for uploaded_file in uploaded_files:
        input_path = os.path.join(temp_dir, uploaded_file.name)
        output_path = os.path.join(temp_dir, f"cleaned_{uploaded_file.name}")

        # Save the uploaded file
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Clean the PDF
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
                cleaned_files.append(output_path)
                st.success(f"✅ Cleaned: {uploaded_file.name}")

        except Exception as e:
            st.error(f"❌ Error cleaning {uploaded_file.name}: {e}")

    # Create a ZIP file for download
    if cleaned_files:
        zip_filename = "cleaned_pdfs.zip"
        zip_path = os.path.join(temp_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in cleaned_files:
                zipf.write(file, os.path.basename(file))

        # Download button for the ZIP file
        with open(zip_path, "rb") as f:
            zip_data = f.read()
        st.download_button(
            label="⬇️ Download All Cleaned PDFs (ZIP)",
            data=zip_data,
            file_name=zip_filename,
            mime="application/zip",
        )

    # Clean up temporary files
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)
