"""
Modulo di scoring: calcola l'indice neuro come media ponderata delle 6
caratteristiche e restituisce un giudizio sintetico.

Questa è la parte DETERMINISTICA del sistema: dati i 6 punteggi (che provengano
dall'esperto o dal modello multimodale), il calcolo è sempre lo stesso e
verificabile. È il "motore" che traduce le valutazioni in un punteggio unico.
"""

from config import WEIGHTS, FEATURES, JUDGMENT_THRESHOLDS


def compute_index(scores: dict) -> float:
    """
    Calcola l'indice neuro (media ponderata) a partire da un dizionario di
    punteggi {nome_caratteristica: valore 0-10}.

    Solleva ValueError se manca una caratteristica o un valore è fuori scala.
    """
    total = 0.0
    for feat in FEATURES:
        if feat not in scores:
            raise ValueError(f"Caratteristica mancante: {feat}")
        v = scores[feat]
        if not isinstance(v, (int, float)) or not (0 <= v <= 10):
            raise ValueError(f"Valore non valido per {feat}: {v!r} (atteso 0-10)")
        total += v * WEIGHTS[feat]
    return round(total, 2)


def judgment(index: float) -> str:
    """Restituisce il giudizio sintetico testuale per un dato indice."""
    for soglia, etichetta in JUDGMENT_THRESHOLDS:
        if index >= soglia:
            return etichetta
    return "Da migliorare"


if __name__ == "__main__":
    # Esempio d'uso / verifica rapida
    esempio = {
        "eleganza": 10, "completezza": 10, "visibilita": 10,
        "coerenza": 10, "design": 10, "attrattivita_giovani": 9,
    }
    idx = compute_index(esempio)
    print(f"Indice neuro: {idx} -> {judgment(idx)}")
