import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Data Quality Summary", layout="wide")

st.title("D. Data Quality Summary & Impact Analysis")
st.write("Executive dashboard summarizing data assets health and downstream analytical implications.")

if 'datasets' not in st.session_state:
    st.warning("Please load the data from the home page (app.py) first.")
else:
    datasets = st.session_state['datasets']
    liste_df = list(datasets.values())
    liste_names = list(datasets.keys())

    # --- 1. KPI SECTION ---
    st.header("1. Data Health KPIs")
    
    total_records = sum(len(df) for df in liste_df)
    total_strict_dups = sum(df.duplicated().sum() for df in liste_df)
    total_nan = sum(df.isnull().sum().sum() for df in liste_df)
    
    caract_df = datasets.get('Characteristics', liste_df[0])
    users_df = datasets.get('Users', liste_df[3])
    loc_df = datasets.get('Locations', liste_df[2])
    veh_df = datasets.get('Vehicles', liste_df[1])
    
    geo_anomalies = caract_df[(caract_df['lat'] == 0) | (caract_df['lat'].isna()) | (caract_df['lat'] == 0.0)].shape[0]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows Monitored", f"{total_records:,}")
    m2.metric("Standard Empty Cells (NaN)", f"{total_nan:,}", delta="Critical for an_nais", delta_color="inverse")
    m3.metric("Identified Strict Duplicates", total_strict_dups, delta="2 in Locations", delta_color="inverse")
    m4.metric("Invalid GPS Coordinates (0.0)", f"{geo_anomalies:,}", delta="Need Imputation", delta_color="off")

    st.markdown("---")

    # --- 2. REPORT SECTION ---
    st.header("2. Data Quality Report (Main Discovered Issues)")
    st.markdown(
        """
        Based on our programmatic profiling and manual statistical distributions review, 
        the 2024 French Road Accident dataset is overall structurally intact but presents **three major categories of quality anomalies**:
        """
    )
    
    report_col1, report_col2, report_col3 = st.columns(3)
    
    with report_col1:
        st.subheader("🚨 Hidden Missing Values")
        st.error(
            "**The '-1' System Mask:**\n\n"
            "Traditional `isna()` counts failed to catch massive data gaps. Numeric columns like `senc`, `catv`, "
            "`obs`, `choc`, and `manv` (Vehicles) or `surf`, `infra`, and `vma` (Locations) leverage `-1` to mean *Not specified*. "
            "This structural choice obscures the actual completeness of behavioral attributes."
        )
        
    with report_col2:
        st.subheader("⚠️ Severe Out-of-Bounds")
        st.warning(
            "**Extreme Values & Saisie Faults:**\n\n"
            "The `vma` (Speed Limit) attribute contains an impossible maximum of **900 km/h** in the Locations dataset. "
            "Additionally, while global geographic spans reflect overseas territories perfectly, records sitting precisely at `(0.0, 0.0)` "
            "represent critical telemetry reporting losses."
        )
        
    with report_col3:
        st.subheader("📉 Asymmetric Completeness")
        st.info(
            "**Contextual Sparsity vs. True Gaps:**\n\n"
            "Attributes like `occutc` (empty) and `lartpc` (empty) are technically healthy "
            "as they mirror real-world context (few bus crashes, rare median strips). Conversely, the gap in `an_nais` "
            "is highly critical because it breaks user profiling."
        )

    st.markdown("---")

    # --- NEW: 3. VISUAL EVIDENCE SECTION ---
    st.header("3. Visual Evidence of Data Anomalies")
    st.write("Deep dive visualizations into the exact distributions causing the flags above.")

    vis_col1, vis_col2 = st.columns(2)

    with vis_col1:
        st.subheader("The '-1' Hidden Gap in Vehicles Dataset")
        # Calcul de la proportion de -1 pour quelques colonnes clés de Vehicles
        cols_to_check = ['senc', 'obs', 'obsm', 'choc', 'manv']
        missing_minus_one = []
        
        for col in cols_to_check:
            if col in veh_df.columns:
                pct = (veh_df[col] == -1).mean() * 100
                missing_minus_one.append({'Feature': col, 'Missing/Hidden (-1) %': pct})
        
        if missing_minus_one:
            df_m1 = pd.DataFrame(missing_minus_one)
            fig_m1 = px.bar(
                df_m1, x='Missing/Hidden (-1) %', y='Feature', orientation='h',
                title="Percentage of Hidden Missing Values (Masked as -1)",
                labels={'Missing/Hidden (-1) %': '% of Total Records'},
                color='Missing/Hidden (-1) %', color_continuous_scale='Reds'
            )
            fig_m1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=350)
            st.plotly_chart(fig_m1, use_container_width=True)
        else:
            st.info("Vehicles dataframe structure not found as expected.")

    with vis_col2:
        st.subheader("Outlier Detection: Speed Limit (`vma`) Distribution")
        if 'vma' in loc_df.columns:
            # On simule un rapide value_counts pour éviter de saturer la mémoire si le dataset est immense
            vma_counts = loc_df['vma'].value_counts().reset_index()
            vma_counts.columns = ['Speed Limit (vma)', 'Count']
            
            fig_vma = px.scatter(
                vma_counts, x='Speed Limit (vma)', y='Count', 
                title="Frequency of Speed Limit Values (Spotting the 900 km/h Outlier)",
                log_y=True, size='Count', size_max=20
            )
            # Ajout d'une annotation pour pointer du doigt l'erreur
            fig_vma.add_annotation(
                x=900, y=1, text="Typo: 900 km/h!", showarrow=True, arrowhead=1, ax=-50, ay=-30, font=dict(color="red")
            )
            fig_vma.update_layout(height=350)
            st.plotly_chart(fig_vma, use_container_width=True)
        else:
            st.info("Locations dataframe or 'vma' column not found.")

    # Deuxième ligne de graphes pour la géographie et la complétude
    vis_col3, vis_col4 = st.columns(2)

    with vis_col3:
        st.subheader("Critical vs. Structural Missingness")
        # Comparaison de NaNs réels et de sens métier
        sparsity_data = []
        if 'an_nais' in users_df.columns:
            sparsity_data.append({'Metric': 'Birth Year (an_nais)<br><b>[CRITICAL GAP]</b>', 'Missing %': users_df['an_nais'].isnull().mean() * 100, 'Type': 'True Operational Gap'})
        if 'occutc' in veh_df.columns:
            sparsity_data.append({'Metric': 'Bus Occupants (occutc)<br><i>[STRUCTURAL]</i>', 'Missing %': veh_df['occutc'].isnull().mean() * 100, 'Type': 'Expected Sparsity'})
        if 'lartpc' in loc_df.columns:
            sparsity_data.append({'Metric': 'Median Width (lartpc)<br><i>[STRUCTURAL]</i>', 'Missing %': loc_df['lartpc'].isnull().mean() * 100, 'Type': 'Expected Sparsity'})
            
        if sparsity_data:
            df_sparse = pd.DataFrame(sparsity_data)
            fig_sparse = px.bar(
                df_sparse, x='Metric', y='Missing %', color='Type',
                title="Missing Rate: Structural Context vs. Data Loss",
                color_discrete_map={'True Operational Gap': '#EF553B', 'Expected Sparsity': '#636EFA'}
            )
            fig_sparse.update_layout(height=350, yaxis_range=[0, 105])
            st.plotly_chart(fig_sparse, use_container_width=True)

    with vis_col4:
        st.subheader("Geospatial Telemetry Loss")
        if 'lat' in caract_df.columns and 'long' in caract_df.columns:
            # Dataframe résumé pour le camembert
            valid_geo = caract_df[(caract_df['lat'] != 0) & (caract_df['lat'].notna()) & (caract_df['lat'] != 0.0)].shape[0]
            pie_df = pd.DataFrame({
                'Status': ['Valid Coordinates', 'Lost Telemetry (0.0 or NaN)'],
                'Count': [valid_geo, geo_anomalies]
            })
            fig_pie = px.pie(
                pie_df, values='Count', names='Status', 
                title="GPS Quality Breakdown",
                color='Status', color_discrete_map={'Valid Coordinates': '#00CC96', 'Lost Telemetry (0.0 or NaN)': '#AB63FA'}
            )
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # --- 4. DOWNSTREAM IMPACT SECTION ---
    st.header("4. Downstream Analytics & Architectural Impact")
    st.write("How these structural and quality issues directly threaten Business Intelligence and Machine Learning goals if left uncleaned:")

    st.markdown(
        """
        | Identified Issue | Downstream Business/Analytical Impact | Silver Layer Mitigation Strategy |
        | :--- | :--- | :--- |
        | **Absurd Speed Max (`vma` = 900)** | Biais machine learning models predicting accident severity, pulling statistical averages upwards artificially. | Clamp out-of-bounds metrics to regional road category rules or mark as `Null`. |
        | **Undetected `-1` Values** | Categorical grouping (`GROUP BY`) will interpret `-1` as a real category, treating missing records as a valid type of vehicle or weather. | Programmatically maps all `-1` occurrences into explicit `'Unknown'` string labels. |
        | **Missing Birth Year (`an_nais`)** | Prevents core demographic segmentations (e.g., calculating insurance risks or evaluating youth safety campaigns). | Impute using the distribution's median age, or generate a specific proxy category flag. |
        | **Strict Duplicates (2 rows)** | Minimal direct threat, but breaches data warehouse strict primary constraints and slightly duplicates count results. | Isolate and wipe from the staging pipeline via standard execution of `.drop_duplicates()`. |
        | **0.0 GPS Coordinates** | Breaks geospatial mapping widgets, plotting car accidents inside the Atlantic Ocean rather than on French roads. | Convert `0` entries to real `Null` tokens or fall back on municipal INSEE codes (`com`) for rough imputation. |
        """
    )