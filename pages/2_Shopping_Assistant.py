import streamlit as st
import pandas as pd
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

# Load the CSV data into a DataFrame
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSoPr88VI9diu7isjOUtJwR1zIHQxn3Bdk0XsLKsbFXsOWbtYwdvaGkKLaFUMqOLDEORT3AdzOFTMCa/pub?gid=841858480&single=true&output=csv"
df = pd.read_csv(csv_url)

st.header("Innkjøpsassistent")

picture = st.camera_input("Ta bilde av etiketten 📷")

if picture:
    with st.spinner("Leser etikett..."):
        extracted_text = extract_text_from_image(picture)

    st.subheader("🔍 Tekst funnet på etiketten:")
    edited_text = st.text_input("Rediger eller bekreft teksten", value=extracted_text)
   
    if st.button("Søk etter noe som ligner ?"):
        beer_names = df["Navn"].dropna().tolist()  # Get the list of beer names from the DataFrame
        matches = find_best_beer_matches(edited_text, beer_names)
        match_names = matches
                  
        st.subheader("🔎 Beste treff i våre annaler:")
        for name, score, _ in match_names:
            st.write(f"✅ {name}  —  {score:.0f} % match")
            match_info = df[df["Navn"] == name]
            for _, row in match_info.iterrows():
                st.write(f"📅 Dato: {row['Dato']}  |  📍 Hos: {row['Arrangør']}  |  🏅 Plassering: {row['Plass']}")

