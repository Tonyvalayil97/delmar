import streamlit as st
import os
import base64
import pandas as pd
from mistralai import Mistral

st.set_page_config(layout="wide", page_title="Mistral OCR App", page_icon="🖥️")
st.title("Mistral OCR App")
st.markdown("<h3 style color: white;'>Built by <a href='https://github.com/AIAnytime'>AI Anytime with ❤️ </a></h3>", unsafe_allow_html=True)
with st.expander("Expand Me"):
    st.markdown("""
    This application allows you to extract information from pdf/image based on Mistral OCR. Built by AI Anytime.
    """)

# 1. API Key Input
api_key = st.text_input("Enter your Mistral API Key", type="password")
if not api_key:
    st.info("Please enter your API key to continue.")
    st.stop()

# Initialize session state variables for persistence
if "ocr_result" not in st.session_state:
    st.session_state["ocr_result"] = None
if "preview_src" not in st.session_state:
    st.session_state["preview_src"] = None
if "image_bytes" not in st.session_state:
    st.session_state["image_bytes"] = None

# 2. Choose file type: PDF or Image
file_type = st.radio("Select file type", ("PDF", "Image"))

# 3. Use a relative path for the upload folder
folder_path = "UPLOAD_FOLDER"

# Check if the folder exists
if not os.path.exists(folder_path):
    st.error(f"The folder '{folder_path}' does not exist. Please create it and add files.")
    st.stop()

# Get list of files in the folder
files_in_folder = os.listdir(folder_path)
uploaded_files = [file for file in files_in_folder if file.endswith(('.pdf', '.jpg', '.jpeg', '.png'))]

if not uploaded_files:
    st.error("No valid files found in the upload folder.")
    st.stop()

# 4. Process Button & OCR Handling
if st.button("Process"):
    client = Mistral(api_key=api_key)
    extracted_data = []

    for file_name in uploaded_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "rb") as file:
            file_bytes = file.read()

        if file_name.endswith('.pdf'):
            encoded_file = base64.b64encode(file_bytes).decode("utf-8")
            document = {
                "type": "document_base64",
                "document_base64": encoded_file
            }
            preview_src = f"data:application/pdf;base64,{encoded_file}"
        else:
            mime_type = "image/jpeg" if file_name.endswith('.jpg') or file_name.endswith('.jpeg') else "image/png"
            encoded_image = base64.b64encode(file_bytes).decode("utf-8")
            document = {
                "type": "image_url",
                "image_url": f"data:{mime_type};base64,{encoded_image}"
            }
            preview_src = f"data:{mime_type};base64,{encoded_image}"
            st.session_state["image_bytes"] = file_bytes

        with st.spinner(f"Processing {file_name}..."):
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest",
                document=document,
                include_image_base64=True
            )
            try:
                if hasattr(ocr_response, "pages"):
                    pages = ocr_response.pages
                elif isinstance(ocr_response, list):
                    pages = ocr_response
                else:
                    pages = []
                result_text = "\n\n".join(page.markdown for page in pages)
                if not result_text:
                    result_text = "No result found."
            except Exception as e:
                result_text = f"Error extracting result: {e}"

            # Extract specific fields from the OCR result
            # This is a placeholder for the actual extraction logic
            date = "Extracted Date"
            shipper_name = "Extracted Shipper Name"
            weight = "Extracted Weight"
            volume = "Extracted Volume"
            final_amount = "Extracted Final Amount"

            extracted_data.append({
                "Date": date,
                "Shipper Name": shipper_name,
                "Weight": weight,
                "Volume": volume,
                "Final Amount": final_amount
            })

    st.session_state["ocr_result"] = extracted_data

# 5. Display Extracted Data and Download Excel
if st.session_state["ocr_result"]:
    st.subheader("Extracted Data")
    df = pd.DataFrame(st.session_state["ocr_result"])
    st.write(df)

    # Create a download link for the Excel file
    excel_file = "extracted_data.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{excel_file}">Download Excel File</a>'
    st.markdown(href, unsafe_allow_html=True)
