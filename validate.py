"""
Script di validazione del prototipo.

Confronta i punteggi prodotti dal modello multimodale con i voti dell'esperto
presenti nel catalogo, per misurare la fattibilità tecnica dell'approccio
(errore medio assoluto sull'indice neuro e sulle singole caratteristiche).

COME FUNZIONA
-------------
Il catalogo contiene, nelle colonne `ref_foto_fronte` / `ref_foto_retro`, dei
codici numerici che identificano le foto delle etichette (le immagini NON sono
incluse nel file Excel). Per eseguire la validazione serve quindi una cartella
di immagini i cui nomi file corrispondano a quei codici, ad esempio:

    immagini/3177.jpg
    immagini/3081.jpg
    ...

USO
---
    python validate.py --immagini ./immagini --n 20

Con --n si limita il numero di bottiglie valutate (per contenere i costi API).
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from config import FEATURES, FEATURE_LABELS  # noqa: E402
from scoring import compute_index            # noqa: E402
from vision import score_label, MIME         # noqa: E402

CATALOG = Path(__file__).resolve().parent / "data" / "catalogo_pulito.xlsx"

# Colonne del catalogo che corrispondono alle 6 feature (stesso ordine di FEATURES)
CATALOG_FEATURE_COLS = {
    "eleganza": "eleganza",
    "completezza": "completezza",
    "visibilita": "visibilità",
    "coerenza": "coerenza",
    "design": "design",
    "attrattivita_giovani": "attrattività_giovani",
}


def find_image(folder: Path, ref) -> Path | None:
    if ref is None or pd.isna(ref):
        return None
    stem = str(int(ref))
    for ext in MIME:
        p = folder / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--immagini", required=True, help="Cartella con le foto (nome = codice ref)")
    ap.add_argument("--n", type=int, default=20, help="Numero massimo di bottiglie da valutare")
    args = ap.parse_args()

    load_dotenv()
    folder = Path(args.immagini)
    df = pd.read_excel(CATALOG)

    abs_err_index = []
    abs_err_feat = {f: [] for f in FEATURES}
    valutate = 0

    for _, row in df.iterrows():
        if valutate >= args.n:
            break
        img = find_image(folder, row.get("ref_foto_fronte"))
        if img is None:
            continue

        try:
            result = score_label(str(img))
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {img.name}: {e}")
            continue

        pred = {f: float(result["punteggi"][f]) for f in FEATURES}
        pred_index = compute_index(pred)
        true_index = float(row["indice_neuro_calc"])

        abs_err_index.append(abs(pred_index - true_index))
        for f in FEATURES:
            true_v = float(row[CATALOG_FEATURE_COLS[f]])
            abs_err_feat[f].append(abs(pred[f] - true_v))

        valutate += 1
        print(f"[{valutate}] {row['nome'][:45]:45s} "
              f"pred={pred_index:.2f}  esperto={true_index:.2f}  Δ={abs(pred_index-true_index):.2f}")

    if not abs_err_index:
        print("\nNessuna immagine trovata. Controlla la cartella e i nomi file (codice ref).")
        return

    n = len(abs_err_index)
    print(f"\n=== RISULTATI su {n} bottiglie ===")
    print(f"MAE indice neuro: {sum(abs_err_index)/n:.3f}")
    print("MAE per caratteristica:")
    for f in FEATURES:
        vals = abs_err_feat[f]
        print(f"  {FEATURE_LABELS[f]:26s}: {sum(vals)/len(vals):.3f}")


if __name__ == "__main__":
    main()
