import streamlit as st
from main import get_financial_ratios
st.session_state.stock = st.text_input("Enter the desired Stock")

if "stock" in st.session_state:
    st.dataframe(get_financial_ratios(st.session_state.stock))
