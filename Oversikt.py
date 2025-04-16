import streamlit as st
from PIL import Image

# Load the illustration image
illustrationimage = Image.open('beerpals.png')

# This configures your main app page
st.set_page_config(
    page_title="My App",  # Browser tab title
    page_icon="🏠",       # Browser tab icon
)


st.header("Lindås øldrikkar-app")
st.image(illustrationimage)

st.write("""
Her kan du:

- Se gjennom vår ølhistorikk og søke etter øl
- Bruke kameraet til å identifisere øl i butikken
- Se tidligere vurderinger av øl

Bruk menyen til venstre for å navigere mellom sidene.
""")

# Coming soon features
st.write("Coming soon:")
st.button("Samkjøre innkjøp")
st.button("Legg inn kveldens øl")
st.button("Les opp åpningsdikt")
st.button("Avgi poeng")
st.button("Justere poeng")
st.button("Planlegg øltur")
st.button("Planlegg whiskeytur")
st.button("Bestill hjemreise") 