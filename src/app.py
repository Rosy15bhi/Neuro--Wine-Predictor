"""
Front-end del prototipo NEURO (Streamlit) — versione con tema "vino".

Schermata di upload: l'utente carica la foto di un'etichetta di vino
(preferibilmente su sfondo bianco). Il sistema:
  1. invia l'immagine al modello multimodale (vision.py),
  2. ottiene i 6 punteggi della rubrica,
  3. calcola l'indice neuro ponderato (scoring.py),
  4. mostra punteggi, indice e giudizio con una grafica curata.

Avvio:  python -m streamlit run src/app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Rende importabili i moduli locali quando si lancia "streamlit run src/app.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import FEATURES, FEATURE_LABELS, WEIGHTS  # noqa: E402
from scoring import compute_index, judgment            # noqa: E402
from vision import score_label                          # noqa: E402

load_dotenv()  # carica ANTHROPIC_API_KEY dal file .env

# ----------------------------------------------------------------------------
# Descrizioni brevi dei 6 criteri (per le schede introduttive)
# ----------------------------------------------------------------------------
CRITERIA_DESC = {
    "eleganza": ("Raffinatezza estetica complessiva: palette cromatica, "
                 "equilibrio e senso di pregio percepito."),
    "completezza": ("Presenza e ordine delle informazioni (denominazione, "
                    "annata, gradazione) senza sovraccaricare."),
    "visibilita": ("Capacità di farsi notare a scaffale: contrasto, "
                   "leggibilità a distanza, impatto visivo."),
    "coerenza": ("Allineamento tra stile dell'etichetta, tipologia di vino "
                 "e identità del brand."),
    "design": ("Qualità degli elementi grafici: simboli, tipografia, "
               "originalità e riconoscibilità."),
    "attrattivita_giovani": ("Appeal verso un pubblico giovane (under 35): "
                             "modernità e freschezza dello stile."),
}
CRITERIA_ICON = {
    "eleganza": "💎", "completezza": "📋", "visibilita": "👁",
    "coerenza": "🎯", "design": "🎨", "attrattivita_giovani": "✨",
}

# ----------------------------------------------------------------------------
# Configurazione pagina + tema
# ----------------------------------------------------------------------------
st.set_page_config(page_title="NEURO – Valutatore di etichette",
                   page_icon="🍷", layout="wide")

BORDEAUX = "#6d213c"
BORDEAUX_DARK = "#4a1228"
GOLD = "#c9a24b"
CREAM = "#faf6f0"

st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(160deg, {CREAM} 0%, #f3e9e4 100%); }}
section[data-testid="stSidebar"] {{ background:{BORDEAUX_DARK}; }}
section[data-testid="stSidebar"] * {{ color:#f3e3d8 !important; }}
.neuro-header {{ display:flex; align-items:center; gap:16px; margin: 4px 0 2px 0; }}
.neuro-header h1 {{ font-family: Georgia,'Times New Roman',serif; color:{BORDEAUX_DARK};
                   font-size:2.6rem; margin:0; letter-spacing:0.5px; }}
.neuro-sub {{ color:#6b5b52; font-size:1.05rem; margin: 0 0 18px 2px; max-width:760px; }}
.gold-rule {{ height:3px; background:linear-gradient(90deg,{GOLD},transparent);
             border:none; margin: 0 0 22px 0; border-radius:2px; }}
/* Sezione "come funziona" */
.how-wrap {{ display:flex; gap:16px; margin:6px 0 26px 0; flex-wrap:wrap; }}
.how-step {{ flex:1; min-width:210px; background:#fff; border-radius:14px; padding:18px 20px;
            box-shadow:0 3px 14px rgba(74,18,40,0.08); border-top:4px solid {GOLD}; }}
.how-step .n {{ display:inline-flex; width:28px; height:28px; border-radius:50%;
               background:{BORDEAUX}; color:#fff; align-items:center; justify-content:center;
               font-weight:700; font-size:0.9rem; margin-bottom:8px; }}
.how-step h4 {{ margin:4px 0 6px 0; color:{BORDEAUX_DARK}; font-size:1.05rem; }}
.how-step p {{ margin:0; color:#6b5b52; font-size:0.9rem; }}
/* Schede criteri */
.crit-title {{ font-family:Georgia,serif; color:{BORDEAUX_DARK}; font-size:1.4rem; margin:6px 0 12px 0; }}
.crit-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
@media (max-width:1100px) {{ .crit-grid {{ grid-template-columns:repeat(2,1fr); }} }}
.crit-card {{ background:#fff; border-radius:14px; padding:16px 18px;
             box-shadow:0 3px 14px rgba(74,18,40,0.08); border-left:4px solid {BORDEAUX}; }}
.crit-card .head {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }}
.crit-card .name {{ font-weight:700; color:{BORDEAUX_DARK}; font-size:1.05rem; }}
.crit-card .w {{ background:{GOLD}; color:{BORDEAUX_DARK}; font-weight:700; font-size:0.78rem;
                padding:3px 9px; border-radius:12px; }}
.crit-card p {{ margin:0; color:#6b5b52; font-size:0.88rem; line-height:1.4; }}
/* Card indice */
.index-card {{ background:linear-gradient(160deg,{BORDEAUX} 0%,{BORDEAUX_DARK} 100%);
              color:#fff; border-radius:18px; padding:26px 22px; text-align:center;
              box-shadow:0 8px 24px rgba(74,18,40,0.28); }}
.index-card .num {{ font-family:Georgia,serif; font-size:3.4rem; font-weight:700; line-height:1; }}
.index-card .max {{ font-size:1.1rem; opacity:0.75; }}
.index-card .label {{ text-transform:uppercase; letter-spacing:2px; font-size:0.78rem; opacity:0.85; margin-bottom:8px; }}
.index-card .judg {{ display:inline-block; margin-top:14px; background:{GOLD}; color:{BORDEAUX_DARK};
                    font-weight:700; padding:5px 16px; border-radius:20px; font-size:0.95rem; }}
/* Barre caratteristiche */
.feat-row {{ margin:14px 0; }}
.feat-top {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:5px; }}
.feat-name {{ font-weight:600; color:{BORDEAUX_DARK}; font-size:1.02rem; }}
.feat-weight {{ color:#9a8b82; font-size:0.8rem; }}
.feat-val {{ font-weight:700; color:{BORDEAUX_DARK}; font-size:1.02rem; }}
.bar-bg {{ background:#eaddd5; border-radius:10px; height:14px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:10px; }}
.feat-motiv {{ color:#6b5b52; font-size:0.88rem; margin-top:4px; font-style:italic; }}
.giudizio-box {{ background:#fff; border-left:5px solid {GOLD}; border-radius:8px;
                padding:16px 20px; color:#4a3f39; box-shadow:0 2px 10px rgba(0,0,0,0.05); }}
/* Consigli di miglioramento */
.tips-title {{ font-family:Georgia,serif; color:{BORDEAUX_DARK}; font-size:1.4rem; margin:26px 0 6px 0; }}
.tips-sub {{ color:#6b5b52; font-size:0.9rem; margin:0 0 14px 0; }}
.tip-card {{ background:#fff; border-radius:12px; padding:14px 18px; margin:10px 0;
            box-shadow:0 3px 12px rgba(74,18,40,0.07); display:flex; gap:14px; align-items:flex-start; }}
.tip-rank {{ flex:0 0 auto; width:30px; height:30px; border-radius:50%; background:{BORDEAUX};
            color:#fff; font-weight:700; display:flex; align-items:center; justify-content:center; font-size:0.9rem; }}
.tip-body {{ flex:1; }}
.tip-head {{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:3px; }}
.tip-name {{ font-weight:700; color:{BORDEAUX_DARK}; }}
.tip-gain {{ font-size:0.78rem; color:#fff; background:{GOLD}; padding:2px 9px; border-radius:11px; font-weight:700; }}
.tip-text {{ color:#4a3f39; font-size:0.92rem; margin:0; }}
.tip-now {{ color:#9a8b82; font-size:0.8rem; }}
/* Avviso retro */
.retro-warn {{ background:#fff4e0; border:1px solid #e0992b; border-left:5px solid #e0992b;
              border-radius:10px; padding:16px 20px; margin:4px 0 18px 0; color:#7a4b12; }}
.retro-warn b {{ color:#a85a08; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🍷 NEURO")
    st.markdown("**Valutatore automatico di etichette di vino**")
    st.markdown("---")
    st.markdown("### Come funziona")
    st.markdown(
        "1. Carichi la foto di un'etichetta\n"
        "2. Un modello multimodale (Claude) la valuta seguendo una rubrica\n"
        "3. I 6 voti vengono combinati nell'**indice neuro**")
    st.markdown("### Pesi dell'indice")
    st.markdown(
        "\n".join(f"- {FEATURE_LABELS[f]}: **{WEIGHTS[f]*100:.1f}%**" for f in FEATURES))
    st.caption("Pesi ricavati per regressione dal catalogo di 340 bottiglie "
               "(R² = 0,94).")

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    '<div class="neuro-header"><span style="font-size:2.6rem">🍷</span>'
    '<h1>NEURO – Valutatore di etichette</h1></div>', unsafe_allow_html=True)
st.markdown(
    '<p class="neuro-sub">Uno strumento di analisi del <b>packaging del vino</b>. '
    'Carica la foto di un\'etichetta (idealmente su sfondo bianco): un modello di '
    'intelligenza artificiale ne valuta sei caratteristiche estetiche e ne calcola '
    'un punteggio sintetico, l\'<b>indice neuro</b>, su scala da 0 a 10.</p>',
    unsafe_allow_html=True)
st.markdown('<hr class="gold-rule">', unsafe_allow_html=True)


def bar_color(v: float) -> str:
    if v >= 8:
        return "#2e7d32"
    if v >= 6:
        return "#e0992b"
    return "#c0392b"


def render_feature(name_key: str, value: float, motiv: str):
    label = FEATURE_LABELS[name_key]
    weight = WEIGHTS[name_key] * 100
    color = bar_color(value)
    pct = min(value / 10 * 100, 100)
    html = f"""
    <div class="feat-row">
      <div class="feat-top">
        <span class="feat-name">{label} <span class="feat-weight">· peso {weight:.1f}%</span></span>
        <span class="feat-val">{value:.1f}/10</span>
      </div>
      <div class="bar-bg"><div class="bar-fill" style="width:{pct:.0f}%;background:{color};"></div></div>
      {f'<div class="feat-motiv">{motiv}</div>' if motiv else ''}
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_intro():
    """Sezione descrittiva mostrata quando non è ancora stata caricata una foto."""
    st.markdown("""
    <div class="how-wrap">
      <div class="how-step"><span class="n">1</span><h4>Carica la foto</h4>
        <p>Scatta o seleziona l'immagine dell'etichetta, meglio se su sfondo bianco e ben illuminata.</p></div>
      <div class="how-step"><span class="n">2</span><h4>Analisi AI</h4>
        <p>Il modello multimodale osserva l'etichetta e assegna un voto 0–10 a ciascuna caratteristica, seguendo una rubrica.</p></div>
      <div class="how-step"><span class="n">3</span><h4>Indice neuro</h4>
        <p>I sei voti vengono combinati in una media ponderata: ottieni il punteggio finale e un giudizio sintetico.</p></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="crit-title">Le 6 caratteristiche valutate</div>',
                unsafe_allow_html=True)
    cards = ""
    for f in FEATURES:
        cards += f"""
        <div class="crit-card">
          <div class="head"><span class="name">{CRITERIA_ICON[f]} {FEATURE_LABELS[f]}</span>
            <span class="w">{WEIGHTS[f]*100:.1f}%</span></div>
          <p>{CRITERIA_DESC[f]}</p>
        </div>"""
    st.markdown(f'<div class="crit-grid">{cards}</div>', unsafe_allow_html=True)
    st.write("")
    st.info("👆 Carica un'immagine qui sopra per avviare la valutazione.")


# ----------------------------------------------------------------------------
# Avviso chiave API
# ----------------------------------------------------------------------------
if not os.environ.get("ANTHROPIC_API_KEY"):
    st.warning("⚠️ Nessuna ANTHROPIC_API_KEY trovata. Crea/compila il file `.env` "
               "(vedi `.env.example`) prima di analizzare un'immagine.")

# ----------------------------------------------------------------------------
# Upload
# ----------------------------------------------------------------------------
uploaded = st.file_uploader("Foto dell'etichetta",
                            type=["jpg", "jpeg", "png", "webp"])

if uploaded is None:
    render_intro()
else:
    left, right = st.columns([1, 1.4], gap="large")
    with left:
        st.image(uploaded, caption="Etichetta caricata", use_container_width=True)
        analyze = st.button("🔍 Analizza etichetta", type="primary",
                            use_container_width=True)

    if analyze:
        tmp_dir = Path(__file__).resolve().parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / uploaded.name
        tmp_path.write_bytes(uploaded.getbuffer())

        try:
            with st.spinner("Il modello sta valutando l'etichetta…"):
                result = score_label(str(tmp_path))
        except Exception as e:  # noqa: BLE001
            st.error(f"Errore durante l'analisi: {e}")
        else:
            punteggi = {f: float(result["punteggi"][f]) for f in FEATURES}
            motivazioni = result.get("motivazioni", {})
            indice = compute_index(punteggi)
            giudizio = judgment(indice)
            is_retro = str(result.get("lato", "fronte")).lower() == "retro"

            # Avviso limiti se la foto sembra il RETRO della bottiglia
            if is_retro:
                st.markdown(
                    '<div class="retro-warn">⚠️ <b>Sembra il retro della bottiglia.</b> '
                    'Il sistema (e il dataset di riferimento) sono tarati sul <b>fronte</b> '
                    'dell\'etichetta. Sul retro i punteggi non sono affidabili né '
                    'confrontabili con il catalogo: la completezza può risultare gonfiata '
                    'dai dati tecnici, mentre eleganza, design, visibilità e attrattività '
                    'vengono penalizzate ingiustamente. Per una valutazione valida, carica '
                    'la foto del fronte.</div>', unsafe_allow_html=True)

            with right:
                st.markdown(f"""
                <div class="index-card">
                  <div class="label">Indice neuro</div>
                  <div><span class="num">{indice:.2f}</span><span class="max"> / 10</span></div>
                  <div class="judg">{giudizio}</div>
                </div>""", unsafe_allow_html=True)
                st.write("")
                for f in FEATURES:
                    render_feature(f, punteggi[f], motivazioni.get(f, ""))

            if result.get("descrizione_generale"):
                st.write("")
                st.markdown(
                    f'<div class="giudizio-box"><b>Giudizio complessivo.</b> '
                    f'{result["descrizione_generale"]}</div>', unsafe_allow_html=True)

            # --- Consigli di miglioramento, ordinati per impatto sull'indice ---
            suggerimenti = result.get("suggerimenti", {})
            if suggerimenti:
                # potenziale guadagno sull'indice = (10 - voto) * peso
                ranked = sorted(
                    FEATURES,
                    key=lambda f: (10 - punteggi[f]) * WEIGHTS[f],
                    reverse=True)
                st.markdown('<div class="tips-title">Come arrivare al massimo</div>',
                            unsafe_allow_html=True)
                st.markdown(
                    '<p class="tips-sub">Consigli su misura per questa etichetta, '
                    'ordinati per impatto: in cima ci sono gli interventi che '
                    'farebbero salire di più l\'indice neuro.</p>',
                    unsafe_allow_html=True)
                rank = 0
                for f in ranked:
                    tip = suggerimenti.get(f, "")
                    if not tip:
                        continue
                    gain = (10 - punteggi[f]) * WEIGHTS[f]
                    rank += 1
                    gain_html = (f'<span class="tip-gain">+{gain:.2f} sull\'indice</span>'
                                 if gain > 0.001 else
                                 '<span class="tip-gain" style="background:#2e7d32">già al top</span>')
                    st.markdown(f"""
                    <div class="tip-card">
                      <div class="tip-rank">{rank}</div>
                      <div class="tip-body">
                        <div class="tip-head"><span class="tip-name">{FEATURE_LABELS[f]}
                          <span class="tip-now">· ora {punteggi[f]:.1f}/10</span></span>
                          {gain_html}</div>
                        <p class="tip-text">{tip}</p>
                      </div>
                    </div>""", unsafe_allow_html=True)

            with st.expander("Output grezzo (JSON)"):
                st.json(result)
