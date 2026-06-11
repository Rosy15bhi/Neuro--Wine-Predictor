# Rubrica di valutazione delle etichette di vino

Ogni etichetta viene valutata su **6 caratteristiche**, ciascuna con un punteggio
da **0 a 10**. La rubrica è stata derivata dalle descrizioni testuali presenti nel
catalogo di riferimento (340 bottiglie valutate da esperto) ed è il criterio guida
che il modello multimodale deve seguire per garantire valutazioni coerenti.

Scala generale: **0–3** scarso/assente · **4–5** debole · **6–7** sufficiente/buono ·
**8–9** ottimo · **10** eccellente.

---

## 1. Eleganza
Raffinatezza estetica complessiva dell'etichetta: scelte cromatiche, equilibrio,
sobrietà, senso di lusso o pregio percepito.
- **Alto (8–10):** palette curata (es. oro/bianco/nero), materiali e finiture che
  comunicano pregio, composizione armoniosa e sobria.
- **Basso (0–4):** colori stridenti o casuali, aspetto dozzinale, composizione
  disordinata o sovraccarica.

## 2. Completezza
Presenza e disposizione delle informazioni (denominazione, annata, gradazione,
zona, produttore) in modo leggibile e ben organizzato, senza sovraccaricare.
- **Alto (8–10):** informazioni tecniche complete, gerarchizzate e ben distribuite.
- **Basso (0–4):** informazioni mancanti, confuse o ammassate.

## 3. Visibilità
Presenza visiva e capacità di farsi notare a scaffale: contrasto, leggibilità a
distanza, impatto della capsula e del rapporto figura/sfondo.
- **Alto (8–10):** forte contrasto, elementi leggibili da lontano, ottima presenza
  visiva (es. capsula in contrasto con bottiglia scura).
- **Basso (0–4):** scarso contrasto, testo poco leggibile, etichetta che "sparisce".

## 4. Coerenza
Coerenza tra stile dell'etichetta, colori, tipologia di vino e identità del brand.
- **Alto (8–10):** stile e colori perfettamente allineati al prestigio del vino e
  alla riconoscibilità del marchio.
- **Basso (0–4):** stile in contrasto con il tipo di vino o con l'immagine del brand.

## 5. Design
Qualità degli elementi grafici: simboli, illustrazioni, tipografia, originalità e
riconoscibilità.
- **Alto (8–10):** elemento grafico centrale forte e riconoscibile, tipografia
  curata, identità visiva distintiva.
- **Basso (0–4):** grafica anonima, tipografia trascurata, nessun elemento memorabile.

## 6. Attrattività per giovani
Appeal dell'etichetta verso un pubblico giovane (under 35): modernità, freschezza,
capacità di attrarre senza perdere credibilità.
- **Alto (8–10):** stile contemporaneo e accattivante anche per un pubblico giovane.
- **Basso (0–4):** stile percepito come datato o poco interessante per i giovani.

---

## Calcolo dell'indice neuro

L'indice neuro è la **media ponderata** delle 6 caratteristiche con i seguenti pesi:

| Caratteristica | Peso |
|---|---|
| Visibilità | 30,0% |
| Completezza | 17,5% |
| Attrattività per giovani | 16,0% |
| Coerenza | 14,5% |
| Design | 12,0% |
| Eleganza | 10,0% |

`indice_neuro = 0.30·visibilità + 0.175·completezza + 0.16·attrattività + 0.145·coerenza + 0.12·design + 0.10·eleganza`
