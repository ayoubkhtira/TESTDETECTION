import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import html
import textwrap

# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Plateforme Analyse Achats",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PALETTE
# ============================================================

PLOTLY_COLORS = [
    "#2563eb",
    "#16a34a",
    "#7c3aed",
    "#f97316",
    "#ef4444",
    "#0891b2",
    "#9333ea",
    "#0f766e"
]

# ============================================================
# FONCTION HTML ROBUSTE
# ============================================================

def render_html(content):
    clean_content = html.unescape(textwrap.dedent(content)).strip()
    st.markdown(clean_content, unsafe_allow_html=True)

# ============================================================
# CSS GLOBAL
# ============================================================

render_html("""
<style>
@import url('https://cdn-uicons.flaticon.com/2.6.0/uicons-bold-rounded/css/uicons-bold-rounded.css');
@import url('https://cdn-uicons.flaticon.com/2.6.0/uicons-regular-rounded/css/uicons-regular-rounded.css');

:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-soft: #eff6ff;
    --dark: #0f172a;
    --text: #1e293b;
    --muted: #64748b;
    --muted-soft: #94a3b8;
    --bg: #f8fafc;
    --surface: #ffffff;
    --border: #e2e8f0;
    --success: #16a34a;
    --warning: #f59e0b;
    --danger: #ef4444;
    --purple: #7c3aed;
    --orange: #f97316;
    --shadow-soft: 0 18px 45px rgba(15, 23, 42, 0.07);
    --shadow-card: 0 10px 30px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.main {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 32%),
        radial-gradient(circle at top right, rgba(124, 58, 237, 0.07), transparent 28%),
        var(--bg);
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2.5rem;
    max-width: 1440px;
}

[data-testid="stDecoration"],
#MainMenu,
footer {
    visibility: hidden;
}

/* ============================================================
   HEADER SIMPLE MODERNE
============================================================ */

.top-header {
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
    padding: 20px 24px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.97), rgba(239,246,255,0.96)),
        radial-gradient(circle at top right, rgba(37, 99, 235, 0.18), transparent 35%);
    border: 1px solid rgba(226, 232, 240, 0.95);
    box-shadow: 0 16px 38px rgba(15, 23, 42, 0.07);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    animation: headerFadeUp 0.7s ease both;
}

.top-header::before {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -80px;
    top: -120px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.10);
    animation: headerBlob 6s ease-in-out infinite;
}

.top-header-left,
.top-header-right {
    position: relative;
    z-index: 2;
}

.top-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.top-header-logo {
    width: 48px;
    height: 48px;
    border-radius: 17px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.25);
}

.top-header-title {
    color: #0f172a;
    font-size: 22px;
    font-weight: 950;
    letter-spacing: -0.4px;
}

.top-header-subtitle {
    color: #64748b;
    font-size: 13px;
    font-weight: 650;
    margin-top: 3px;
}

.top-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.top-header-pill {
    padding: 9px 13px;
    border-radius: 999px;
    background: rgba(255,255,255,0.88);
    border: 1px solid #e2e8f0;
    color: #334155;
    font-size: 12.5px;
    font-weight: 850;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
}

.top-header-pill.live {
    color: #16a34a;
    background: #ecfdf5;
    border-color: #bbf7d0;
}

@keyframes headerFadeUp {
    from {
        opacity: 0;
        transform: translateY(14px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes headerBlob {
    0%, 100% {
        transform: translateY(0) scale(1);
    }
    50% {
        transform: translateY(14px) scale(1.05);
    }
}

@media (max-width: 768px) {
    .top-header {
        flex-direction: column;
        align-items: flex-start;
        padding: 20px;
    }

    .top-header-right {
        width: 100%;
        flex-wrap: wrap;
    }

    .top-header-pill {
        flex: 1;
        text-align: center;
    }
}

/* ============================================================
   TITRES
============================================================ */

.section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 22px;
    font-weight: 950;
    color: var(--dark);
    margin: 24px 0 18px 0;
    letter-spacing: -0.35px;
}

.section-title i {
    width: 42px;
    height: 42px;
    border-radius: 15px;
    background: var(--primary-soft);
    color: var(--primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.sub-section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 900;
    color: var(--text);
    margin: 24px 0 15px 0;
}

.sub-section-title i {
    color: var(--primary);
}

/* ============================================================
   CARTES
============================================================ */

.card {
    background: rgba(255, 255, 255, 0.92);
    padding: 25px;
    border-radius: 24px;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border);
    min-height: 175px;
    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.09);
    border-color: #cbd5e1;
}

.card h4 {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--dark);
    margin: 0 0 11px 0;
    font-size: 17px;
    font-weight: 950;
}

.pro-icon {
    min-width: 42px;
    width: 42px;
    height: 42px;
    border-radius: 15px;
    background: var(--primary-soft);
    color: var(--primary);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.small-note {
    font-size: 13.5px;
    color: var(--muted);
    line-height: 1.65;
    margin: 0;
}

/* ============================================================
   KPI
============================================================ */

.metric-card {
    position: relative;
    overflow: hidden;
    background: white;
    padding: 22px 22px;
    border-radius: 23px;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border);
    min-height: 135px;
}

.metric-card::before {
    content: "";
    position: absolute;
    right: -35px;
    top: -35px;
    width: 105px;
    height: 105px;
    border-radius: 999px;
    background: var(--metric-soft, #eff6ff);
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    position: relative;
    z-index: 2;
}

.metric-icon {
    width: 39px;
    height: 39px;
    border-radius: 14px;
    background: var(--metric-soft, #eff6ff);
    color: var(--metric-color, #2563eb);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 17px;
}

.metric-label {
    font-size: 13px;
    color: var(--muted);
    font-weight: 850;
    margin-bottom: 8px;
    position: relative;
    z-index: 2;
}

.metric-value {
    font-size: 30px;
    color: var(--dark);
    font-weight: 950;
    letter-spacing: -0.7px;
    position: relative;
    z-index: 2;
}

.metric-help {
    font-size: 12px;
    color: var(--muted-soft);
    margin-top: 6px;
    line-height: 1.45;
    position: relative;
    z-index: 2;
}

/* ============================================================
   ALERTS
============================================================ */

.warning-box {
    background: linear-gradient(135deg, #fffbeb, #fff7ed);
    border: 1px solid #fde68a;
    color: #92400e;
    padding: 17px 19px;
    border-radius: 18px;
    font-weight: 820;
    display: flex;
    align-items: center;
    gap: 11px;
    box-shadow: 0 10px 25px rgba(245, 158, 11, 0.08);
}

.info-card {
    background: white;
    border: 1px dashed #cbd5e1;
    color: var(--muted);
    padding: 22px;
    border-radius: 22px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* ============================================================
   TABS
============================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: white;
    border: 1px solid var(--border);
    padding: 8px;
    border-radius: 20px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 15px;
    padding: 12px 18px;
    font-weight: 850;
    color: #475569;
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: var(--dark) !important;
    color: white !important;
}

/* ============================================================
   SIDEBAR
============================================================ */

div[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.28), transparent 35%),
        linear-gradient(180deg, #0f172a 0%, #111827 100%);
}

div[data-testid="stSidebar"] * {
    color: white;
}

div[data-testid="stSidebar"] label {
    color: #e5e7eb !important;
    font-weight: 800 !important;
    font-size: 13px !important;
}

.sidebar-brand {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.14);
    padding: 16px;
    border-radius: 22px;
    margin-bottom: 18px;
}

.sidebar-brand-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 950;
    margin-bottom: 8px;
}

.sidebar-brand-title i {
    color: #93c5fd;
}

.sidebar-brand-subtitle {
    color: #cbd5e1;
    font-size: 12.5px;
    line-height: 1.55;
}

.sidebar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 950;
    margin: 20px 0 10px 0;
    color: white;
}

.sidebar-title i {
    width: 31px;
    height: 31px;
    border-radius: 11px;
    background: rgba(147, 197, 253, 0.16);
    color: #93c5fd;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.sidebar-note {
    color: #cbd5e1;
    font-size: 13px;
    line-height: 1.55;
    margin-bottom: 14px;
}

.stDownloadButton > button,
.stButton > button {
    border-radius: 15px !important;
    border: 1px solid #dbeafe !important;
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    font-weight: 900 !important;
    padding: 0.7rem 1rem !important;
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.22);
}

[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.045);
}

[data-testid="stPlotlyChart"] {
    background: white;
    border-radius: 24px;
    border: 1px solid var(--border);
    padding: 12px;
    box-shadow: var(--shadow-card);
}

.footer {
    margin-top: 46px;
    padding: 18px 20px;
    border-radius: 20px;
    background: white;
    border: 1px solid var(--border);
    color: var(--muted);
    font-size: 12.5px;
    text-align: center;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
}
</style>
""")

