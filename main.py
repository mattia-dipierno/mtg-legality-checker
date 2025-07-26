from goldfish import estrai_mazzo
from legality_checker import controlla_mazzo

def scegli_formato():
    formati = {
        "1": "timeless",
        "2": "historic",
        "3": "legacy",
        "4": "modern",
        "5": "standard",
        "q": "quit",
        "Q": "quit"
    }

    while True:
        print("\nSeleziona un formato da controllare:")
        print("  1. Timeless")
        print("  2. Historic")
        print("  3. Legacy")
        print("  4. Modern")
        print("  5. Standard")
        print("  Q. Esci")

        scelta = input("Scelta: ").strip()

        if scelta in formati:
            if formati[scelta] == "quit":
                print("Programma terminato.")
                exit(0)
            return formati[scelta]
        else:
            print("❌ Scelta non valida. Riprova.")

def main():
    url = input("Inserisci il link del mazzo su MTGGoldfish: ").strip()
    formato = scegli_formato()

    mazzo = estrai_mazzo(url)

    if not mazzo:
        print("⚠️ Errore: impossibile estrarre il mazzo da Goldfish.")
        return

    print("\n=== MAZZO ESTRATTO ===")
    for carta, quantita in mazzo.items():
        print(f"{quantita}x {carta}")

    print(f"\nTotale carte: {sum(mazzo.values())}")
    print("\n" + "=" * 50)

    risultati, carte_illegali, carte_con_errori = controlla_mazzo(mazzo, formato=formato)

    print(f"\n=== RISULTATI LEGALITÀ {formato.upper()} ===")
    print(f"Carte uniche controllate: {len(risultati)}")
    print(f"Carte totali nel mazzo: {sum(mazzo.values())}")
    print(f"Carte illegali in {formato}: {len(carte_illegali)}")
    print(f"Carte con errori: {len(carte_con_errori)}")

    if carte_illegali:
        print(f"\n❌ CARTE ILLEGALI IN {formato.upper()}:")
        for carta in carte_illegali:
            print(f"  {risultati[carta]['quantita']}x {carta}")

    if carte_con_errori:
        print(f"\n⚠️ CARTE CON ERRORI (da ricontrollare):")
        for carta in carte_con_errori:
            print(f"  {risultati[carta]['quantita']}x {carta} - {risultati[carta]['errore']}")

    if not carte_illegali and not carte_con_errori:
        print(f"\n✅ Tutte le carte sono legali in {formato.capitalize()}!")

    legali = sum(1 for r in risultati.values() if r[f'{formato}_legal'] and not r['errore'])
    controllate = sum(1 for r in risultati.values() if not r['errore'])

    print(f"\nStatistiche:")
    print(f"  Carte controllate con successo: {controllate}/{len(risultati)}")
    if controllate > 0:
        print(f"  Carte legali: {legali}/{controllate}")
        print(f"  Percentuale legale: {legali / controllate * 100:.1f}%")

if __name__ == "__main__":
    main()
