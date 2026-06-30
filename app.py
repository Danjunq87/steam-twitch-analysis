import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Indie Games on Twitch — 2025",
    page_icon="🎮",
    layout="wide"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    [data-testid="metric-container"] {
        background: #1a1a2e;
        border: 1px solid #2d2d4e;
        border-radius: 8px;
        padding: 1rem 1.25rem;
    }
    [data-testid="stMetricValue"] { color: #a78bfa; font-size: 1.6rem; }
    [data-testid="stMetricLabel"] { color: #9ca3af; font-size: 0.8rem; }
    [data-testid="stMetricDelta"] { font-size: 0.78rem; }
    h2 { border-bottom: 2px solid #a78bfa; padding-bottom: 0.3rem; }
    .methodology-note {
        background: #111827;
        border-left: 3px solid #a78bfa;
        padding: 0.6rem 1rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
        color: #9ca3af;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPER: layout padrão para todos os gráficos
# ─────────────────────────────────────────────
LAYOUT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#e5e7eb',
    font_size=13,
    uniformtext_minsize=11,
    uniformtext_mode='hide',
)
TEXT_FONT = dict(color='#ffffff', size=12)


def apply_style(fig, **extra):
    """Aplica tema escuro + texto branco em todas as barras."""
    fig.update_layout(**LAYOUT_BASE, **extra)
    fig.update_traces(textfont=TEXT_FONT)
    return fig


# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    indie     = pd.read_csv("data/indie_final.csv")
    nao_indie = pd.read_csv("data/naoindie_final.csv")

    indie['categoria']     = 'Indie'
    nao_indie['categoria'] = 'Non-Indie'

    indie['pct_pos_total'] = pd.to_numeric(indie['pct_pos_total'], errors='coerce')
    indie.loc[indie['pct_pos_total'] == -1, 'pct_pos_total'] = None

    for df in [indie, nao_indie]:
        df['release_year']     = pd.to_datetime(df['release_date'], errors='coerce').dt.year
        df['watch_time_hours'] = pd.to_numeric(df['watch_time_hours'], errors='coerce')
        df['streamers']        = pd.to_numeric(df['streamers'],        errors='coerce')
        df['peak_viewers']     = pd.to_numeric(df['peak_viewers'],     errors='coerce')

    # Dedup primário por nome exato
    indie     = indie.sort_values('watch_time_hours', ascending=False).drop_duplicates('name', keep='first')
    nao_indie = nao_indie.sort_values('watch_time_hours', ascending=False).drop_duplicates('name', keep='first')

    # Dedup secundário: remove duplicatas por caracteres especiais (™ ® ©)
    # Ex: "Rocket League" e "Rocket League®" viram a mesma chave
    for df in [indie, nao_indie]:
        df['_name_clean'] = df['name'].str.replace(r'[™®©]', '', regex=True).str.strip()

    indie     = indie.sort_values('watch_time_hours', ascending=False).drop_duplicates('_name_clean', keep='first').drop(columns=['_name_clean'])
    nao_indie = nao_indie.sort_values('watch_time_hours', ascending=False).drop_duplicates('_name_clean', keep='first').drop(columns=['_name_clean'])

    return indie, nao_indie


df_indie, df_nao_indie = load_data()

# ─────────────────────────────────────────────
# PRE-COMPUTED AGGREGATES
# ─────────────────────────────────────────────
total_indie     = df_indie['watch_time_hours'].sum()
total_nao_indie = df_nao_indie['watch_time_hours'].sum()
total_geral     = total_indie + total_nao_indie
pct_indie       = total_indie / total_geral * 100

top_indie_row     = df_indie.nlargest(1, 'watch_time_hours').iloc[0]
top_streamers_row = df_indie.nlargest(1, 'streamers').iloc[0]
jogos_2025_indie  = df_indie[df_indie['release_year'] == 2025]
jogos_2025_nao    = df_nao_indie[df_nao_indie['release_year'] == 2025]

avg_indie     = df_indie['watch_time_hours'].mean()
avg_nao_indie = df_nao_indie['watch_time_hours'].mean()
avg_ratio     = avg_nao_indie / avg_indie

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🎮 Indie Games on Twitch — 2025")
st.markdown(
    "**Do indie games punch above their weight on Twitch?**  \n"
    "Analysis of the top 1,000 most-watched games on Twitch in 2025, "
    "crossing Twitch viewership data (SullyGnome) with Steam catalog metadata."
)
st.markdown(
    '<div class="methodology-note">⚙️ <b>Methodology:</b> '
    'Games not on Steam (e.g. League of Legends, Fortnite, Nintendo titles) were classified manually '
    'and included to avoid distorting the non-indie side. '
    'Indie classification follows Steam genre tags. '
    'Watch hours sourced from SullyGnome (full year 2025).'
    '</div>',
    unsafe_allow_html=True
)
st.divider()

# ─────────────────────────────────────────────
# KPI STRIP
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Indie Titles Tracked",      f"{len(df_indie)}")
c2.metric("Non-Indie Titles Tracked",  f"{len(df_nao_indie)}")
c3.metric("Indie Share of Watch Hrs",  f"{pct_indie:.1f}%")
c4.metric("Avg Watch Hrs — Indie",     f"{avg_indie/1_000_000:.1f}M")
c5.metric("Avg Watch Hrs — Non-Indie", f"{avg_nao_indie/1_000_000:.1f}M",
          delta=f"{avg_ratio:.1f}× higher than indie", delta_color="off")
st.divider()

# ─────────────────────────────────────────────
# SECTION 1 — KEY FINDINGS
# ─────────────────────────────────────────────
st.header("💡 Key Findings")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.info(f"""
**📉 The Watch-Hour Gap Is Real — and Expected**

Non-indie games average **{avg_nao_indie/1_000_000:.1f}M watch hours** per title vs  
**{avg_indie/1_000_000:.1f}M** for indie — a **{avg_ratio:.1f}× gap**.

This reflects budget, IP recognition, and marketing investment, not audience preference.  
The more interesting question is which indie games close that gap.
""")

with col_b:
    top_hrs      = top_indie_row['watch_time_hours'] / 1_000_000
    nao_below    = df_nao_indie[df_nao_indie['watch_time_hours'] < top_indie_row['watch_time_hours']]
    pct_nao_below = len(nao_below) / len(df_nao_indie) * 100
    st.info(f"""
**🏆 Top Indie Beats Most Non-Indie Titles**

**{top_indie_row['name']}** generated **{top_hrs:.0f}M watch hours** —  
outperforming **{pct_nao_below:.0f}%** of all non-indie games in this dataset.

Single breakout titles skew the indie average upward significantly.
""")

with col_c:
    avg_2025_indie = jogos_2025_indie['watch_time_hours'].mean() / 1_000_000 if len(jogos_2025_indie) else 0
    avg_2025_nao   = jogos_2025_nao['watch_time_hours'].mean()   / 1_000_000 if len(jogos_2025_nao)   else 0
    indie_2025_pct = len(jogos_2025_indie) / len(df_indie) * 100
    st.info(f"""
**🚀 2025 Indie Launches Are Competitive**

2025 indie releases average **{avg_2025_indie:.1f}M hrs/game** vs  
**{avg_2025_nao:.1f}M** for non-indie in the same year.

**{len(jogos_2025_indie)} indie titles** ({indie_2025_pct:.0f}% of the indie set) launched in 2025  
and already appear in Twitch's top 1,000 for the year.
""")

col_d, col_e, col_f = st.columns(3)

with col_d:
    paid_indie     = df_indie[df_indie['price'] > 0]['watch_time_hours'].mean() / 1_000_000
    paid_nao_indie = df_nao_indie[df_nao_indie['price'] > 0]['watch_time_hours'].mean() / 1_000_000
    free_indie_n   = (df_indie['price'] == 0).sum()
    st.success(f"""
**💰 Paid Indie vs Paid Non-Indie**

Among paid titles only:  
— Paid indie avg: **{paid_indie:.1f}M hrs/game**  
— Paid non-indie avg: **{paid_nao_indie:.1f}M hrs/game**

{free_indie_n} free-to-play indie titles excluded to avoid  
mixing monetisation models in the comparison.
""")

with col_e:
    top_str_n = int(top_streamers_row['streamers'])
    st.success(f"""
**📡 Content Creation: Indies Drive Variety**

**{top_streamers_row['name']}** attracted **{top_str_n:,} streamers** —  
rivalling blockbuster titles in content creator reach.

Indie games with high streamer counts amplify a title  
far beyond what peak-viewer rankings alone show.
""")

with col_f:
    try:
        disp          = pd.read_csv("data/disponibilidade_steam.csv")
        on_steam_pct  = disp.loc[disp['disponibilidade'] == 'On Steam',     'pct_horas'].values[0]
        not_steam_pct = disp.loc[disp['disponibilidade'] == 'Not on Steam', 'pct_horas'].values[0]
    except Exception:
        on_steam_pct, not_steam_pct = 0, 0

    st.success(f"""
**🗺️ Steam ≠ Twitch: Platform Blind Spot**

Only **{on_steam_pct:.0f}%** of Twitch watch hours come from Steam-available games.  
**{not_steam_pct:.0f}%** belongs to closed-platform titles  
(Riot, Epic, Nintendo, Blizzard).

Any Steam-only dataset structurally undercounts non-indie viewership,  
making indie share appear higher than it actually is.
""")

st.divider()

# ─────────────────────────────────────────────
# SECTION 2 — TOP 20 MOST WATCHED
# ─────────────────────────────────────────────
st.header("📊 Top 20 Most Watched — Indie vs Non-Indie")
st.caption(
    "Non-Steam titles (League of Legends, VALORANT, Fortnite, etc.) added manually with SullyGnome data "
    "to ensure the non-indie side is not artificially deflated."
)

top20_indie = df_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()
top20_nao   = df_nao_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()

for df in [top20_indie, top20_nao]:
    df['watch_time_hours'] = (df['watch_time_hours'] / 1_000_000).round(1)

fig_comp = make_subplots(
    rows=2, cols=1,
    subplot_titles=(
        '🎮 Top 20 Indie Games (2025 watch hours)',
        '🏢 Top 20 Non-Indie Games (2025 watch hours)'
    ),
    vertical_spacing=0.1
)
fig_comp.add_trace(go.Bar(
    x=top20_indie.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_indie.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#7c3aed', name='Indie',
    text=top20_indie.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M'),
    textposition='outside',
    textfont=TEXT_FONT,
), row=1, col=1)
fig_comp.add_trace(go.Bar(
    x=top20_nao.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_nao.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#dc2626', name='Non-Indie',
    text=top20_nao.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M'),
    textposition='outside',
    textfont=TEXT_FONT,
), row=2, col=1)

fig_comp.update_layout(height=1150, showlegend=True, **LAYOUT_BASE)
fig_comp.update_xaxes(title_text='Watch Hours (Millions)', gridcolor='#1f2937')
st.plotly_chart(fig_comp, use_container_width=True)
st.divider()

# ─────────────────────────────────────────────
# SECTION 3 — GAME TYPE (Indie only)
# ─────────────────────────────────────────────
st.header("🕹️ Game Type Breakdown — Indie Only")
st.markdown(
    "Among indie games in the top 1,000, how does watch performance differ by game type? "
    "Avg = per-game efficiency; Total = aggregate audience size."
)

df_indie_tipos = df_indie[~df_indie['tipo'].isin(['Outro', None])].copy()
analise_tipo = df_indie_tipos.groupby('tipo', as_index=False).agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
    total_watch_hours=('watch_time_hours', 'sum'),
).round(0).sort_values('media_watch_hours', ascending=False)

col_t1, col_t2 = st.columns(2)

fig_tipo_avg = px.bar(
    analise_tipo, x='tipo', y='media_watch_hours', color='tipo', text='qtd_jogos',
    labels={'media_watch_hours': 'Avg Watch Hours', 'tipo': 'Game Type'},
    title='Average Watch Hours per Game Type',
    color_discrete_sequence=['#7c3aed', '#a78bfa', '#6d28d9']
)
fig_tipo_avg.update_traces(texttemplate='%{text} titles', textposition='outside')
fig_tipo_avg.update_yaxes(tickformat='.2s')
apply_style(fig_tipo_avg, showlegend=False)
col_t1.plotly_chart(fig_tipo_avg, use_container_width=True)

fig_tipo_tot = px.bar(
    analise_tipo, x='tipo', y='total_watch_hours', color='tipo', text='qtd_jogos',
    labels={'total_watch_hours': 'Total Watch Hours', 'tipo': 'Game Type'},
    title='Total Watch Hours per Game Type',
    color_discrete_sequence=['#dc2626', '#f87171', '#b91c1c']
)
fig_tipo_tot.update_traces(texttemplate='%{text} titles', textposition='outside')
fig_tipo_tot.update_yaxes(tickformat='.2s')
apply_style(fig_tipo_tot, showlegend=False)
col_t2.plotly_chart(fig_tipo_tot, use_container_width=True)

st.caption(
    "💡 A type can have a high average but low total if few games represent it — "
    "both charts together give the full picture."
)
st.divider()

# ─────────────────────────────────────────────
# SECTION 4 — PRICE RANGE
# ─────────────────────────────────────────────
st.header("💰 Price Range vs Twitch Performance")
st.markdown(
    "Free-to-play and paid titles are shown together for context, "
    "but interpret FTP numbers carefully — zero price lowers the streamer discovery barrier "
    "independently of game quality."
)

def faixa_preco(price):
    if pd.isna(price): return 'No Data'
    elif price == 0:   return 'Free to Play'
    elif price <= 20:  return '$1–$20'
    elif price <= 40:  return '$21–$40'
    elif price <= 60:  return '$41–$60'
    else:              return 'Above $60'

ordem = ['Free to Play', '$1–$20', '$21–$40', '$41–$60', 'Above $60', 'No Data']
col_p1, col_p2 = st.columns(2)

for df, label, col in [(df_indie, 'Indie', col_p1), (df_nao_indie, 'Non-Indie', col_p2)]:
    tmp = df.copy()
    tmp['faixa_preco'] = tmp['price'].apply(faixa_preco)
    agg = tmp.groupby('faixa_preco', as_index=False).agg(
        qtd_jogos=('name', 'count'),
        media_watch_hours=('watch_time_hours', 'mean'),
    ).round(0)
    cats = [c for c in ordem if c in agg['faixa_preco'].values]
    agg['faixa_preco'] = pd.Categorical(agg['faixa_preco'], categories=cats, ordered=True)
    agg = agg.sort_values('faixa_preco')

    fig = px.bar(agg, x='faixa_preco', y='media_watch_hours', color='faixa_preco',
                 text='qtd_jogos', title=f'{label} — Price Range vs Avg Watch Hours',
                 labels={'faixa_preco': 'Price Range', 'media_watch_hours': 'Avg Watch Hours'})
    fig.update_traces(texttemplate='%{text} titles', textposition='outside')
    fig.update_yaxes(tickformat='.2s')
    apply_style(fig, showlegend=False)
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 5 — STREAMERS
# ─────────────────────────────────────────────
st.header("📡 Top 15 by Number of Streamers")
st.caption("Number of unique channels that streamed each game during the analysis period.")

col_s1, col_s2 = st.columns(2)
for df, label, col in [(df_indie, 'Indie', col_s1), (df_nao_indie, 'Non-Indie', col_s2)]:
    top = df.nlargest(15, 'streamers')[['name', 'tipo', 'streamers']].copy()
    top['streamers'] = pd.to_numeric(top['streamers'], errors='coerce').fillna(0).astype(int)
    top = top.sort_values('streamers', ascending=True)
    fig = px.bar(top, x='streamers', y='name', color='tipo', orientation='h',
                 title=f'{label} — Top 15 by Streamers',
                 labels={'streamers': 'Streamers', 'name': 'Game', 'tipo': 'Type'},
                 text='streamers')
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    apply_style(fig)
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 6 — 2025 VS LEGACY
# ─────────────────────────────────────────────
st.header("🚀 2025 Releases vs Legacy Titles")
st.markdown(
    "Average watch hours per game by release cohort and category. "
    "Note: pre-2025 titles accumulate hours over multiple years — "
    "direct comparison understates 2025 performance."
)

todos = pd.concat([df_indie, df_nao_indie], ignore_index=True)
todos['cohort'] = todos['release_year'].apply(
    lambda x: '2025 Release' if x == 2025 else 'Pre-2025')

agg_ano = todos.groupby(['cohort', 'categoria'], as_index=False).agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0)

fig_ano = px.bar(agg_ano, x='cohort', y='media_watch_hours',
                 color='categoria', barmode='group', text='qtd_jogos',
                 title='Avg Watch Hours per Game — 2025 Releases vs Pre-2025',
                 labels={'cohort': '', 'media_watch_hours': 'Avg Watch Hours', 'categoria': 'Category'},
                 color_discrete_map={'Indie': '#7c3aed', 'Non-Indie': '#dc2626'})
fig_ano.update_traces(texttemplate='%{text} titles', textposition='outside')
fig_ano.update_yaxes(tickformat='.2s')
apply_style(fig_ano)
st.plotly_chart(fig_ano, use_container_width=True)

st.subheader("🆕 2025 Game Releases in This Dataset")
col_2a, col_2b = st.columns(2)
for df, label, col in [(df_indie, 'Indie', col_2a), (df_nao_indie, 'Non-Indie', col_2b)]:
    j25 = df[df['release_year'] == 2025][['name', 'tipo', 'watch_time_hours']].copy()
    j25['watch_time_hours'] = (j25['watch_time_hours'] / 1_000_000).round(1)
    j25 = j25.sort_values('watch_time_hours', ascending=False)
    j25.columns = ['Game', 'Type', 'Watch Hours (M)']
    col.markdown(f"**{label} — {len(j25)} titles**")
    col.dataframe(j25, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 7 — REVIEW SCORE VS VIEWERSHIP
# ─────────────────────────────────────────────
st.header("⭐ Steam Review Score vs Twitch Performance (Indie Only)")

sem_review = df_indie[df_indie['pct_pos_total'].isna()][['name', 'watch_time_hours']].copy()
sem_review['watch_time_hours_M'] = (sem_review['watch_time_hours'] / 1_000_000).round(1)
sem_review = sem_review.sort_values('watch_time_hours', ascending=False)

if len(sem_review) > 0:
    top5  = sem_review.head(5)
    lista = ', '.join(
        [f"**{r['name']}** ({r['watch_time_hours_M']:.1f}M hrs)" for _, r in top5.iterrows()]
    )
    extra = f" and {len(sem_review)-5} others" if len(sem_review) > 5 else ""
    st.warning(
        f"⚠️ **{len(sem_review)} games excluded** — not on Steam or too new for review data. "
        f"Top by watch hours: {lista}{extra}."
    )

df_rev = df_indie[df_indie['pct_pos_total'].notna() & (df_indie['pct_pos_total'] > 0)].copy()

def faixa_review(pct):
    if pct < 60:   return 'Below 60%'
    elif pct < 70: return '60–69%'
    elif pct < 80: return '70–79%'
    elif pct < 90: return '80–89%'
    else:          return '90–100%'

ordem_rev = ['Below 60%', '60–69%', '70–79%', '80–89%', '90–100%']
df_rev['faixa_review'] = df_rev['pct_pos_total'].apply(faixa_review)

agg_rev = df_rev.groupby('faixa_review', as_index=False).agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
    media_streamers=('streamers', 'mean'),
).round(0)
agg_rev['faixa_review'] = pd.Categorical(agg_rev['faixa_review'], categories=ordem_rev, ordered=True)
agg_rev = agg_rev.sort_values('faixa_review')

col_r1, col_r2 = st.columns(2)

fig_r1 = px.bar(agg_rev, x='faixa_review', y='media_watch_hours',
                color='faixa_review', text='qtd_jogos',
                title='Steam Review Score vs Avg Watch Hours',
                labels={'faixa_review': 'Positive Reviews', 'media_watch_hours': 'Avg Watch Hours'})
fig_r1.update_traces(texttemplate='%{text} titles', textposition='outside')
fig_r1.update_yaxes(tickformat='.2s')
apply_style(fig_r1, showlegend=False)
col_r1.plotly_chart(fig_r1, use_container_width=True)

fig_r2 = px.bar(agg_rev, x='faixa_review', y='media_streamers',
                color='faixa_review', text='qtd_jogos',
                title='Steam Review Score vs Avg Streamers',
                labels={'faixa_review': 'Positive Reviews', 'media_streamers': 'Avg Streamers'})
fig_r2.update_traces(texttemplate='%{text} titles', textposition='outside')
fig_r2.update_yaxes(tickformat='.2s')
apply_style(fig_r2, showlegend=False)
col_r2.plotly_chart(fig_r2, use_container_width=True)

st.caption(
    "Review score is one signal, not a predictor — a mid-review game with viral potential "
    "can easily outperform a critically acclaimed niche title."
)

with st.expander(f"📋 All {len(sem_review)} titles excluded from review analysis"):
    st.dataframe(
        sem_review[['name', 'watch_time_hours_M']].rename(
            columns={'name': 'Game', 'watch_time_hours_M': 'Watch Hours (M)'}),
        use_container_width=True
    )

st.divider()

# ─────────────────────────────────────────────
# SECTION 8 — STEAM COVERAGE
# ─────────────────────────────────────────────
st.header("🗺️ Distribution Platform Coverage")
st.markdown(
    "Of the top 1,000 most-watched Twitch games in 2025, how many are available on Steam? "
    "This matters for any Steam-centric market analysis."
)

try:
    disp = pd.read_csv("data/disponibilidade_steam.csv")
    label_map = {
        'On Steam':         '🟢 On Steam',
        'Not on Steam':     '🔴 Not on Steam',
        'Non-Game Content': '⬜ Non-Game Content',
        'Unknown':          '⚪ Unclassified',
    }
    disp['label'] = disp['disponibilidade'].map(label_map)

    col_pie, col_txt = st.columns([1, 1])

    fig_pie = px.pie(
        disp, names='label', values='total_watch_hours',
        title='Share of Twitch Watch Hours by Platform Availability',
        color='label',
        color_discrete_map={
            '🟢 On Steam':         '#059669',
            '🔴 Not on Steam':     '#dc2626',
            '⬜ Non-Game Content': '#6b7280',
            '⚪ Unclassified':     '#9ca3af',
        },
        hole=0.4
    )
    fig_pie.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont=dict(color='#e5e7eb', size=12)
    )
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e5e7eb', showlegend=False)
    col_pie.plotly_chart(fig_pie, use_container_width=True)

    with col_txt:
        st.markdown("### What This Means for the Analysis")
        for _, row in disp.iterrows():
            ico = label_map.get(row['disponibilidade'], row['disponibilidade'])
            st.markdown(
                f"**{ico}** — {row['qtd_jogos']} titles · "
                f"{row['total_watch_hours_bi']:.1f}B hours · **{row['pct_horas']:.1f}%** of total"
            )
        st.markdown("---")
        st.markdown(
            "Any analysis built on Steam data alone misses the 'Not on Steam' block, "
            "which includes the largest individual Twitch titles (League of Legends, Fortnite, "
            "VALORANT, all Nintendo IP). This dataset corrects for that by adding them manually."
        )

