import streamlit as st
import re
import pandas as pd
from collections import defaultdict
from goldfish import estrai_mazzo 
from legality_checker import controlla_mazzo

FORMATS = {
    "Timeless": "timeless",
    "Historic": "historic",
    "Legacy": "legacy",
}

# Initialize history
if "cronologia" not in st.session_state:
    st.session_state.cronologia = []

st.title("Arena Deck Legality Checker")

tab1, tab2 = st.tabs(["🌐 Goldfish Link", "📄 Paste MTG Arena Deck"])

with tab1:
    url = st.text_input("Enter the Goldfish deck link")

with tab2:
    mazzo_txt = st.text_area("Paste your MTG Arena exported deck here")

formato = st.selectbox("Choose the format to check", list(FORMATS.keys()))

def parse_arena_deck(text):
    main_deck = defaultdict(int)
    sideboard = defaultdict(int)
    current_section = main_deck
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower() == "sideboard":
            current_section = sideboard
            continue
        match = re.match(r"(\d+)x?\s+(.+)", line)
        if match:
            qty = int(match.group(1))
            name = match.group(2).strip()
            current_section[name] += qty
    return dict(main_deck), dict(sideboard)

def crea_decklist_pulita(risultati, carte_illegali, carte_con_errori, main_deck, sideboard):
    # Filter only legal cards without errors (keep original quantities)
    def filtra(diz):
        return {
            c: q for c, q in diz.items()
            if c in risultati and c not in carte_illegali and c not in carte_con_errori
        }
    main_legale = filtra(main_deck)
    side_legale = filtra(sideboard)

    lines = []
    # Main deck
    lines.append("Deck")
    for c, q in main_legale.items():
        lines.append(f"{q} {c}")
    # Sideboard if present
    if side_legale:
        lines.append("")
        lines.append("Sideboard")
        for c, q in side_legale.items():
            lines.append(f"{q} {c}")
    return "\n".join(lines)

if st.button("Check legality"):
    if not url and not mazzo_txt.strip():
        st.error("Please enter a valid link or paste a deck.")
    else:
        # Deck extraction
        if mazzo_txt.strip():
            main_deck, sideboard = parse_arena_deck(mazzo_txt)
        else:
            st.info(f"Extracting deck from: {url} ...")
            main_deck, sideboard = estrai_mazzo(url)

        # Combine main + side for legality check (controlla_mazzo expects a single dict)
        mazzo_unito = main_deck.copy()
        for c, q in sideboard.items():
            mazzo_unito[c] = mazzo_unito.get(c, 0) + q

        if not mazzo_unito:
            st.error("Could not extract or read the deck. Please check the input.")
        else:
            st.success(f"Deck loaded with {sum(mazzo_unito.values())} total cards.")

            st.session_state.cronologia.append((url or "Pasted deck", formato))

            risultati, carte_illegali, carte_con_errori = controlla_mazzo(mazzo_unito, FORMATS[formato])

            st.subheader(f"Legality results in {formato}")
            st.write(f"Unique cards checked: {len(risultati)}")
            st.write(f"Total cards: {sum(mazzo_unito.values())}")
            st.write(f"Illegal cards: {len(carte_illegali)}")
            st.write(f"Cards with errors: {len(carte_con_errori)}")

            if carte_illegali:
                st.error("Illegal cards:")
                for c in carte_illegali:
                    st.write(f"{risultati[c]['quantita']}x {c}")

            if carte_con_errori:
                st.warning("Cards with errors (please double-check):")
                for c in carte_con_errori:
                    st.write(f"{risultati[c]['quantita']}x {c} - {risultati[c]['errore']}")

            if not carte_illegali and not carte_con_errori:
                st.success(f"All cards are legal in {formato}!")

            # Export clean decklist button ONLY for Arena formats
            if formato in ["Timeless", "Historic"]:
                decklist_pulita = crea_decklist_pulita(risultati, carte_illegali, carte_con_errori, main_deck, sideboard)

                st.subheader("📥 Legal decklist for Arena")
                st.text_area("Exportable decklist", decklist_pulita, height=200, key="decklist_area")

# Session history
if st.session_state.cronologia:
    st.subheader("🕒 Recent checks history")
    for i, (link, fmt) in enumerate(reversed(st.session_state.cronologia[-5:]), 1):
        st.write(f"{i}. [{fmt}] {link}")