# ============================================================
# HEADER COMPACT
# ============================================================

def app_header():
    render_html("""
    <div class="top-header">
        <div class="top-header-left">
            <div class="top-header-logo">🛒</div>
            <div>
                <div class="top-header-title">Achats Analytics</div>
                <div class="top-header-subtitle">Tableau de bord décisionnel achats</div>
            </div>
        </div>

        <div class="top-header-right">
            <span class="top-header-pill live">● Live</span>
            <span class="top-header-pill">Excel Ready</span>
        </div>
    </div>
    """)

app_header()

# ============================================================
# FONCTIONS EXCEL
# ============================================================

def get_excel_engine(file_name):
    file_name = file_name.lower()

    if file_name.endswith(".xlsx"):
        return "openpyxl"

    if file_name.endswith(".xls"):
        return "xlrd"

    return None


@st.cache_data(show_spinner=False)
def get_sheet_names(file_bytes, file_name):
    engine = get_excel_engine(file_name)

    if engine is None:
        raise ValueError("Format non supporté. Importez un fichier .xlsx ou .xls.")

    return pd.ExcelFile(BytesIO(file_bytes), engine=engine).sheet_names


@st.cache_data(show_spinner=False)
def read_sheet(file_bytes, file_name, sheet_name):
    engine = get_excel_engine(file_name)

    if engine is None:
        raise ValueError("Format non supporté. Importez un fichier .xlsx ou .xls.")

    return pd.read_excel(
        BytesIO(file_bytes),
        sheet_name=sheet_name,
        engine=engine
    )

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("\t", " ", regex=False)
        .str.replace("  ", " ", regex=False)
    )
    return df


def find_column(df, possible_names):
    if df.empty:
        return None

    cols = list(df.columns)
    cols_clean = {c.lower().strip(): c for c in cols}

    for name in possible_names:
        key = name.lower().strip()
        if key in cols_clean:
            return cols_clean[key]

    for col in cols:
        col_low = col.lower().strip()
        for name in possible_names:
            if name.lower().strip() in col_low:
                return col

    return None


