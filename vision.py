"""
Modulo vision: invia la foto di un'etichetta all'API Anthropic (modello
multimodale) insieme alla rubrica, e ottiene i 6 punteggi (0-10) con una
breve motivazione per ciascuno, in formato JSON strutturato.

Questa è la parte "appresa/predittiva" del sistema: il modello osserva
l'immagine e applica la rubrica, esattamente come farebbe un esperto.
"""

import base64
import json
import os
from pathlib import Path

from anthropic import Anthropic

from config import MODEL_NAME, FEATURES, FEATURE_LABELS

# Percorso della rubrica (cartella data/ accanto a src/)
RUBRIC_PATH = Path(__file__).resolve().parent.parent / "data" / "rubrica.md"

# Tipi MIME supportati per le immagini
MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif",
}


def _load_rubric() -> str:
    return RUBRIC_PATH.read_text(encoding="utf-8")


def _build_prompt() -> str:
    rubric = _load_rubric()
    feats_json = ", ".join(f'"{f}"' for f in FEATURES)
    return f"""Sei un esperto di neuromarketing e packaging design del vino.
Valuta l'etichetta mostrata nella foto seguendo SCRUPOLOSAMENTE la rubrica qui sotto.

{rubric}

ISTRUZIONI:
- Prima di tutto, stabilisci se la foto mostra il FRONTE dell'etichetta (lato principale,
  con nome del vino, marchio, elemento grafico) oppure il RETRO (lato posteriore, con testo
  descrittivo, informazioni legali, allergeni, codice a barre, dati nutrizionali). Indicalo
  nel campo "lato" con valore "fronte" o "retro". Se è ambiguo, usa "fronte".
- Assegna a ciascuna delle 6 caratteristiche un punteggio intero o con un decimale, da 0 a 10.
- Per ogni caratteristica scrivi una motivazione di UNA frase basata su ciò che vedi.
- Per ogni caratteristica scrivi anche un CONSIGLIO pratico e concreto (una frase) su
  cosa cambierebbe nell'etichetta per avvicinarla al punteggio massimo (10). Il consiglio
  deve essere specifico per QUESTA etichetta; se la caratteristica è già a 10, indica come
  mantenerla.
- Aggiungi un campo "descrizione_generale" di una o due frasi.
- Rispondi ESCLUSIVAMENTE con un oggetto JSON valido, senza testo prima o dopo,
  con questa struttura esatta:

{{
  "lato": "fronte" oppure "retro",
  "punteggi": {{ {feats_json} }},
  "motivazioni": {{ {feats_json} }},
  "suggerimenti": {{ {feats_json} }},
  "descrizione_generale": "..."
}}

I valori in "punteggi" sono numeri 0-10. I valori in "motivazioni" e "suggerimenti" sono stringhe.

REGOLE DI FORMATO (IMPORTANTI per ottenere JSON valido):
- Usa SEMPRE il punto come separatore decimale (es. 7.5, mai 7,5).
- Ogni motivazione e ogni suggerimento devono essere brevi (massimo ~20 parole) e su una sola riga.
- Non inserire virgolette doppie all'interno delle stringhe e non andare a capo dentro le stringhe.
- Assicurati che il JSON sia completo e valido."""


def _encode_image(image_path: str):
    p = Path(image_path)
    media_type = MIME.get(p.suffix.lower())
    if media_type is None:
        raise ValueError(f"Formato immagine non supportato: {p.suffix}")
    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return media_type, data


def score_label(image_path: str, client: Anthropic | None = None) -> dict:
    """
    Valuta l'etichetta nell'immagine indicata e restituisce un dizionario:
    {
      "punteggi": {feature: float, ...},
      "motivazioni": {feature: str, ...},
      "suggerimenti": {feature: str, ...},
      "descrizione_generale": str
    }
    Richiede la variabile d'ambiente ANTHROPIC_API_KEY (o un client passato).
    """
    if client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY non impostata. Crea un file .env (vedi .env.example)."
            )
        client = Anthropic(api_key=api_key)

    media_type, data = _encode_image(image_path)

    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": _build_prompt()},
            ],
        }],
    )

    raw = message.content[0].text.strip()
    # Robustezza: estrai il blocco JSON anche se il modello aggiunge testo.
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Risposta non in formato JSON:\n{raw}")
    blob = raw[start:end + 1]
    try:
        result = json.loads(blob)
    except json.JSONDecodeError:
        # Riparazione tipica: decimali all'italiana ("7,5" -> "7.5") nei numeri.
        import re
        repaired = re.sub(r"(:\s*\d+),(\d+)", r"\1.\2", blob)
        result = json.loads(repaired)

    # Validazione minima
    for feat in FEATURES:
        if feat not in result.get("punteggi", {}):
            raise ValueError(f"Punteggio mancante nella risposta: {feat}")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python vision.py <percorso_immagine>")
        sys.exit(1)
    out = score_label(sys.argv[1])
    print(json.dumps(out, ensure_ascii=False, indent=2))