except FileNotFoundError:
    st.warning("disponibilidade_steam.csv not found. Run 04_missing_games.py first.")

st.divider()

# ─────────────────────────────────────────────
# SECTION 9 — OPPORTUNITY INDEX
# ─────────────────────────────────────────────
st.header("🎯 Streamer Opportunity Index — Indie Games")
st.markdown("""
**Definition:** Peak Viewers ÷ Number of Streamers.

A ratio of **30×** means 30 peak viewers existed for every active streamer —  
high audience, low creator saturation. For a new streamer, a high-ratio game offers  
**more potential viewers relative to the competition already streaming it.**

This is correlation, not guarantee: discoverability, clip culture, and hype windows  
also determine whether an audience finds a new channel.
""")
st.caption("Filter: ≥ 200 streamers and ≥ 500,000 total watch hours (removes low-data outliers).")

df_opp = df_indie.copy()
df_opp = df_opp[
    (df_opp['streamers'] >= 200) &
    (df_opp['watch_time_hours'] >= 500_000)
].copy()
df_opp['opportunity_ratio'] = (df_opp['peak_viewers'] / df_opp['streamers']).round(1)
df_opp = df_opp.nlargest(15, 'opportunity_ratio')[
    ['name', 'tipo', 'opportunity_ratio', 'peak_viewers', 'streamers', 'watch_time_hours']
].copy()
df_opp['watch_time_hours_M'] = (df_opp['watch_time_hours'] / 1_000_000).round(1)
df_opp = df_opp.sort_values('opportunity_ratio', ascending=True)

