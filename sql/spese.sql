PRAGMA foreign_keys = ON;

-- =========================
-- RESET TABELLE
-- =========================
DROP TABLE IF EXISTS spese;
DROP TABLE IF EXISTS budget_mensile;
DROP TABLE IF EXISTS categorie;

-- =========================
-- CREAZIONE TABELLE
-- =========================

CREATE TABLE categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0)
);

-- Unicità case-insensitive sul nome categoria
CREATE UNIQUE INDEX ux_categorie_nome_nocase
ON categorie (lower(trim(nome)));

CREATE TABLE spese (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL CHECK (data LIKE '____-__-__'),
    importo REAL NOT NULL CHECK (importo > 0),
    categoria_id INTEGER NOT NULL,
    descrizione TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categorie(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE budget_mensile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mese TEXT NOT NULL CHECK (mese LIKE '____-__'),
    categoria_id INTEGER NOT NULL,
    importo REAL NOT NULL CHECK (importo > 0),
    UNIQUE (mese, categoria_id),
    FOREIGN KEY (categoria_id) REFERENCES categorie(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- =========================
-- INSERT DATI DI ESEMPIO
-- =========================

INSERT INTO categorie (nome) VALUES
('Alimentari'),
('Trasporti'),
('Affitto'),
('Svago');

INSERT INTO budget_mensile (mese, categoria_id, importo)
SELECT '2026-02', id, 300.00 FROM categorie WHERE nome = 'Alimentari';

INSERT INTO budget_mensile (mese, categoria_id, importo)
SELECT '2026-02', id, 120.00 FROM categorie WHERE nome = 'Trasporti';

INSERT INTO budget_mensile (mese, categoria_id, importo)
SELECT '2026-02', id, 650.00 FROM categorie WHERE nome = 'Affitto';

INSERT INTO spese (data, importo, categoria_id, descrizione)
SELECT '2026-02-01', 25.00, id, 'Pranzo' FROM categorie WHERE nome = 'Alimentari';

INSERT INTO spese (data, importo, categoria_id, descrizione)
SELECT '2026-02-02', 15.50, id, 'Spesa supermercato' FROM categorie WHERE nome = 'Alimentari';

INSERT INTO spese (data, importo, categoria_id, descrizione)
SELECT '2026-02-02', 3.00, id, 'Metro' FROM categorie WHERE nome = 'Trasporti';

INSERT INTO spese (data, importo, categoria_id, descrizione)
SELECT '2026-02-01', 650.00, id, 'Canone mensile' FROM categorie WHERE nome = 'Affitto';

INSERT INTO spese (data, importo, categoria_id, descrizione)
SELECT '2026-02-03', 12.00, id, 'Cinema' FROM categorie WHERE nome = 'Svago';