def convert_dates(df, columns):
    df = df.copy()

    for col in columns:
        if col and col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def convert_numeric(df, columns):
    df = df.copy()

    for col in columns:
        if col and col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace("\u00a0", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def format_number(value):
    try:
        if pd.isna(value):
            return "0"
        return f"{value:,.0f}".replace(",", " ")
    except Exception:
        return "0"


def format_amount(value):
    try:
        if pd.isna(value):
            return "0,00"
        return f"{value:,.2f}".replace(",", " ").replace(".", ",")
    except Exception:
        return "0,00"


def get_soft_color(color):
    mapping = {
        "#2563eb": "#eff6ff",
        "#16a34a": "#ecfdf5",
        "#7c3aed": "#f5f3ff",
        "#f97316": "#fff7ed",
        "#f59e0b": "#fffbeb",
        "#ef4444": "#fef2f2",
        "#0891b2": "#ecfeff",
        "#9333ea": "#faf5ff",
        "#0f766e": "#f0fdfa"
    }
    return mapping.get(color, "#eff6ff")


def metric_card(label, value, help_text="", color="#2563eb", icon="fi fi-rr-stats"):
    soft = get_soft_color(color)

    render_html(
        f"""
        <div class="metric-card" style="--metric-color:{color}; --metric-soft:{soft};">
            <div class="metric-top">
                <div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                <div class="metric-icon">
                    <i class="{icon}"></i>
                </div>
            </div>
            <div class="metric-help">{help_text}</div>
        </div>
        """
    )


def section_title(icon, title):
    render_html(
        f"""
        <div class="section-title">
            <i class="{icon}"></i>
            <span>{title}</span>
        </div>
        """
    )


def sub_section_title(icon, title):
    render_html(
        f"""
        <div class="sub-section-title">
            <i class="{icon}"></i>
            <span>{title}</span>
        </div>
        """
    )


def sidebar_title(icon, title):
    render_html(
        f"""
        <div class="sidebar-title">
            <i class="{icon}"></i>
            <span>{title}</span>
        </div>
        """
    )


def empty_info(message):
    render_html(
        f"""
        <div class="info-card">
            <i class="fi fi-rr-info"></i>
            <span>{message}</span>
        </div>
        """
    )


def get_unique_values(df, col):
    if col and col in df.columns:
        return sorted(df[col].dropna().astype(str).unique())
    return []


def safe_group_count(df, group_col, count_col=None, top_n=15):
    if df.empty or not group_col or group_col not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp[group_col] = temp[group_col].fillna("Non renseigné").astype(str)

    if count_col and count_col in temp.columns:
        result = (
            temp.groupby(group_col)[count_col]
            .nunique()
            .reset_index(name="Nombre")
            .sort_values("Nombre", ascending=False)
            .head(top_n)
        )
    else:
        result = temp[group_col].value_counts().reset_index()
        result.columns = [group_col, "Nombre"]
        result = result.head(top_n)

    return result


def safe_group_sum(df, group_col, value_col, top_n=15):
    if df.empty or not group_col or not value_col:
        return pd.DataFrame()

    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp[group_col] = temp[group_col].fillna("Non renseigné").astype(str)

    return (
        temp.groupby(group_col)[value_col]
        .sum()
        .reset_index(name="Total")
        .sort_values("Total", ascending=False)
        .head(top_n)
    )


def apply_filters(df, filters):
    filtered = df.copy()

    for col, values in filters.items():
        if values and col in filtered.columns:
            filtered = filtered[filtered[col].astype(str).isin(values)]

    return filtered


def apply_date_filter(df, date_col, date_range):
    filtered = df.copy()

    if not date_col or date_col not in filtered.columns or date_range is None:
        return filtered

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered[date_col].dt.date >= start_date) &
            (filtered[date_col].dt.date <= end_date)
        ]

    return filtered


def download_excel_button(df, filename, label):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Données filtrées")

    st.download_button(
        label=label,
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


def data_quality_card(df):
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Lignes", format_number(total_rows), "Nombre total d'enregistrements", "#2563eb", "fi fi-rr-list")
    with c2:
        metric_card("Colonnes", format_number(total_cols), "Champs disponibles", "#7c3aed", "fi fi-rr-columns-3")
    with c3:
        metric_card("Cellules vides", format_number(missing_cells), "Valeurs manquantes", "#f59e0b", "fi fi-rr-triangle-warning")
    with c4:
        metric_card("Doublons", format_number(duplicate_rows), "Lignes dupliquées", "#ef4444", "fi fi-rr-copy")


def show_chart(fig, key):
    fig.update_layout(
        template="plotly_white",
        title=dict(
            font=dict(size=17, color="#0f172a"),
            x=0.02,
            xanchor="left"
        ),
        font=dict(
            family="Inter, system-ui, sans-serif",
            color="#334155"
        ),
        margin=dict(l=10, r=10, t=62, b=20),
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#eef2f7",
        zeroline=False,
        linecolor="#e2e8f0"
    )

    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#e2e8f0"
    )

    st.plotly_chart(fig, use_container_width=True, key=key)

# ============================================================
# SIDEBAR - IMPORT
# ============================================================

