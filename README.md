# Sistema di Gestione delle Spese Personali e del Budget

## Descrizione del Progetto
Il progetto consiste nello sviluppo di un Sistema di Gestione delle Spese Personali
basato su interfaccia testuale (console).  
L’applicazione è progettata per un singolo utente e consente di registrare le spese
giornaliere, organizzarle per categoria, definire budget mensili e visualizzare
report riepilogativi tramite interrogazioni SQL.

Il sistema è sviluppato in linguaggio Python e utilizza un database relazionale SQLite
per la persistenza dei dati.

---

## Requisiti per l’esecuzione

### Interprete necessario
- Python versione 3.10 o superiore

### Librerie utilizzate
- sqlite3 (libreria standard di Python)


---

## Istruzioni per l’esecuzione del programma

1. Aprire il terminale nella cartella contenente i file del progetto
2. Assicurarsi che il file `main.py` sia presente nella directory
3. Eseguire il seguente comando:

   python main.py

Al primo avvio del programma, il database SQLite viene creato automaticamente.

---

## Modalità di utilizzo
L’utente interagisce con il sistema tramite un menu testuale che consente di:
- gestire le categorie di spesa
- inserire nuove spese
- definire il budget mensile per categoria
- visualizzare report riepilogativi delle spese

Tutte le operazioni avvengono tramite console.
