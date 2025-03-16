import streamlit as st
import requests
import pandas as pd
import base64
from mistralai import Mistral
from mistralai.models import SDKError
import fitz  # PyMuPDF for PDF text extraction

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
    st
