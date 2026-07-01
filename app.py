import streamlit as st
import pandas as pd

st.set_page_config(page_title="Open Data Profiling - Accidents 2024", layout="wide")

st.title("Open Data Profiling Report - Road Accidents 2024")
st.write("Welcome to the data quality analysis application (Data Integration Lab).")


SEMANTIC_MEANINGS = {
    "Characteristics": {
        "Num_Acc": "Unique identification number of the accident.",
        "jour": "Day of the accident.",
        "mois": "Month of the accident.",
        "an": "Year of the accident.",
        "hrmn": "Time of the accident in hours and minutes (HHMM).",
        "lum": "Lighting conditions (1: Daylight, 2: Twilight/dawn, 3-5: Night with/without street lighting).",
        "dep": "Department: INSEE code of the department.",
        "com": "Commune: INSEE code of the department followed by 3 digits.",
        "agg": "Location: 1 – Outside built-up area, 2 – Inside built-up area.",
        "int": "Intersection: Type of intersection (1: Outside intersection, 2: X-intersection, 3: T-intersection, 6: Roundabout, etc.).",
        "atm": "Atmospheric conditions (1: Normal, 2-3: Rain, 5: Fog, etc.).",
        "col": "Type of collision between vehicles (1: Head-on, 2: Rear-end, 7: No collision, etc.).",
        "adr": "Postal address: Variable filled for accidents occurring inside built-up areas.",
        "lat": "Latitude of the accident location.",
        "long": "Longitude of the accident location."
    },
    "Locations": {
        "Num_Acc": "Accident identifier (foreign key to Characteristics).",
        "catr": "Category of road (1: Highway/Motorway, 2: National road, 3: Departmental road, 4: Communal road, etc.).",
        "voie": "Road number.",
        "V1": "Numerical index of the road number (e.g., 2 bis, 3 ter).",
        "V2": "Alphanumeric index letter of the road.",
        "circ": "Traffic regime (1: One-way, 2: Two-way/Bidirectional, 3: Divided highway/Separated carriageways).",
        "nbv": "Total number of traffic lanes.",
        "vosp": "Indicates the existence of a reserved lane (cycle lane, bus lane, etc.).",
        "prof": "Longitudinal profile: slope of the road (1: Flat, 2: Gradient/slope, 3: Crest/hilltop, 4: Valley/bottom).",
        "pr": "Reference landmark milestone number (upstream milestone).",
        "pr1": "Distance in meters to the upstream reference milestone.",
        "plan": "Plan view layout: road geometry (1: Straight line, 2-3: Curve, 4: S-shaped curve).",
        "lartpc": "Width of the central reservation / median strip if it exists (in meters).",
        "larrout": "Width of the roadway allocated to traffic (in meters).",
        "surf": "Road surface condition (1: Normal, 2: Wet, 5: Snowy, 7: Icy/frosty).",
        "infra": "Layout - Infrastructure (1: Tunnel, 2: Bridge, 6: Pedestrian zone, etc.).",
        "situ": "Location of the accident (1: On the roadway, 4: On the sidewalk, 5: On a cycle path).",
        "vma": "Maximum authorized speed limit at the location at the time of the accident."
    },
    "Vehicles": {
        "Num_Acc": "Accident identifier.",
        "id_vehicule": "Unique identifier of the vehicle (used to link users).",
        "Num_Veh": "Alphanumeric identifier of the vehicle within the accident.",
        "senc": "Direction of traffic (1: Increasing milestone numbers, 2: Decreasing milestone numbers).",
        "catv": "Category of vehicle (01: Bicycle, 07: Single passenger car, 10: Light commercial vehicle, 33: Motorcycle, 50: Motorized personal mobility device, etc.).",
        "obs": "Fixed obstacle hit (2: Tree, 4: Safety barrier/guardrail, 8: Post/pole, 13: Ditch, etc.).",
        "obsm": "Moving obstacle hit (1: Pedestrian, 2: Vehicle, 5-6: Animal).",
        "choc": "Initial point of impact (1: Front, 4: Rear, 7-8: Sides, 9: Multiple impacts).",
        "manv": "Main maneuver prior to the accident (1: No change in direction, 15: Turning, etc.).",
        "motor": "Type of vehicle engine/motorization (1: Combustion engine/hydrocarbons, 3: Electric, 5: Human power, etc.).",
        "occutc": "Number of occupants in the case of public transport."
    },
    "Users": {
        "Num_Acc": "Accident identifier.",
        "id_usager": "Unique identifier of the user.",
        "id_vehicule": "Unique identifier of the vehicle the user was in.",
        "num_Veh": "Alphanumeric identifier of the vehicle.",
        "place": "Seat position occupied in the vehicle by the user (10: Pedestrian).",
        "catu": "Category of user (1: Driver, 2: Passenger, 3: Pedestrian).",
        "grav": "Severity of injury (1: Unharmed, 2: Killed, 3: Injured and hospitalized, 4: Lightly injured).",
        "sexe": "Gender of the user (1: Male, 2: Female).",
        "An_nais": "Year of birth of the user.",
        "trajet": "Purpose of the journey (1: Home-to-work commute, 5: Leisure/walk, etc.).",
        "secu1": "Primary safety equipment used (Seatbelt, Helmet, Gloves, etc.).",
        "secu2": "Secondary safety equipment used.",
        "secu3": "Tertiary safety equipment used.",
        "locp": "Location of the pedestrian (On pedestrian crossing, on sidewalk, etc.).",
        "actp": "Action of the pedestrian (Crossing, moving, etc.).",
        "etatp": "Specifies whether the casualty pedestrian was alone or accompanied."
    }
}


@st.cache_data
def load_data():
    caract = pd.read_csv("2024_data/caract-2024.csv", sep=";", decimal=",", low_memory=False)
    vehicules = pd.read_csv("2024_data/vehicules-2024.csv", sep=";", decimal=",", low_memory=False)
    lieux = pd.read_csv("2024_data/lieux-2024.csv", sep=";", decimal=",", low_memory=False)
    usagers = pd.read_csv("2024_data/usagers-2024.csv", sep=";", decimal=",", low_memory=False)
    
    return {"Characteristics": caract, "Vehicles": vehicules, "Locations": lieux, "Users": usagers}

try:
    datasets = load_data()
    st.success("The 4 datasets have been successfully loaded!")
    
    st.session_state['datasets'] = datasets
    st.session_state['semantic_meanings'] = SEMANTIC_MEANINGS

    st.subheader("Data volumes overview:")
    for name, df in datasets.items():
        st.write(f"• **{name}** : {df.shape[0]:,} rows and {df.shape[1]} columns.")

except Exception as e:
    st.error(f"Error loading files: {e}")
    st.info("Please verify that your files are in the '2024_data' folder and that the separator is correct.")