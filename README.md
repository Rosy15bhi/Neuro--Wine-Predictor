# NEURO – Valutatore di etichette di vino

Prototipo (proof of concept) che, data la **foto di un'etichetta di vino**,
valuta automaticamente **6 caratteristiche estetiche** e calcola un **indice neuro**
(media ponderata), restituendo punteggi e giudizio.

Il sistema usa un **modello multimodale (API Anthropic / Claude)** che osserva
l'immagine e applica una rubrica di valutazione derivata da un catalogo di 340
bottiglie valutate da esperto.

---

## Come funziona (architettura)

```
   Foto etichetta
        │
        ▼
 ┌──────────────┐   rubrica.md      ┌───────────────────────────┐
 │  vision.py   │ ───────────────►  │  API Anthropic (Claude)   │
 │ (multimodale)│ ◄───────────────  │  6 punteggi 0-10 + motiv. │
 └──────────────┘                   └───────────────────────────┘
        │  punteggi (JSON)
        ▼
 ┌──────────────┐
 │  scoring.py  │  media ponderata (pesi fissi) → indice neuro + giudizio
 └──────────────┘
        │
        ▼
 ┌──────────────┐
 │   app.py     │  front-end Streamlit: upload foto + risultati
 └──────────────┘
```

Due moduli distinti e indipendenti:

- **Parte appresa/predittiva** (`vision.py`): il modello multimodale "guarda"
  l'etichetta e assegna i 6 voti seguendo la rubrica, come farebbe un esperto.
- **Parte deterministica** (`scoring.py`): applica i pesi e calcola l'indice
  neuro. È sempre verificabile e riproducibile.

I **pesi dell'indice** sono stati ricavati per regressione lineare sull'indice
neuro del catalogo originale (R² = 0,94, errore medio 0,10 su scala 0–10):

| Caratteristica | Peso |
|---|---|
| Visibilità | 30,0% |
| Completezza | 17,5% |
| Attrattività per giovani | 16,0% |
| Coerenza | 14,5% |
| Design | 12,0% |
| Eleganza | 10,0% |

---

## Struttura del progetto

```
NEURO PROGETTO/
├── README.md               # questo file
├── requirements.txt        # dipendenze Python
├── .env.example            # modello per la chiave API
├── validate.py             # confronto modello vs voti esperto
├── data/
│   ├── catalogo_pulito.xlsx # catalogo ripulito + indice ricalcolato
│   └── rubrica.md           # rubrica dei 6 criteri (usata nel prompt)
└── src/
    ├── config.py            # pesi, modello, soglie di giudizio
    ├── clean_dataset.py     # script di pulizia del catalogo originale
    ├── scoring.py           # calcolo indice neuro + giudizio
    ├── vision.py            # chiamata all'API Anthropic
    └── app.py               # front-end Streamlit
```

---

## Installazione ed esecuzione

### 1. Requisiti
- Python 3.10 o superiore
- Una chiave API Anthropic (https://console.anthropic.com/settings/keys)

### 2. Installa le dipendenze

```bash
cd "NEURO PROGETTO"
python -m venv venv
source venv/bin/activate        # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configura la chiave API

```bash
cp .env.example .env
```

Apri `.env` e inserisci la tua chiave:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Avvia l'interfaccia

```bash
streamlit run src/app.py
```

Si apre il browser: carica la foto di un'etichetta (idealmente su sfondo
bianco) e premi **Analizza etichetta**.

### Uso da riga di comando (senza interfaccia)

```bash
python src/vision.py percorso/della/foto.jpg
```

---

## Validazione (prova di fattibilità)

Per misurare quanto i voti del modello si avvicinano a quelli dell'esperto:

```bash
python validate.py --immagini ./immagini --n 20
```

> **Nota:** il catalogo contiene solo i *codici* delle foto (colonne
> `ref_foto_fronte` / `ref_foto_retro`), non le immagini. Per eseguire la
> validazione serve una cartella `immagini/` con file nominati come quei codici
> (es. `3177.jpg`). Lo script stampa l'errore medio assoluto (MAE) sull'indice
> e sulle singole caratteristiche.

---

## Limiti del prototipo

- **Soggettività**: la valutazione estetica è intrinsecamente soggettiva; la
  rubrica riduce ma non elimina la variabilità.
- **Dataset di riferimento piccolo** (340 bottiglie) e con ~37% di foto mancanti.
- **Categoria `tipo`** ricondotta a macro-categorie tramite dizionario di vitigni;
  39 voci restano "Non specificato" (denominazioni generiche senza vitigno/colore).
- **Dipendenza da API esterna** (costo per chiamata, latenza, connessione).
- L'indice neuro originale non è perfettamente lineare (R² = 0,94): i pesi sono
  un'approssimazione fedele ma non esatta della formula usata dall'esperto.

## Possibili sviluppi futuri

- Riconoscimento automatico della bottiglia (OCR/match) per collegare la foto al
  catalogo e confrontare il voto predetto con quello esistente.
- Fine-tuning o few-shot con esempi del catalogo per aumentare la coerenza.
- Raccolta di immagini mancanti e ampliamento del dataset.
- Esportazione dei risultati (PDF/Excel) e storicizzazione delle valutazioni.
