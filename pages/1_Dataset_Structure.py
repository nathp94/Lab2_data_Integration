import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dataset Structure", layout="wide")

st.title("A. Dataset Structure")
st.write("This page presents the column inventory, their data types, and their semantic meaning.")
semantic_meanings = st.session_state['semantic_meanings']


if 'datasets' not in st.session_state:
    st.warning("Please load the data from the home page (app.py) first.")
else:
    datasets = st.session_state['datasets']
    
    tabs = st.tabs(list(datasets.keys()))
    
    for tab, (name, df) in zip(tabs, datasets.items()):
        with tab:
            st.subheader(f"Table Structure: {name}")
            
            col1, col2 = st.columns(2)
            col1.metric("Number of rows", f"{df.shape[0]:,}")
            col2.metric("Number of columns", df.shape[1])
            
            st.markdown("### Column Inventory and Data Types")

            semantic_meanings = st.session_state['semantic_meanings']
            descriptions = []
            for col in df.columns:
                descriptions.append(semantic_meanings.get(name, {}).get(col, "no description"))

            structure_df = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type (Dtype)": [str(t) for t in df.dtypes],
                "Description (Semantic Meaning)": descriptions,
                "Example Value": [df[col].iloc[0] if not df[col].empty else "N/A" for col in df.columns]
            })
            
            st.dataframe(structure_df, use_container_width=True)
            
            st.markdown("### Preview of the first 5 rows")
            st.dataframe(df.head(), use_container_width=True)