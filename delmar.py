import streamlit as st
import requests
import pandas as pd
import base64
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

# 2. Input Shareable Links
st.subheader("Enter Shareable Links to Files")
input_links = st.text_area("Paste OneDrive/OneNote shareable links (one per line)", value="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

if not input_links:
    st.info("Please paste the shareable links to continue.")
    st.stop()

# Split links into a list
file_links = input_links.strip().split("\n")

# 3. Process Button & OCR Handling
if st.button("Process"):
    client = Mistral(api_key=api_key)
    extracted_data = []

    for link in file_links:
        try:
            # Download the file from the shareable link
            response = requests.get(link)
            if response.status_code != 200:
                st.error(f"Failed to download file from {link}. Status code: {response.status_code}")
                continue

            file_bytes = response.content
            file_name = link.split("/")[-1]  # Extract file name from the link

            # Prepare the document payload based on file type
            if file_name.endswith('.pdf'):
                encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                document = {
                    "type": "document_base64",  # Correct type for PDFs
                    "document_base64": encoded_file  # Correct field for PDFs
                }
            else:  # Assume it's an image
                mime_type = "image/jpeg" if file_name.endswith('.jpg') or file_name.endswith('.jpeg') else "image/png"
                encoded_image = base64.b64encode(file_bytes).decode("utf-8")
                document = {
                    "type": "image_base64",  # Correct type for images
                    "image_base64": encoded_image  # Correct field for images
                }

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

        except Exception as e:
            st.error(f"Error processing {link}: {e}")

    st.session_state["ocr_result"] = extracted_data

# 4. Display Extracted Data and Download Excel
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
