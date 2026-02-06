import sqlite3
from datetime import datetime

DB_NAME = "spese.db"


# DB UTILS
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Crea le tabelle se non esistono.
    Fix inclusi:
    - data/mese validati con LIKE (corretto per wildcard '_')
    - categorie uniche case-insensitive tramite UNIQUE INDEX su lower(trim(nome))
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS categorie (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL CHECK (length(trim(nome)) > 0)
    );

    -- Unicità case-insensitive per nome categoria
    CREATE UNIQUE INDEX IF NOT EXISTS ux_categorie_nome_nocase
    ON categorie (lower(trim(nome)));

    CREATE TABLE IF NOT EXISTS spese (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL CHECK (data LIKE '____-__-__'),
        importo REAL NOT NULL CHECK (importo > 0),
        categoria_id INTEGER NOT NULL,
        descrizione TEXT,
        FOREIGN KEY (categoria_id) REFERENCES categorie(id)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    );

    CREATE TABLE IF NOT EXISTS budget_mensile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mese TEXT NOT NULL CHECK (mese LIKE '____-__'),
        categoria_id INTEGER NOT NULL,
        importo REAL NOT NULL CHECK (importo > 0),
        UNIQUE (mese, categoria_id),
        FOREIGN KEY (categoria_id) REFERENCES categorie(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
    );
    """
    conn = get_connection()
    conn.executescript(ddl)
    conn.commit()
    conn.close()


#VALIDAZIONI
def valida_data_yyyy_mm_dd(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def valida_mese_yyyy_mm(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m")
        return True
    except ValueError:
        return False


def leggi_float(prompt: str) -> float | None:
    raw = input(prompt).strip().replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def get_categoria_id(nome_categoria: str) -> int | None:
    """
    Ricerca categoria in modo case-insensitive.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM categorie WHERE lower(trim(nome)) = lower(trim(?))",
        (nome_categoria,),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


#CATEGORIE
def gestione_categorie():
    nome = input("Inserisci nome categoria: ").strip()

    if nome == "":
        print("Errore: nome categoria vuoto.")
        return

    conn = get_connection()
    cur = conn.cursor()

    # Controllo esistenza case-insensitive
    cur.execute(
        "SELECT 1 FROM categorie WHERE lower(trim(nome)) = lower(trim(?))",
        (nome,),
    )
    if cur.fetchone():
        print("Errore: la categoria esiste già.")
        conn.close()
        return

    try:
        cur.execute("INSERT INTO categorie (nome) VALUES (?)", (nome,))
        conn.commit()
        print("Categoria inserita correttamente.")
    except sqlite3.IntegrityError as e:
        print(f"Errore DB: {e}")
    finally:
        conn.close()


# INSERIMENTO SPESA 
def inserisci_spesa():
    data = input("Inserisci data (YYYY-MM-DD): ").strip()
    if not valida_data_yyyy_mm_dd(data):
        print("Errore: formato data non valido. Usa YYYY-MM-DD.")
        return

    importo = leggi_float("Inserisci importo: ")
    if importo is None:
        print("Errore: importo non valido.")
        return
    if importo <= 0:
        print("Errore: l’importo deve essere maggiore di zero.")
        return

    categoria = input("Inserisci nome categoria: ").strip()
    categoria_id = get_categoria_id(categoria)
    if categoria_id is None:
        print("Errore: la categoria non esiste.")
        return

    descrizione = input("Descrizione (facoltativa): ").strip()
    descrizione = descrizione if descrizione != "" else None

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO spese (data, importo, categoria_id, descrizione) VALUES (?, ?, ?, ?)",
            (data, importo, categoria_id, descrizione),
        )
        conn.commit()
        print("Spesa inserita correttamente.")
    except sqlite3.IntegrityError as e:
        print(f"Errore DB: {e}")
    finally:
        conn.close()


