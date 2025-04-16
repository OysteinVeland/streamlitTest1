import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# Load the CSV data into a DataFrame
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSoPr88VI9diu7isjOUtJwR1zIHQxn3Bdk0XsLKsbFXsOWbtYwdvaGkKLaFUMqOLDEORT3AdzOFTMCa/pub?gid=841858480&single=true&output=csv"
df = pd.read_csv(csv_url)

# Ensure that the '%' column is treated the same in both df and filtered_df
df['%'] = df['%'].astype(str).str.replace(",", ".", regex=False).str.strip()
df['%'] = pd.to_numeric(df['%'], errors='coerce')  # Convert to float, non-convertibles become NaN

df['Snitt pr deltager'] = df['Snitt pr deltager'].astype(str).str.replace(",", ".", regex=False).str.strip()
df['Snitt pr deltager'] = pd.to_numeric(df['Snitt pr deltager'], errors='coerce').round(1)

# Load the illustration image
illustrationimage = Image.open('beerpals.png')

st.header("Ølhistorikk")

col1, col2 = st.columns(2)

# Country filter
unique_countries = sorted(df['Land'].dropna().astype(str).unique())
countries = ["Alle land"] + unique_countries
with col1:
    selected_country = st.selectbox("", options=countries)
    if selected_country != "Alle land":
        filtered_df = df[df['Land'] == selected_country]
    else:
        filtered_df = df

# Producer filter
unique_producers = sorted(filtered_df['Produsent'].dropna().astype(str).unique())
producers = ["Alle produsenter"] + unique_producers
with col2:
    selected_producer = st.selectbox("", options=producers)
    if selected_producer != "Alle produsenter":
        filtered_df = filtered_df[filtered_df['Produsent'] == selected_producer]

# Alcohol content filter
abv_series = filtered_df['%'].dropna()
min_abv = float(abv_series.min())
max_abv = float(abv_series.max())
if (min_abv == max_abv):
    max_abv = min_abv + 0.1

with col2:
    abv_range = st.slider(
        "Alkohol %",
        min_value=min_abv,
        max_value=max_abv,
        value=(min_abv, max_abv),
        step=0.1
    )
    filtered_df = filtered_df[(df['%'] >= abv_range[0]) & (filtered_df['%'] <= abv_range[1])]

# Search functionality
with col1:
    search_term = st.text_input("Søk på ølnavn:")
if search_term:
    filtered_df = filtered_df[filtered_df['Navn'].str.contains(search_term, case=False, na=False)]

# Display results
st.write(len(filtered_df), " øl:")
st.dataframe(
    filtered_df[["Navn", "%", "Snitt pr deltager", "Produsent", "Land"]],
    use_container_width=True,
    hide_index=True,
    height=800
)

# Display the illustration
st.image(illustrationimage) 