import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="YProfiling Global Report", layout="wide")

st.title("E. Automated Data Profiling Report")
st.write("Exploration of the full HTML profiling report generated via ydata-profiling.")


html_file_path = "rapport_global_2024.html"

if not os.path.exists(html_file_path):
    st.error(f"The file `{html_file_path}` was not found at the root of your project.")
    st.info("Please make sure the generated HTML report is placed in your main project directory.")
else:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    st.success("YData Profiling report loaded successfully!")
    
    components.html(html_content, height=900, scrolling=True)