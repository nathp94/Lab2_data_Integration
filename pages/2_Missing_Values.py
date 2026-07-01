import streamlit as st
import pandas as pd

st.set_page_config(page_title="Missing Values & Completeness", layout="wide")

st.title("B. Missing Values and Completeness")
st.write("Quantitative analysis of completeness rates, identification of critical gaps, and remediation strategies.")

semantic_meanings = st.session_state['semantic_meanings']

if 'datasets' not in st.session_state:
    st.warning("Please load the data from the home page (app.py) first.")
else:
    datasets = st.session_state['datasets']
    
    st.header("1. Missing Percentages")
    
    tabs = st.tabs(list(datasets.keys()))
    
    for tab, (name, df) in zip(tabs, datasets.items()):
        with tab:
            st.subheader(f"Missing Values Analysis: {name} Table")
            
            missing_count = df.isnull().sum()
            missing_percent = (df.isnull().sum() / len(df)) * 100

            descriptions = []
            for col in df.columns:
                descriptions.append(semantic_meanings.get(name, {}).get(col, "no description"))

            missing_df = pd.DataFrame({
                "Column": df.columns,
                "Description (Semantic Meaning)": descriptions,
                "Missing Values (NaN)": missing_count,
                "Percentage (%)": missing_percent.round(2)
            }).sort_values(by="Percentage (%)", ascending=False)
            
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
            
            if missing_count.sum() == 0:
                st.success("No standard missing values (NaN) detected in this table!")
            else:
                st.info(f"Total of {missing_count.sum():,} empty fields (NaN) detected.")

    st.markdown("---")

    st.header("2. Critical Analysis & Remediation Strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Critical missingness")
        st.markdown(
        """
        * **`an_nais` (2.06% - Low but Critical):** The absence of the birth year prevents calculating the user's age. This is a **highly critical** gap for road safety analysis (e.g., targeting young drivers or seniors).
        * **`voie` (18.98% - Moderate):** Nearly 19% of roads do not have a number recorded. This impacts the precise traceability of major accident-prone routes.
        * **`occutc` (98.98%) and `lartpc` (99.95%):** These extremely high rates **are not anomalies**. They are explained semantically: the majority of accidents do not involve public transport (`occutc`) and do not feature a central reservation / median strip (`lartpc`). These are "contextual missing values."
        * **`v2` (91.58%) and `adr` (4.25%):** The address (`adr`) is missing outside built-up areas (which is expected according to the documentation). The road index letter (`v2`) (e.g., National Road 'A') is rarely used.
        """
    )
        
    with col2:
        st.subheader("Remediation strategies")
        st.markdown(
        """
        For the transformation stage of our Medallion architecture, the following actions will be implemented:
        
        1. **For `an_nais`:** Do not drop rows (to avoid losing overall accident data). Instead, impute using the table's median age or set the calculated age to `-1` (Unknown) in the final Users table.
        2. **For `voie`:** Standardize the missing textual value to `'Unknown'` to prevent aggregation errors during `GROUP BY` operations in the Gold layer.
        3. **For `occutc` and `lartpc`:** Replace `NaN` values with `0`. Programmatically, a `NaN` in `occutc` signifies "0 public transport occupants involved." This transformation avoids distorting summation metrics.
        4. **For `v2` and `adr`:** Replace with `'N/A'` (Not Applicable) to clarify that the missing data is structural and tied directly to the accident context.
        """
    )  