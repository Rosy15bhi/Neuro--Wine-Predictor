"""
Configurazione centrale del prototipo NEURO.

Qui sono definiti i pesi dell'indice neuro, il modello multimodale usato
e le soglie di giudizio. Modificando questo file si modifica il comportamento
dell'intero sistema senza toccare la logica.
"""

# --- Modello multimodale (API Anthropic) ---
# Modello vision usato per valutare le foto delle etichette.
MODEL_NAME = "claude-opus-4-8"

# --- Le 6 caratteristiche valutate ---
# L'ordine qui definisce l'ordine usato ovunque nel sistema.
FEATURES = [
    "eleganza",
    "completezza",
    "visibilita",
    "coerenza",
    "design",
    "attrattivita_giovani",
]

# Etichette leggibili (per UI e report)
FEATURE_LABELS = {
    "eleganza": "Eleganza",
    "completezza": "Completezza",
    "visibilita": "Visibilità",
    "coerenza": "Coerenza",
    "design": "Design",
    "attrattivita_giovani": "Attrattività per giovani",
}

# --- Pesi dell'indice neuro ---
# Ricavati per regressione lineare (senza intercetta) sull'indice neuro
# del catalogo originale: R^2 = 0.94, errore medio assoluto = 0.10 su scala 0-10.
# Somma dei pesi = 1.0. La visibilità pesa il triplo dell'eleganza:
# coerente con un'ottica di neuromarketing (impatto a scaffale prioritario).
WEIGHTS = {
    "eleganza": 0.10,
    "completezza": 0.175,
    "visibilita": 0.30,
    "coerenza": 0.145,
    "design": 0.12,
    "attrattivita_giovani": 0.16,
}

# --- Soglie di giudizio sintetico (sull'indice neuro 0-10) ---
JUDGMENT_THRESHOLDS = [
    (9.0, "Eccellente"),
    (8.0, "Ottimo"),
    (7.0, "Buono"),
    (6.0, "Sufficiente"),
    (0.0, "Da migliorare"),
]
