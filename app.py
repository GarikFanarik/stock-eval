import streamlit as st
import pandas as pd
from main import get_financial_ratios,compare_with_target_values
st.session_state.stock = st.text_input("Enter the desired Stock")

if st.session_state.stock:
    res = get_financial_ratios(st.session_state.stock)
    st.subheader(res[1])
    #st.dataframe(res[0].T)
    st.dataframe(pd.concat([res[0].T, compare_with_target_values(res[0]).T],axis=1))

