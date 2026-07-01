import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consistency & Validity Checks", layout="wide")

st.title("C. Consistency and Validity Checks")
st.write("Identification of out-of-bounds values, categorical anomalies, and duplicate records.")

if 'datasets' not in st.session_state:
    st.warning("Please load the data from the home page (app.py) first.")
else:
    datasets = st.session_state['datasets']
    
    liste_df = list(datasets.values())
    liste_names = list(datasets.keys())
    
    caract = liste_df[0]
    vehicules = liste_df[1]
    lieux = liste_df[2]
    usagers = liste_df[3]

    st.header("1. Value Ranges & Statistical Summaries (.describe())")
    st.write("Exploration of statistical indicators (min, max, mean) to manually detect distribution anomalies.")

    tabs_desc = st.tabs(list(datasets.keys()))
    
    for tab, (name, df) in zip(tabs_desc, datasets.items()):
        with tab:
            st.subheader(f"Statistical summary of numerical columns: {name}")
            
            stats_df = df.describe()
            st.dataframe(stats_df, use_container_width=True)

    st.markdown("---")
    st.markdown("# Values range : ")

    st.markdown("""
                ## For Characteristics :
                - Geographics Anomalies : While France's mainland coordinates span roughly from $41^\circ$ to $51^\circ$ North and $-5^\circ$ to $9^\circ$ East, the extreme latitude and longitude values in the data (ranging from $-22.4$ to $51.1$ and $-178.1$ to $167.9$) are not entirely errors. A semantic analysis reveals that these extremes account for French overseas territories (DOM-TOM) like Réunion or New Caledonia. However, any coordinates pointing near $0,0$ or falling entirely outside actual French territories should be flagged as geographical anomalies and cleaned in the Silver data layer.
                - Hidden Missing Values : The collision type column (col) contains a minimum value of $-1$, which according to the data dictionary represents "Not specified". It is semantically a missing value that needs to be cleaned                
                ## For Vehicule :
                - Hidden Missing Values : Nearly all categorical columns (including senc, catv, obs, and others) feature a minimum value of $-1$, which the data dictionary defines as "Not specified". Because these represent system error codes rather than empty cells (NaN). They must be converted to Nan or whatever null type to be handled.
                - Public Transport Occupants : The public transport occupants column (occutc) has a row count of just $949$ compared to the $92,678$ records found in all other columns, confirming that over 98% of the data is missing. This is a normal, context-driven pattern: out of all vehicles involved in 2024 accidents, only $949$ were public transit vehicles
                ## For Locations :
                - Absurd Maximum Speed : The maximum speed limit (vma) column contains a highly exaggerated maximum value of $900$ km/h.
                - Strip Width : $33$ out of $70,248$ accident records, confirming a $99.95\%$ missing data rate. This structural gap is contextually normal, as the vast majority of accident locations simply do not feature a median strip.
                - Missing Data for Road Width : For the road width variable (larrout), the minimum value as well as both the 25% and 50% quartiles are entirely stuck at $-1$. This indicates that for over half of all recorded accidents, law enforcement did not collect or input the exact width of the roadway.
                - Hidden Missing Values : Consistent with the rest of the dataset, several infrastructure and environmental variables (such as v1, circ, vosp, prof, plan, surf, infra, and situ) all report a minimum value of $-1$. 
                ## For Users :
                - Age Profiles and Extreme Values : The minimum birth year is $1914$, that means someone had 110 years old when this person had the accident. We even have a maximum of 2024, that means we had a newborn. While the upper age bound is an extreme rarity that could be a typo, the boundaries remain valid overall, with no impossible future dates or negative ages.
                - Hidden Missing Values : Unsurprisingly, the value $-1$ reappears as the minimum across several behavioral and demographic attributes, including place, sexe, trajet, secu1, secu2, secu3, locp, and etatp.
                """)
    st.markdown("---")
    st.header("2. Duplicate Records Quantification")
    st.write("Analysis of strict data duplication (100% identical rows) across the 2024 datasets.")
    
    dup_summary = []
    
    for i, df in enumerate(liste_df):
        name = liste_names[i]
        total_rows = len(df)
        
        strict_dups = df.duplicated().sum()
        strict_pct = (strict_dups / total_rows) * 100

        dup_summary.append({
            "Dataset": name,
            "Total Rows": total_rows,
            "Strict Duplicates (Count)": strict_dups,
            "Strict Duplicates (%)": f"{strict_pct:.4f} %"
        })

    df_dup_report = pd.DataFrame(dup_summary)
    st.dataframe(df_dup_report, use_container_width=True, hide_index=True)
    
    st.markdown("""
                The Characteristics, Vehicles, and Users tables contain exactly zero complete duplicate rows, while the Locations table possesses just two strict duplicates—representing an infinitesimal rate of $0.0028\%$. 
                """)
