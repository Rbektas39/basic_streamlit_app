import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Penguin Explorer", layout="wide")

st.title("🐧 Penguin Explorer")
st.write("Interactive exploration of the Palmer Penguins dataset.")

@st.cache_data
def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    candidates = ["penguins.csv", "penguins (1).csv", "your_data.csv"]

    for fname in candidates:
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df, fname

    raise FileNotFoundError(
        "Could not find penguins CSV in basic_streamlit_app/data/. "
        "Expected one of: penguins.csv, penguins (1).csv, your_data.csv"
    )

df, which_file = load_data()

st.caption(f"Loaded: `basic_streamlit_app/data/{which_file}`")

df = df.copy()
df.columns = [c.strip() for c in df.columns]

st.sidebar.header("Filters")

def multiselect_filter(label, col):
    if col in df.columns:
        options = sorted([x for x in df[col].dropna().unique()])
        chosen = st.sidebar.multiselect(label, options, default=options)
        return chosen
    return None

species_col = "species" if "species" in df.columns else ("Species" if "Species" in df.columns else None)
island_col = "island" if "island" in df.columns else ("Island" if "Island" in df.columns else None)
sex_col = "sex" if "sex" in df.columns else ("Sex" if "Sex" in df.columns else None)

chosen_species = multiselect_filter("Species", species_col) if species_col else None
chosen_island = multiselect_filter("Island", island_col) if island_col else None
chosen_sex = multiselect_filter("Sex", sex_col) if sex_col else None

body_mass_col = None
for c in ["body_mass_g", "body_mass", "Body Mass (g)", "body mass (g)"]:
    if c in df.columns:
        body_mass_col = c
        break

filtered = df
if species_col and chosen_species is not None:
    filtered = filtered[filtered[species_col].isin(chosen_species)]
if island_col and chosen_island is not None:
    filtered = filtered[filtered[island_col].isin(chosen_island)]
if sex_col and chosen_sex is not None:
    filtered = filtered[filtered[sex_col].isin(chosen_sex)]

if body_mass_col:
    non_null = filtered[body_mass_col].dropna()
    if len(non_null) > 0:
        min_v, max_v = float(non_null.min()), float(non_null.max())
        lo, hi = st.sidebar.slider(
            "Body mass range",
            min_value=min_v,
            max_value=max_v,
            value=(min_v, max_v)
        )
        filtered = filtered[
            (filtered[body_mass_col].isna()) |
            ((filtered[body_mass_col] >= lo) & (filtered[body_mass_col] <= hi))
        ]

st.subheader("Filtered dataset")
st.write(f"Rows: **{len(filtered):,}**")
st.dataframe(filtered, use_container_width=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered dataset as CSV",
    data=csv_bytes,
    file_name="filtered_penguins.csv",
    mime="text/csv",
)

st.subheader("Summary statistics")
numeric_cols = filtered.select_dtypes(include="number")
if numeric_cols.shape[1] > 0:
    st.dataframe(numeric_cols.describe().T, use_container_width=True)
else:
    st.info("No numeric columns available after filtering.")