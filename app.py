import streamlit as st
import pandas as pd
import altair as alt
import requests
from PIL import Image
import io
import rapidfuzz
from rapidfuzz import fuzz, process

OCR_API_KEY = "K89559071588957"

def extract_text_from_image(uploaded_picture):
    url = 'https://api.ocr.space/parse/image'
    uploaded_image = Image.open(uploaded_picture).convert("RGB")
    # Convert image to JPEG in memory
    buffer = io.BytesIO()
    uploaded_image.save(buffer, format="JPEG")
    buffer.seek(0)

    response = requests.post(
        url,
        files={'filename':  ('beer.jpg', buffer, 'image/jpeg')},
        data={
            'apikey': OCR_API_KEY,
         #   'language':  'eng', 'deu', etc.
            'isOverlayRequired': False,
        }
    )

    result = response.json()
    if result.get("IsErroredOnProcessing"):
        st.error("❌ OCR failed")
        st.write("📦 Full response:", result)
        return "Klarer ikke lese noe tekst fra bildet. Skjerp deg!"

    parsed_text = result['ParsedResults'][0]['ParsedText']
    return parsed_text.strip()

def find_best_beer_matches(ocr_text, beer_names, limit=3):
    # Returns a list of (match, score) tuples
    matches = process.extract(ocr_text, beer_names, scorer=fuzz.token_sort_ratio, limit=limit)
    return matches


# Replace with your actual CSV export URL from Google Sheets
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSoPr88VI9diu7isjOUtJwR1zIHQxn3Bdk0XsLKsbFXsOWbtYwdvaGkKLaFUMqOLDEORT3AdzOFTMCa/pub?gid=841858480&single=true&output=csv"

# Load the CSV data into a DataFrame
df = pd.read_csv(csv_url)

# Ensure that the '%' column is treated the same in both df and filtered_df
df['%'] = df['%'].astype(str).str.replace(",", ".", regex=False).str.strip()
df['%'] = pd.to_numeric(df['%'], errors='coerce')  # Convert to float, non-convertibles become NaN

df['Snitt pr deltager'] = df['Snitt pr deltager'].astype(str).str.replace(",", ".", regex=False).str.strip()
df['Snitt pr deltager'] = pd.to_numeric(df['Snitt pr deltager'], errors='coerce').round(1)

#opening the image

illustrationimage = Image.open('beerpals.png')
#displaying the image on streamlit app

selected_beer = 'none'

st.title("Lindås øldrikkarlag app")

with st.expander("**Står du foran hylla?  Søk med kameraet her**"):
    picture = st.camera_input("Ta bilde av etiketten 📷")

    # If a picture is taken, display it
    if picture:
    
    #    st.image(picture, caption="Ditt bilde", use_container_width=True)

        with st.spinner("Leser etikett..."):
            extracted_text = extract_text_from_image(picture)

        st.subheader("🔍 Tekst funnet på etiketten:")
        edited_text = st.text_input("Rediger eller bekreft teksten", value=extracted_text)
       
        if st.button("Søk etter noe som ligner ?"):
            beer_names = df["Navn"].dropna().tolist()  # Get the list of beer names from the DataFrame
            matches = find_best_beer_matches(edited_text, beer_names)
            match_names = matches # [match[0] for match in matches if match[1] > 10]  # Filter weak matches
                      
            st.subheader("🔎 Beste treff i våre annaler:")
            for name, score, _ in match_names:
                st.write(f"✅ {name}  —  {score:.0f} % match")
                match_info = df[df["Navn"] == name]
                for _, row in match_info.iterrows():
                    st.write(f"📅 Dato: {row['Dato']}  |  📍 Hos: {row['Arrangør']}  |  🏅 Plassering: {row['Plass']}")
               
                      
 

col1, col2 = st.columns(2)



# Extract unique countries and create a list for the dropdown
# Include an "All Countries" option so users can opt-out of filtering
#unique_countries = sorted(df['Land'].unique())

unique_countries = sorted(df['Land'].dropna().astype(str).unique())
countries = ["Alle land"] + unique_countries
with col1:
    selected_country = st.selectbox("", options=countries)
    if selected_country != "Alle land":
        filtered_df = df[df['Land'] == selected_country]
    else:
        filtered_df = df


unique_producers = sorted(filtered_df['Produsent'].dropna().astype(str).unique())
producers = ["Alle produsenter"] + unique_producers
with col2:

    selected_producer = st.selectbox("", options=producers)

    if selected_producer != "Alle produsenter":
        filtered_df = filtered_df[filtered_df['Produsent'] == selected_producer]


# Alkololinnhold filter
# Convert ABV strings with comma to float
abv_series = filtered_df['%'].dropna()  # remove NaN before min/max

min_abv = float(abv_series.min())
max_abv = float(abv_series.max())
if (min_abv == max_abv):
    max_abv=min_abv+0.1

with col2:
    abv_range = st.slider(
        "Alkoholinnhold (% ABV)",
        min_value=min_abv,
        max_value=max_abv,
        value=(min_abv, max_abv),
        step=0.1
    )
    filtered_df = filtered_df[(df['%'] >= abv_range[0]) & (filtered_df['%'] <= abv_range[1])]

# Adding a simple search functionality
with col1:
    search_term = st.text_input("Søk på ølnavn:")

# Filter the DataFrame based on the search term
if search_term:
    # Assuming you want to search in a specific column named 'Name'
   filtered_df = filtered_df[filtered_df['Navn'].str.contains(search_term, case=False, na=False)]

st.write(len(filtered_df), " øl:")
st.dataframe ( 
    filtered_df[["Navn", "%","Snitt pr deltager","Produsent", "Land"]],
    use_container_width=True, hide_index=True
)
# First, sort the filtered DataFrame by score descending
chart_df = filtered_df.sort_values(by="Snitt pr deltager", ascending=False)

# Optional: Drop NaNs in case some scores are missing
chart_df = chart_df.dropna(subset=["Snitt pr deltager", "Navn"])

# Create a horizontal bar chart
bars = alt.Chart(chart_df).mark_bar(color="#336f77a4").encode(
    x=alt.X("Snitt pr deltager:Q", title="Snitt pr deltager"),
    y=alt.Y("Navn:N", sort="-x", title="Øl / Navn", axis=alt.Axis(labelLimit=250) ),
    tooltip=["Navn", "Snitt pr deltager"]
   # ,color=alt.Color("Poengsum:Q", scale=alt.Scale(scheme="blues"), legend=None),
).properties(
    width=600,
    title="Poengsnitt"
)
labels = alt.Chart(chart_df).mark_text(
    align="left",
    baseline="middle",
    dx=3  # moves text slightly to the right of the bar
).encode(
    x="Poengsnitt:Q",
    y=alt.Y("Navn:N", sort="-x"),
    text=alt.Text("Poengnitt:Q", format=".1f")  # format with one decimal
)

bar_chart = (bars + labels).properties(
    title="Rangering",
    width=600,
 #   height=500
)

# Tatt ut barchart - ga rare resultater for øl med flere entryer -
# st.altair_chart(bar_chart, use_container_width=True) # Display the chart in your Streamlit app
st.image(illustrationimage)


st.write("Coming soon:")
st.button("Samkjøre innkjøp")
st.button("Legg inn kveldens øl")
st.button("Les opp åpningsdikt")
st.button("Avgi poeng")
st.button("Avgi justere poeng")
st.button("Planlegg øltur")
st.button("Planlegg whiskeytur")
st.button("Bestill hjemreise")