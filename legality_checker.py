import requests
import time
import concurrent.futures
from threading import Lock

print_lock = Lock()

def controlla_carta(nome_carta, formato):
    for _ in range(3):  # 3 tentativi
        try:
            response = requests.get(
                "https://api.scryfall.com/cards/named",
                params={'exact': nome_carta},
                timeout=15
            )
            if response.status_code == 200:
                legalities = response.json().get('legalities', {})
                return legalities.get(formato, 'not_legal') == 'legal', None
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            time.sleep(1)
        except Exception as e:
            return False, str(e)
    return False, "Timeout"

def worker(args):
    nome_carta, quantita, indice, totale, formato = args
    with print_lock:
        print(f"Controllo {indice}/{totale}: {nome_carta} in {formato}")
    is_legal, errore = controlla_carta(nome_carta, formato)
    if errore:
        with print_lock:
            print(f"  ⚠️ Errore per {nome_carta}: {errore}")
    return nome_carta, {'quantita': quantita, f'{formato}_legal': is_legal, 'errore': errore}

def controlla_mazzo(mazzo, formato):
    print(f"Controllo legalità {formato} per {len(mazzo)} carte uniche...")
    print(f"Carte totali nel mazzo: {sum(mazzo.values())}")
    print(f"(Controllo in parallelo con max 5 thread)\n")
    
    tasks = [(nome, qty, i, len(mazzo), formato) for i, (nome, qty) in enumerate(mazzo.items(), 1)]
    risultati, carte_illegali, carte_con_errori = {}, [], []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(worker, task): task[0] for task in tasks}
        
        for future in concurrent.futures.as_completed(futures):
            nome_carta, risultato = future.result()
            risultati[nome_carta] = risultato
            
            if risultato['errore']:
                carte_con_errori.append(nome_carta)
            elif not risultato[f'{formato}_legal']:
                carte_illegali.append(nome_carta)
        
        executor.shutdown(wait=True)
    
    return risultati, carte_illegali, carte_con_errori

