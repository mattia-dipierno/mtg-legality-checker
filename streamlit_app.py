import streamlit as st
import re
import pandas as pd
from collections import defaultdict
from goldfish import estrai_mazzo  # Modificato per restituire main_deck, sideboard
from legality_checker import controlla_mazzo

FORMATS = {
    "Timeless": "timeless",
    "Historic": "historic",
    "Legacy": "legacy",
}

# Inizializza cronologia
if "cronologia" not in st.session_state:
    st.session_state.cronologia = []

st.title("MTG Goldfish / Arena Deck Legality Checker")

tab1, tab2 = st.tabs(["🌐 Link da Goldfish", "📄 Incolla mazzo MTG Arena"])

with tab1:
    url = st.text_input("Inserisci il link del mazzo Goldfish (paper)")

with tab2:
    mazzo_txt = st.text_area("Incolla qui il tuo mazzo esportato da MTG Arena")

formato = st.selectbox("Scegli il formato per il controllo", list(FORMATS.keys()))

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
    # Filtra solo carte legali e senza errori (mantieni quantità originali)
    def filtra(diz):
        return {
            c: q for c, q in diz.items()
            if c in risultati and c not in carte_illegali and c not in carte_con_errori
        }
    main_legale = filtra(main_deck)
    side_legale = filtra(sideboard)

    lines = []
    # Deck main
    lines.append("Deck")
    for c, q in main_legale.items():
        lines.append(f"{q} {c}")
    # Sideboard se presente
    if side_legale:
        lines.append("")
        lines.append("Sideboard")
        for c, q in side_legale.items():
            lines.append(f"{q} {c}")
    return "\n".join(lines)

if st.button("Controlla legalità"):
    if not url and not mazzo_txt.strip():
        st.error("Per favore inserisci un link valido o incolla un mazzo.")
    else:
        # Estrazione mazzo
        if mazzo_txt.strip():
            main_deck, sideboard = parse_arena_deck(mazzo_txt)
        else:
            st.info(f"Estrazione del mazzo da: {url} ...")
            main_deck, sideboard = estrai_mazzo(url)

        # Unisci main + side per controllo legalità (controlla_mazzo si aspetta un singolo dict)
        mazzo_unito = main_deck.copy()
        for c, q in sideboard.items():
            mazzo_unito[c] = mazzo_unito.get(c, 0) + q

        if not mazzo_unito:
            st.error("Non è stato possibile estrarre o leggere il mazzo. Controlla l'input.")
        else:
            st.success(f"Mazzo caricato con {sum(mazzo_unito.values())} carte totali.")

            st.session_state.cronologia.append((url or "Mazzo incollato", formato))

            risultati, carte_illegali, carte_con_errori = controlla_mazzo(mazzo_unito, FORMATS[formato])

            st.subheader(f"Risultati legalità in {formato}")
            st.write(f"Carte uniche controllate: {len(risultati)}")
            st.write(f"Carte totali: {sum(mazzo_unito.values())}")
            st.write(f"Carte illegali: {len(carte_illegali)}")
            st.write(f"Carte con errori: {len(carte_con_errori)}")

            if carte_illegali:
                st.error("Carte illegali:")
                for c in carte_illegali:
                    st.write(f"{risultati[c]['quantita']}x {c}")

            if carte_con_errori:
                st.warning("Carte con errori (da ricontrollare):")
                for c in carte_con_errori:
                    st.write(f"{risultati[c]['quantita']}x {c} - {risultati[c]['errore']}")

            if not carte_illegali and not carte_con_errori:
                st.success(f"Tutte le carte sono legali in {formato}!")

            # Pulsante per esportare decklist pulita SOLO per formati Arena
            if formato in ["Timeless", "Historic"]:
                decklist_pulita = crea_decklist_pulita(risultati, carte_illegali, carte_con_errori, main_deck, sideboard)

                st.subheader("📥 Decklist legale per Arena")
                st.text_area("Decklist esportabile", decklist_pulita, height=200, key="decklist_area")

# Cronologia sessione
if st.session_state.cronologia:
    st.subheader("🕒 Cronologia verifiche recenti")
    for i, (link, fmt) in enumerate(reversed(st.session_state.cronologia[-5:]), 1):
        st.write(f"{i}. [{fmt}] {link}")
