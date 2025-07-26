import streamlit as st
import pandas as pd
from goldfish import estrai_mazzo
from legality_checker import controlla_mazzo
from collections import defaultdict
import re

# Formati disponibili
FORMATS = {
    "Timeless": "timeless",
    "Historic": "historic",
    "Legacy": "legacy",
}

# Inizializza cronologia
if "cronologia" not in st.session_state:
    st.session_state.cronologia = []

st.title("MTG Goldfish / Arena Deck Legality Checker")

# Tabs per scegliere input
tab1, tab2 = st.tabs(["🌐 Link da Goldfish", "📄 Incolla mazzo MTG Arena"])

with tab1:
    url = st.text_input("Inserisci il link del mazzo Goldfish (paper)")

with tab2:
    mazzo_txt = st.text_area("Incolla qui il tuo mazzo esportato da MTG Arena")

# Selezione formato
formato = st.selectbox("Scegli il formato per il controllo", list(FORMATS.keys()))

# Bottone per eseguire
if st.button("Controlla legalità"):
    if not url and not mazzo_txt.strip():
        st.error("Per favore inserisci un link valido o incolla un mazzo.")
    else:
        # Parsing da testo incollato oppure da Goldfish
        if mazzo_txt.strip():
            mazzo = defaultdict(int)
            for riga in mazzo_txt.strip().splitlines():
                match = re.match(r"(\d+)x?\s+(.+)", riga.strip())
                if match:
                    qty, nome = match.groups()
                    mazzo[nome.strip()] += int(qty)
        else:
            st.info(f"Estrazione del mazzo da: {url} ...")
            mazzo = estrai_mazzo(url)

        # Se il mazzo è vuoto
        if not mazzo:
            st.error("Non è stato possibile estrarre o leggere il mazzo. Controlla l'input.")
        else:
            st.success(f"Mazzo caricato con {sum(mazzo.values())} carte totali.")

            # Salva nella cronologia
            st.session_state.cronologia.append((url or "Mazzo incollato", formato))

            # Controllo legalità
            risultati, carte_illegali, carte_con_errori = controlla_mazzo(mazzo, FORMATS[formato])

            # Output
            st.subheader(f"Risultati legalità in {formato}")
            st.write(f"Carte uniche controllate: {len(risultati)}")
            st.write(f"Carte totali: {sum(mazzo.values())}")
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

            # Report scaricabile
            df = pd.DataFrame([
                {"Carta": c, "Quantità": risultati[c]["quantita"], "Stato": "Illegale"}
                for c in carte_illegali
            ] + [
                {"Carta": c, "Quantità": risultati[c]["quantita"], "Stato": "Errore", "Errore": risultati[c]["errore"]}
                for c in carte_con_errori
            ])
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button("📥 Scarica report CSV", csv, "report_legality.csv", "text/csv")

# Cronologia sessione
if st.session_state.cronologia:
    st.subheader("🕒 Cronologia verifiche recenti")
    for i, (link, fmt) in enumerate(reversed(st.session_state.cronologia[-5:]), 1):
        st.write(f"{i}. [{fmt}] {link}")