fig_opp = px.bar(
    df_opp, x='opportunity_ratio', y='name', color='tipo', orientation='h',
    title='Top 15 Indie Games — Peak Viewers per Streamer',
    labels={'opportunity_ratio': 'Peak Viewers per Streamer', 'name': 'Game', 'tipo': 'Type'},
    text='opportunity_ratio',
    custom_data=['peak_viewers', 'streamers', 'watch_time_hours_M']
)
fig_opp.update_traces(
    texttemplate='%{x:.0f}×',
    textposition='outside',
    textfont=TEXT_FONT,
    hovertemplate=(
        '<b>%{y}</b><br>'
        'Ratio: <b>%{x:.1f}×</b><br>'
        'Peak Viewers: %{customdata[0]:,}<br>'
        'Streamers: %{customdata[1]:,}<br>'
        'Watch Hours: %{customdata[2]}M<br>'
        '<extra></extra>'
    )
)
apply_style(fig_opp,
    xaxis_title='Peak Viewers per Active Streamer  (higher = less crowded for new creators)')
st.plotly_chart(fig_opp, use_container_width=True)

with st.expander("📊 Raw numbers — Opportunity Index"):
    show = df_opp[['name', 'tipo', 'peak_viewers', 'streamers', 'opportunity_ratio', 'watch_time_hours_M']].copy()
    show = show.sort_values('opportunity_ratio', ascending=False)
    show.columns = ['Game', 'Type', 'Peak Viewers', 'Streamers', 'Viewers/Streamer', 'Watch Hours (M)']
    st.dataframe(show, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# SECTION 10 — EXPLORE
# ─────────────────────────────────────────────
st.header("🔍 Explore the Full Dataset")

cat_filter  = st.selectbox("Category", ['Indie', 'Non-Indie'])
df_base     = df_indie if cat_filter == 'Indie' else df_nao_indie
tipo_opts   = sorted(df_base['tipo'].dropna().unique().tolist())
tipo_filter = st.multiselect("Game Type", options=tipo_opts, default=tipo_opts)

cols_show = ['name', 'tipo', 'price', 'watch_time_hours',
             'peak_viewers', 'streamers', 'pct_pos_total', 'release_year']
df_show = df_base[df_base['tipo'].isin(tipo_filter)][cols_show].copy()
df_show['watch_time_hours'] = (df_show['watch_time_hours'] / 1_000_000).round(2)
df_show = df_show.sort_values('watch_time_hours', ascending=False)
df_show.columns = ['Game', 'Type', 'Price ($)', 'Watch Hours (M)',
                   'Peak Viewers', 'Streamers', 'Positive Reviews (%)', 'Release Year']
st.dataframe(df_show, use_container_width=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption(
    "**Sources:** Steam API (March 2025 snapshot) · SullyGnome Twitch Statistics (full year 2025)  |  "
    "**Stack:** Python · Pandas · Plotly · Streamlit  |  "
    "**Author:** github.com/Danjunq87"
)