#BUDGET MENSILE 
def definisci_budget_mensile():
    mese = input("Inserisci mese (YYYY-MM): ").strip()
    if not valida_mese_yyyy_mm(mese):
        print("Errore: formato mese non valido. Usa YYYY-MM.")
        return

    categoria = input("Inserisci nome categoria: ").strip()
    categoria_id = get_categoria_id(categoria)
    if categoria_id is None:
        print("Errore: la categoria non esiste.")
        return

    importo = leggi_float("Inserisci importo budget: ")
    if importo is None:
        print("Errore: importo non valido.")
        return
    if importo <= 0:
        print("Errore: il budget deve essere maggiore di zero.")
        return

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO budget_mensile (mese, categoria_id, importo)
            VALUES (?, ?, ?)
            ON CONFLICT(mese, categoria_id) DO UPDATE SET importo = excluded.importo
            """,
            (mese, categoria_id, importo),
        )
        conn.commit()
        print("Budget mensile salvato correttamente.")
    except sqlite3.IntegrityError as e:
        print(f"Errore DB: {e}")
    finally:
        conn.close()


#REPORT SPSE
def report_totale_spese_per_categoria():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.nome, ROUND(COALESCE(SUM(s.importo), 0), 2) AS totale
        FROM categorie c
        LEFT JOIN spese s ON s.categoria_id = c.id
        GROUP BY c.id, c.nome
        ORDER BY totale DESC, c.nome ASC
        """
    )
    rows = cur.fetchall()
    conn.close()

    print("\nCategoria.................Totale Speso")
    for nome, totale in rows:
        print(f"{nome:<25} {totale:>10.2f}")
    print("")


def report_spese_mensili_vs_budget():
    mese = input("Inserisci mese da analizzare (YYYY-MM): ").strip()
    if not valida_mese_yyyy_mm(mese):
        print("Errore: formato mese non valido. Usa YYYY-MM.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            c.nome AS categoria,
            ROUND(COALESCE(b.importo, 0), 2) AS budget,
            ROUND(COALESCE(SUM(s.importo), 0), 2) AS speso
        FROM categorie c
        LEFT JOIN budget_mensile b
            ON b.categoria_id = c.id AND b.mese = ?
        LEFT JOIN spese s
            ON s.categoria_id = c.id AND substr(s.data, 1, 7) = ?
        GROUP BY c.id, c.nome, b.importo
        ORDER BY c.nome ASC
        """,
        (mese, mese),
    )
    rows = cur.fetchall()
    conn.close()

    print(f"\nMese: {mese}\n")
    for categoria, budget, speso in rows:
        if budget <= 0:
            stato = "NESSUN BUDGET IMPOSTATO"
        elif speso > budget:
            stato = "SUPERAMENTO BUDGET"
        else:
            stato = "OK"

        print(f"Categoria: {categoria}")
        print(f"Budget:    {budget:.2f}")
        print(f"Speso:     {speso:.2f}")
        print(f"Stato:     {stato}")
        print("-" * 30)
    print("")


def report_elenco_spese_ordinate():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.data, c.nome, s.importo, COALESCE(s.descrizione, '')
        FROM spese s
        JOIN categorie c ON c.id = s.categoria_id
        ORDER BY s.data ASC, s.id ASC
        """
    )
    rows = cur.fetchall()
    conn.close()

    print("\nData       Categoria           Importo   Descrizione")
    print("-" * 70)
    for data, cat, imp, desc in rows:
        print(f"{data:<10} {cat:<18} {imp:>8.2f}   {desc}")
    print("")


def menu_report():
    while True:
        print("\n--- MENU REPORT ---")
        print("1. Totale spese per categoria")
        print("2. Spese mensili vs budget")
        print("3. Elenco completo delle spese ordinate per data")
        print("4. Ritorna al menu principale")

        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            report_totale_spese_per_categoria()
        elif scelta == "2":
            report_spese_mensili_vs_budget()
        elif scelta == "3":
            report_elenco_spese_ordinate()
        elif scelta == "4":
            break
        else:
            print("Scelta non valida. Riprovare.")


#MAIN MENU
def main():
    init_db()
    print("Benvenuto nel Sistema di Gestione delle Spese Personali!\n")

    while True:
        print("-------------------------")
        print("SISTEMA SPESE PERSONALI")
        print("-------------------------")
        print("1. Gestione Categorie")
        print("2. Inserisci Spesa")
        print("3. Definisci Budget Mensile")
        print("4. Visualizza Report")
        print("5. Esci")
        print("-------------------------")

        scelta = input("Inserisci la tua scelta: ").strip()

        if scelta == "1":
            gestione_categorie()
        elif scelta == "2":
            inserisci_spesa()
        elif scelta == "3":
            definisci_budget_mensile()
        elif scelta == "4":
            menu_report()
        elif scelta == "5":
            print("Uscita dal programma. Arrivederci!")
            break
        else:
            print("Scelta non valida. Riprovare.")


if __name__ == "__main__":
    main()
