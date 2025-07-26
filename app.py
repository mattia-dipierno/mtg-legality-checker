import streamlit as st
from goldfish import estrai_mazzo
from legality_checker import controlla_mazzo

FORMATS = {
    "Timeless": "timeless",
    "Historic": "historic",
    "Legacy": "legacy",
}

st.title("MTG Goldfish Deck Legality Checker")

url = st.text_input("Inserisci il link del mazzo Goldfish (paper)")

formato = st.selectbox("Scegli il formato per il controllo", list(FORMATS.keys()))

if st.button("Controlla legalità"):
    if not url:
        st.error("Per favore inserisci un link valido.")
    else:
        st.info(f"Estrazione del mazzo da: {url} ...")
        mazzo = estrai_mazzo(url)
        if not mazzo:
            st.error("Non è stato possibile estrarre il mazzo. Controlla il link.")
        else:
            st.success(f"Mazzo estratto con {sum(mazzo.values())} carte totali.")
            
            # Passa il formato scelto (esempio: 'timeless') al controllo
            risultati, carte_illegali, carte_con_errori = controlla_mazzo(mazzo, FORMATS[formato])
            
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