with st.sidebar:
    render_html("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">
            <i class="fi fi-br-shopping-cart"></i>
            <span>Achats Analytics</span>
        </div>
        <div class="sidebar-brand-subtitle">
            Import, filtrage et analyse décisionnelle des demandes et commandes achats.
        </div>
    </div>
    """)

    sidebar_title("fi fi-rr-settings-sliders", "Paramètres")

    render_html("""
    <div class="sidebar-note">
        Importez votre fichier Excel puis sélectionnez les feuilles correspondant aux demandes et commandes achats.
    </div>
    """)

    uploaded_file = st.file_uploader(
        "Importer un fichier Excel",
        type=["xlsx", "xls"]
    )

    st.markdown("---")

    sidebar_title("fi fi-rr-document", "Colonnes attendues")

    st.markdown("""
**Demandes :**
- Dem.achat
- Poste
- Article
- Désignation
- GAc
- Créé par
- Demandeur
- Quantité
- Date DA
- Date lanc.
- Div.

**Commandes :**
- Doc achat
- Article
- Désignation
- Date doc.
- Quantité
- Prix net
- Nom du fournisseur
- GAc
- Div.
- Dev.
""")

# ============================================================
# PAGE AVANT IMPORT
# ============================================================

if uploaded_file is None:
    render_html("""
    <div class="warning-box">
        <i class="fi fi-rr-info"></i>
        <span>Importez votre fichier Excel pour générer automatiquement vos analyses achats.</span>
    </div>
    """)

    sub_section_title("fi fi-rr-apps", "Ce que la plateforme vous permet de faire")

    f1, f2, f3 = st.columns(3)

    with f1:
        render_html("""
        <div class="card">
            <h4>
                <span class="pro-icon"><i class="fi fi-rr-file-invoice"></i></span>
                Analyse des demandes
            </h4>
            <p class="small-note">
                Identifiez les volumes de DA, les articles les plus demandés,
                les demandeurs actifs, les divisions concernées et les tendances mensuelles.
            </p>
        </div>
        """)

    with f2:
        render_html("""
        <div class="card">
            <h4>
                <span class="pro-icon"><i class="fi fi-rr-shopping-cart"></i></span>
                Pilotage des commandes
            </h4>
            <p class="small-note">
                Analysez les fournisseurs, les montants engagés, les articles commandés,
                les devises, les divisions et les évolutions dans le temps.
            </p>
        </div>
        """)

    with f3:
        render_html("""
        <div class="card">
            <h4>
                <span class="pro-icon"><i class="fi fi-rr-search-alt"></i></span>
                Détection des écarts
            </h4>
            <p class="small-note">
                Comparez les articles demandés et commandés afin d’identifier
                les demandes non transformées et les commandes hors demandes.
            </p>
        </div>
        """)

    render_html("""
    <div class="footer">
        Plateforme d’analyse achats — Développée par <strong>Ayoub Khtira</strong> pour <strong>Ciments du Maroc</strong>
    </div>
    """)

    st.stop()

# ============================================================
# LECTURE FICHIER
# ============================================================

try:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    sheet_names = get_sheet_names(file_bytes, file_name)

except ImportError as e:
    st.error("Un moteur Excel requis n’est pas installé.")
    st.info("Ajoute ces packages dans requirements.txt : openpyxl et xlrd.")
    st.code("pip install openpyxl xlrd")
    st.exception(e)
    st.stop()

except Exception as e:
    st.error("Erreur lors de la lecture du fichier Excel.")
    st.info(
        "Vérifie que le fichier est bien un vrai fichier Excel .xlsx ou .xls. "
        "Si nécessaire, ouvre le fichier dans Excel puis fais : "
        "Fichier > Enregistrer sous > Classeur Excel (*.xlsx)."
    )
    st.exception(e)
    st.stop()

with st.sidebar:
    st.markdown("---")
    sidebar_title("fi fi-rr-folder-open", "Feuilles Excel")

    demande_sheet = st.selectbox(
        "Feuille des demandes d'achat",
        options=["Aucune"] + sheet_names,
        index=1 if len(sheet_names) >= 1 else 0
    )

    commande_sheet = st.selectbox(
        "Feuille des commandes achats",
        options=["Aucune"] + sheet_names,
        index=2 if len(sheet_names) >= 2 else 0
    )

df_demandes = pd.DataFrame()
df_commandes = pd.DataFrame()

try:
    if demande_sheet != "Aucune":
        df_demandes = normalize_columns(
            read_sheet(file_bytes, file_name, demande_sheet)
        )

    if commande_sheet != "Aucune":
        df_commandes = normalize_columns(
            read_sheet(file_bytes, file_name, commande_sheet)
        )

except Exception as e:
    st.error("Erreur pendant la lecture des feuilles sélectionnées.")
    st.exception(e)
    st.stop()

# ============================================================
# MAPPING COLONNES DEMANDES
# ============================================================

dem_col_da = find_column(df_demandes, ["Dem.achat", "Demande achat", "DA"])
dem_col_poste = find_column(df_demandes, ["Poste"])
dem_col_article = find_column(df_demandes, ["Article"])
dem_col_designation = find_column(df_demandes, ["Désignation", "Designation"])
dem_col_gac = find_column(df_demandes, ["GAc", "GAC"])
dem_col_createur = find_column(df_demandes, ["Créé par", "Cree par", "Créateur"])
dem_col_demandeur = find_column(df_demandes, ["Demandeur"])
dem_col_quantite = find_column(df_demandes, ["Quantité", "Quantite"])
dem_col_date_da = find_column(df_demandes, ["Date DA", "Date demande"])
dem_col_date_lanc = find_column(df_demandes, ["Date lanc.", "Date lanc", "Date lancement"])
dem_col_div = find_column(df_demandes, ["Div.", "Div", "Division"])

if not df_demandes.empty:
    df_demandes = convert_dates(df_demandes, [dem_col_date_da, dem_col_date_lanc])
    df_demandes = convert_numeric(df_demandes, [dem_col_quantite])

# ============================================================
# MAPPING COLONNES COMMANDES
# ============================================================

cmd_col_article = find_column(df_commandes, ["Article"])
cmd_col_designation = find_column(df_commandes, ["Désignation", "Designation"])
cmd_col_doc = find_column(df_commandes, ["Doc achat", "Document achat", "Commande"])
cmd_col_poste = find_column(df_commandes, ["Poste"])
cmd_col_date = find_column(df_commandes, ["Date doc.", "Date doc", "Date document"])
cmd_col_quantite = find_column(df_commandes, ["Quantité", "Quantite"])
cmd_col_fournisseur = find_column(df_commandes, ["Nom du fournisseur", "Fournisseur"])
cmd_col_prix = find_column(df_commandes, ["Prix net", "Prix"])
cmd_col_devise = find_column(df_commandes, ["Dev.", "Devise"])
cmd_col_gac = find_column(df_commandes, ["GAc", "GAC"])
cmd_col_div = find_column(df_commandes, ["Div.", "Div", "Division"])

if not df_commandes.empty:
    df_commandes = convert_dates(df_commandes, [cmd_col_date])
    df_commandes = convert_numeric(df_commandes, [cmd_col_quantite, cmd_col_prix])

    if cmd_col_quantite and cmd_col_prix:
        df_commandes["Montant estimé"] = (
            df_commandes[cmd_col_quantite].fillna(0) *
            df_commandes[cmd_col_prix].fillna(0)
        )
    elif cmd_col_prix:
        df_commandes["Montant estimé"] = df_commandes[cmd_col_prix].fillna(0)
    else:
        df_commandes["Montant estimé"] = 0

# ============================================================
# TABS
# ============================================================

tab_overview, tab_demandes, tab_commandes, tab_compare, tab_data = st.tabs([
    "Vue globale",
    "Demandes d'achat",
    "Commandes achats",
    "Analyse croisée",
    "Données"
])

# ============================================================
# TAB 1 - VUE GLOBALE
# ============================================================

with tab_overview:
    section_title("fi fi-br-home", "Vue globale du fichier importé")

    nb_demandes = df_demandes[dem_col_da].nunique() if not df_demandes.empty and dem_col_da else len(df_demandes)
    nb_commandes = df_commandes[cmd_col_doc].nunique() if not df_commandes.empty and cmd_col_doc else len(df_commandes)
    nb_fournisseurs = df_commandes[cmd_col_fournisseur].nunique() if not df_commandes.empty and cmd_col_fournisseur else 0
    montant_total = df_commandes["Montant estimé"].sum() if not df_commandes.empty and "Montant estimé" in df_commandes.columns else 0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Demandes d'achat", format_number(nb_demandes), "Nombre de DA uniques", "#2563eb", "fi fi-rr-file-invoice")
    with c2:
        metric_card("Commandes achats", format_number(nb_commandes), "Nombre de commandes uniques", "#16a34a", "fi fi-rr-shopping-cart")
    with c3:
        metric_card("Fournisseurs", format_number(nb_fournisseurs), "Fournisseurs distincts", "#7c3aed", "fi fi-rr-users-alt")
    with c4:
        metric_card("Montant commandes", format_amount(montant_total), "Quantité × Prix net", "#f97316", "fi fi-rr-coins")

    sub_section_title("fi fi-rr-chart-histogram", "Synthèse visuelle")

    col_left, col_right = st.columns(2)

    with col_left:
        if not df_demandes.empty and dem_col_gac:
            data = safe_group_count(df_demandes, dem_col_gac, dem_col_da, 10)

            fig = px.bar(
                data,
                x="Nombre",
                y=dem_col_gac,
                orientation="h",
                title="Top GAc par nombre de demandes",
                text="Nombre",
                color_discrete_sequence=PLOTLY_COLORS
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            show_chart(fig, "overview_top_gac")
        else:
            empty_info("Aucune donnée demande exploitable pour le graphique GAc.")

    with col_right:
        if not df_commandes.empty and cmd_col_fournisseur:
            data = safe_group_sum(df_commandes, cmd_col_fournisseur, "Montant estimé", 10)

            fig = px.bar(
                data,
                x="Total",
                y=cmd_col_fournisseur,
                orientation="h",
                title="Top fournisseurs par montant estimé",
                text="Total",
                color_discrete_sequence=PLOTLY_COLORS
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            show_chart(fig, "overview_top_fournisseurs")
        else:
            empty_info("Aucune donnée commande exploitable pour le graphique fournisseurs.")

# ============================================================
# TAB 2 - DEMANDES
# ============================================================

with tab_demandes:
    section_title("fi fi-rr-file-invoice", "Analyse des demandes d’achat")

    if df_demandes.empty:
        st.warning("Aucune feuille de demandes sélectionnée ou feuille vide.")

    else:
        with st.sidebar:
            st.markdown("---")
            sidebar_title("fi fi-rr-filter", "Filtres demandes")

            dem_filters = {}

            if dem_col_gac:
                dem_filters[dem_col_gac] = st.multiselect(
                    "GAc",
                    get_unique_values(df_demandes, dem_col_gac)
                )

            if dem_col_demandeur:
                dem_filters[dem_col_demandeur] = st.multiselect(
                    "Demandeur",
                    get_unique_values(df_demandes, dem_col_demandeur)
                )

            if dem_col_createur:
                dem_filters[dem_col_createur] = st.multiselect(
                    "Créateur",
                    get_unique_values(df_demandes, dem_col_createur)
                )

            if dem_col_div:
                dem_filters[dem_col_div] = st.multiselect(
                    "Division",
                    get_unique_values(df_demandes, dem_col_div)
                )

            dem_date_range = None

            if dem_col_date_da and dem_col_date_da in df_demandes.columns and df_demandes[dem_col_date_da].notna().any():
                min_date = df_demandes[dem_col_date_da].min().date()
                max_date = df_demandes[dem_col_date_da].max().date()

                dem_date_range = st.date_input(
                    "Période Date DA",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="dem_date_range"
                )

        df_dem_filtered = apply_filters(df_demandes, dem_filters)
        df_dem_filtered = apply_date_filter(df_dem_filtered, dem_col_date_da, dem_date_range)

        total_da = df_dem_filtered[dem_col_da].nunique() if dem_col_da else len(df_dem_filtered)
        total_lignes = len(df_dem_filtered)
        total_articles = df_dem_filtered[dem_col_article].nunique() if dem_col_article else 0
        total_quantite = df_dem_filtered[dem_col_quantite].sum() if dem_col_quantite else 0

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("DA uniques", format_number(total_da), "Demandes distinctes", "#2563eb", "fi fi-rr-file-invoice")
        with c2:
            metric_card("Lignes DA", format_number(total_lignes), "Postes de demandes", "#16a34a", "fi fi-rr-list")
        with c3:
            metric_card("Articles", format_number(total_articles), "Articles distincts", "#7c3aed", "fi fi-rr-box")
        with c4:
            metric_card("Quantité totale", format_number(total_quantite), "Somme des quantités", "#f97316", "fi fi-rr-calculator")

        sub_section_title("fi fi-rr-chart-histogram", "Analyses principales")

        g1, g2 = st.columns(2)

        with g1:
            if dem_col_div:
                data = safe_group_count(df_dem_filtered, dem_col_div, dem_col_da, 15)

                fig = px.bar(
                    data,
                    x=dem_col_div,
                    y="Nombre",
                    title="Nombre de demandes par division",
                    text="Nombre",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                show_chart(fig, "demandes_division")

            elif dem_col_gac:
                data = safe_group_count(df_dem_filtered, dem_col_gac, dem_col_da, 15)

                fig = px.bar(
                    data,
                    x=dem_col_gac,
                    y="Nombre",
                    title="Nombre de demandes par GAc",
                    text="Nombre",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                show_chart(fig, "demandes_gac")

            else:
                empty_info("Colonne Division ou GAc non disponible.")

        with g2:
            if dem_col_designation:
                data = safe_group_count(df_dem_filtered, dem_col_designation, None, 15)

                fig = px.bar(
                    data,
                    x="Nombre",
                    y=dem_col_designation,
                    orientation="h",
                    title="Top articles demandés",
                    text="Nombre",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                show_chart(fig, "demandes_articles")
            else:
                empty_info("Colonne Désignation non disponible.")

        g3, g4 = st.columns(2)

        with g3:
            if dem_col_demandeur:
                data = safe_group_count(df_dem_filtered, dem_col_demandeur, dem_col_da, 15)

                fig = px.bar(
                    data,
                    x="Nombre",
                    y=dem_col_demandeur,
                    orientation="h",
                    title="Top demandeurs par nombre de DA",
                    text="Nombre",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                show_chart(fig, "demandes_demandeurs")
            else:
                empty_info("Colonne demandeur non disponible.")

        with g4:
            if dem_col_date_da:
                trend = (
                    df_dem_filtered
                    .dropna(subset=[dem_col_date_da])
                    .groupby(df_dem_filtered[dem_col_date_da].dt.to_period("M"))
                    .size()
                    .reset_index(name="Nombre")
                )

                if not trend.empty:
                    trend[dem_col_date_da] = trend[dem_col_date_da].astype(str)

                    fig = px.line(
                        trend,
                        x=dem_col_date_da,
                        y="Nombre",
                        markers=True,
                        title="Évolution mensuelle des demandes",
                        color_discrete_sequence=PLOTLY_COLORS
                    )
                    show_chart(fig, "demandes_trend")
                else:
                    empty_info("Aucune donnée temporelle disponible.")
            else:
                empty_info("Colonne Date DA non disponible.")

        sub_section_title("fi fi-rr-database", "Qualité des données demandes")
        data_quality_card(df_dem_filtered)

        sub_section_title("fi fi-rr-table", "Données demandes filtrées")
        st.dataframe(df_dem_filtered, use_container_width=True, height=420)

        download_excel_button(
            df_dem_filtered,
            "demandes_filtrees.xlsx",
            "Télécharger les demandes filtrées"
        )

# ============================================================
# TAB 3 - COMMANDES
# ============================================================

with tab_commandes:
    section_title("fi fi-rr-shopping-cart", "Analyse des commandes achats")

    if df_commandes.empty:
        st.warning("Aucune feuille de commandes sélectionnée ou feuille vide.")

    else:
        with st.sidebar:
            st.markdown("---")
            sidebar_title("fi fi-rr-filter", "Filtres commandes")

            cmd_filters = {}

            if cmd_col_fournisseur:
                cmd_filters[cmd_col_fournisseur] = st.multiselect(
                    "Fournisseur",
                    get_unique_values(df_commandes, cmd_col_fournisseur)
                )

            if cmd_col_div:
                cmd_filters[cmd_col_div] = st.multiselect(
                    "Division commande",
                    get_unique_values(df_commandes, cmd_col_div)
                )

            if cmd_col_gac:
                cmd_filters[cmd_col_gac] = st.multiselect(
                    "GAc commande",
                    get_unique_values(df_commandes, cmd_col_gac)
                )

            if cmd_col_devise:
                cmd_filters[cmd_col_devise] = st.multiselect(
                    "Devise",
                    get_unique_values(df_commandes, cmd_col_devise)
                )

            cmd_date_range = None

            if cmd_col_date and cmd_col_date in df_commandes.columns and df_commandes[cmd_col_date].notna().any():
                min_date = df_commandes[cmd_col_date].min().date()
                max_date = df_commandes[cmd_col_date].max().date()

                cmd_date_range = st.date_input(
                    "Période Date document",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="cmd_date_range"
                )

        df_cmd_filtered = apply_filters(df_commandes, cmd_filters)
        df_cmd_filtered = apply_date_filter(df_cmd_filtered, cmd_col_date, cmd_date_range)

        total_cmd = df_cmd_filtered[cmd_col_doc].nunique() if cmd_col_doc else len(df_cmd_filtered)
        total_lignes_cmd = len(df_cmd_filtered)
        total_fournisseurs = df_cmd_filtered[cmd_col_fournisseur].nunique() if cmd_col_fournisseur else 0
        total_montant = df_cmd_filtered["Montant estimé"].sum() if "Montant estimé" in df_cmd_filtered.columns else 0

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("Commandes uniques", format_number(total_cmd), "Documents achats distincts", "#2563eb", "fi fi-rr-shopping-cart")
        with c2:
            metric_card("Lignes commandes", format_number(total_lignes_cmd), "Postes de commandes", "#16a34a", "fi fi-rr-list")
        with c3:
            metric_card("Fournisseurs", format_number(total_fournisseurs), "Fournisseurs distincts", "#7c3aed", "fi fi-rr-users-alt")
        with c4:
            metric_card("Montant total", format_amount(total_montant), "Quantité × Prix net", "#f97316", "fi fi-rr-coins")

        sub_section_title("fi fi-rr-chart-histogram", "Analyses fournisseurs, articles et divisions")

        g1, g2 = st.columns(2)

        with g1:
            if cmd_col_fournisseur:
                data = safe_group_sum(df_cmd_filtered, cmd_col_fournisseur, "Montant estimé", 15)

                fig = px.bar(
                    data,
                    x="Total",
                    y=cmd_col_fournisseur,
                    orientation="h",
                    title="Top fournisseurs par montant estimé",
                    text="Total",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                show_chart(fig, "commandes_fournisseurs")
            else:
                empty_info("Colonne fournisseur non disponible.")

        with g2:
            if cmd_col_designation:
                data = safe_group_sum(df_cmd_filtered, cmd_col_designation, "Montant estimé", 15)

                fig = px.bar(
                    data,
                    x="Total",
                    y=cmd_col_designation,
                    orientation="h",
                    title="Top articles par montant estimé",
                    text="Total",
                    color_discrete_sequence=PLOTLY_COLORS
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                show_chart(fig, "commandes_articles")
            else:
                empty_info("Colonne désignation non disponible.")

        g3, g4 = st.columns(2)

        with g3:
            if cmd_col_div:
                data = safe_group_sum(df_cmd_filtered, cmd_col_div, "Montant estimé", 15)

                fig = px.pie(
                    data,
                    names=cmd_col_div,
                    values="Total",
                    title="Répartition du montant par division",
                    hole=0.5,
                    color_discrete_sequence=PLOTLY_COLORS
                )
                show_chart(fig, "commandes_division")

            elif cmd_col_gac:
                data = safe_group_sum(df_cmd_filtered, cmd_col_gac, "Montant estimé", 15)

                fig = px.pie(
                    data,
                    names=cmd_col_gac,
                    values="Total",
                    title="Répartition du montant par GAc",
                    hole=0.5,
                    color_discrete_sequence=PLOTLY_COLORS
                )
                show_chart(fig, "commandes_gac")
            else:
                empty_info("Colonne division ou GAc non disponible.")

        with g4:
            if cmd_col_date:
                trend = (
                    df_cmd_filtered
                    .dropna(subset=[cmd_col_date])
                    .groupby(df_cmd_filtered[cmd_col_date].dt.to_period("M"))["Montant estimé"]
                    .sum()
                    .reset_index(name="Montant")
                )

                if not trend.empty:
                    trend[cmd_col_date] = trend[cmd_col_date].astype(str)

                    fig = px.line(
                        trend,
                        x=cmd_col_date,
                        y="Montant",
                        markers=True,
                        title="Évolution mensuelle des montants commandes",
                        color_discrete_sequence=PLOTLY_COLORS
                    )
                    show_chart(fig, "commandes_trend")
                else:
                    empty_info("Aucune donnée temporelle disponible.")
            else:
                empty_info("Colonne Date document non disponible.")

        sub_section_title("fi fi-rr-ranking-star", "Classements avancés")

        t1, t2, t3 = st.columns(3)

        with t1:
            if cmd_col_fournisseur:
                st.markdown("#### Fournisseurs par nombre de commandes")
                top_nb_cmd = safe_group_count(df_cmd_filtered, cmd_col_fournisseur, cmd_col_doc, 10)
                st.dataframe(top_nb_cmd, use_container_width=True, height=320)

        with t2:
            if cmd_col_designation and cmd_col_quantite:
                st.markdown("#### Articles par quantité")
                top_qty = safe_group_sum(df_cmd_filtered, cmd_col_designation, cmd_col_quantite, 10)
                st.dataframe(top_qty, use_container_width=True, height=320)

        with t3:
            if cmd_col_gac:
                st.markdown("#### GAc par montant")
                top_gac = safe_group_sum(df_cmd_filtered, cmd_col_gac, "Montant estimé", 10)
                st.dataframe(top_gac, use_container_width=True, height=320)

        sub_section_title("fi fi-rr-database", "Qualité des données commandes")
        data_quality_card(df_cmd_filtered)

        sub_section_title("fi fi-rr-table", "Données commandes filtrées")
        st.dataframe(df_cmd_filtered, use_container_width=True, height=420)

        download_excel_button(
            df_cmd_filtered,
            "commandes_filtrees.xlsx",
            "Télécharger les commandes filtrées"
        )

# ============================================================
# TAB 4 - ANALYSE CROISÉE
# ============================================================

with tab_compare:
    section_title("fi fi-rr-search-alt", "Analyse croisée demandes vs commandes")

    if df_demandes.empty or df_commandes.empty:
        st.warning("L’analyse croisée nécessite les deux feuilles : demandes et commandes.")

    elif not dem_col_article or not cmd_col_article:
        st.warning("L’analyse croisée nécessite la colonne Article dans les deux feuilles.")

    else:
        articles_demandes = set(df_demandes[dem_col_article].dropna().astype(str))
        articles_commandes = set(df_commandes[cmd_col_article].dropna().astype(str))

        articles_communs = articles_demandes.intersection(articles_commandes)
        articles_non_commandes = articles_demandes - articles_commandes
        articles_commandes_hors_demandes = articles_commandes - articles_demandes

        taux_couverture = (
            len(articles_communs) / len(articles_demandes) * 100
            if len(articles_demandes) > 0 else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("Articles demandés", format_number(len(articles_demandes)), "Articles dans les DA", "#2563eb", "fi fi-rr-box")
        with c2:
            metric_card("Articles commandés", format_number(len(articles_commandes)), "Articles dans les commandes", "#16a34a", "fi fi-rr-shopping-cart")
        with c3:
            metric_card("Articles communs", format_number(len(articles_communs)), f"Taux couverture : {taux_couverture:.1f}%", "#7c3aed", "fi fi-rr-check-circle")
        with c4:
            metric_card("Demandés non commandés", format_number(len(articles_non_commandes)), "Écart potentiel", "#ef4444", "fi fi-rr-triangle-warning")

        sub_section_title("fi fi-rr-chart-pie-alt", "Couverture articles")

        coverage_df = pd.DataFrame({
            "Catégorie": [
                "Articles communs",
                "Demandés non commandés",
                "Commandés hors demandes"
            ],
            "Nombre": [
                len(articles_communs),
                len(articles_non_commandes),
                len(articles_commandes_hors_demandes)
            ]
        })

        fig = px.bar(
            coverage_df,
            x="Catégorie",
            y="Nombre",
            text="Nombre",
            title="Couverture entre demandes et commandes",
            color="Catégorie",
            color_discrete_sequence=PLOTLY_COLORS
        )
        show_chart(fig, "compare_couverture")

        if articles_non_commandes:
            sub_section_title("fi fi-rr-triangle-warning", "Articles demandés mais non commandés")

            non_cmd_df = df_demandes[
                df_demandes[dem_col_article].astype(str).isin(articles_non_commandes)
            ]

            st.dataframe(non_cmd_df, use_container_width=True, height=350)

            download_excel_button(
                non_cmd_df,
                "articles_demandes_non_commandes.xlsx",
                "Télécharger les articles demandés non commandés"
            )
        else:
            st.success("Tous les articles demandés existent dans les commandes.")

# ============================================================
# TAB 5 - DONNÉES
# ============================================================

with tab_data:
    section_title("fi fi-rr-folder-open", "Exploration des données")

    data_tab1, data_tab2 = st.tabs(["Demandes", "Commandes"])

    with data_tab1:
        if df_demandes.empty:
            st.info("Aucune donnée demande disponible.")
        else:
            sub_section_title("fi fi-rr-table", "Aperçu demandes")
            st.dataframe(df_demandes, use_container_width=True, height=500)

            sub_section_title("fi fi-rr-list", "Colonnes détectées demandes")
            st.write(list(df_demandes.columns))

    with data_tab2:
        if df_commandes.empty:
            st.info("Aucune donnée commande disponible.")
        else:
            sub_section_title("fi fi-rr-table", "Aperçu commandes")
            st.dataframe(df_commandes, use_container_width=True, height=500)

            sub_section_title("fi fi-rr-list", "Colonnes détectées commandes")
            st.write(list(df_commandes.columns))

# ============================================================
# FOOTER
# ============================================================

render_html("""
<div class="footer">
    Plateforme d’analyse achats — Développée par <strong>Ayoub Khtira</strong> pour <strong>Ciments du Maroc</strong>
</div>
""")
