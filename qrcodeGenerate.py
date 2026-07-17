import streamlit as st
import qrcode
from PIL import Image
import io

# App title and description
st.title("QR Code Generator")
st.write("Generate a custom QR code for any link. Adjust the settings below and download your QR code.")

# User inputs
link = st.text_input("Enter the link (URL):", "https://github.com/bhavinmoriya")
version = st.slider("QR Code Version (Size):", 1, 40, 2)
error_correction = st.selectbox(
    "Error Correction Level:",
    ["Low (L)", "Medium (M)", "Quartile (Q)", "High (H)"]
)
box_size = st.slider("Box Size (Pixel per module):", 1, 20, 10)
border = st.slider("Border Size (Modules):", 0, 10, 4)
fill_color = st.color_picker("Fill Color:", "#000000")
back_color = st.color_picker("Background Color:", "#FFFFFF")

# Map error correction level to qrcode constants
error_correction_map = {
    "Low (L)": qrcode.constants.ERROR_CORRECT_L,
    "Medium (M)": qrcode.constants.ERROR_CORRECT_M,
    "Quartile (Q)": qrcode.constants.ERROR_CORRECT_Q,
    "High (H)": qrcode.constants.ERROR_CORRECT_H,
}

# Generate QR code
if st.button("Generate QR Code"):
    if not link:
        st.error("Please enter a valid link.")
    else:
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=version,
                error_correction=error_correction_map[error_correction],
                box_size=box_size,
                border=border,
            )
            qr.add_data(link)
            qr.make(fit=True)

            # Create PIL image
            img = qr.make_image(fill_color=fill_color, back_color=back_color)

            # Convert PIL image to bytes
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Display the QR code
            st.image(byte_im, caption="Generated QR Code", use_column_width=True)

            # Download button
            st.download_button(
                label="Download QR Code",
                data=byte_im,
                file_name="qrcode.png",
                mime="image/png",
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
