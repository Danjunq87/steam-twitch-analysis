import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Indie Games & Twitch Analysis",
    page_icon="🎮",
    layout="wide"
)

# ============================================================
# CARREGA DADOS
# ============================================================
@st.cache_data
def load_data():
    indie = pd.read_csv("data/indie_final.csv")
    nao_indie = pd.read_csv("data/naoindie_final.csv")
    indie['categoria'] = 'Indie'
    nao_indie['categoria'] = 'Não-Indie'
    indie['pct_pos_total'] = pd.to_numeric(indie['pct_pos_total'], errors='coerce')
    indie.loc[indie['pct_pos_total'] == -1, 'pct_pos_total'] = None
    indie['release_year'] = pd.to_datetime(indie['release_date'], errors='coerce').dt.year
    nao_indie['release_year'] = pd.to_datetime(nao_indie['release_date'], errors='coerce').dt.year
    return indie, nao_indie

df_indie, df_nao_indie = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("🎮 Indie Games & Twitch — 2025")
st.markdown("**How do indie games perform on Twitch compared to AAA titles?**")
st.divider()

# ============================================================
# MÉTRICAS PRINCIPAIS
# ============================================================
total_indie = df_indie['watch_time_hours'].sum()
total_nao_indie = df_nao_indie['watch_time_hours'].sum()
total_geral = total_indie + total_nao_indie
pct_indie = total_indie / total_geral * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Indie Games Analyzed", f"{len(df_indie)}")
col2.metric("Non-Indie Games Analyzed", f"{len(df_nao_indie)}")
col3.metric("Indie Share of Watch Hours", f"{pct_indie:.1f}%")
col4.metric("Total Watch Hours (Indie)", f"{total_indie/1_000_000:.0f}M hrs")

st.divider()

# ============================================================
# SEÇÃO 1: KEY INSIGHTS
# ============================================================
st.header("💡 Key Insights")

top_indie = df_indie.nlargest(1, 'watch_time_hours').iloc[0]
top_nao_indie = df_nao_indie.nlargest(1, 'watch_time_hours').iloc[0]
top_streamers_game = df_indie.nlargest(1, 'streamers').iloc[0]
jogos_2025_indie = df_indie[df_indie['release_year'] == 2025]
jogos_2025_nao_indie = df_nao_indie[df_nao_indie['release_year'] == 2025]

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.info(f"""
    **🏆 Top Indie Game on Twitch**
    
    **{top_indie['name']}** generated **{top_indie['watch_time_hours']/1_000_000:.0f}M watch hours** in 2025 — 
    competing directly with major AAA titles despite being an indie production.
    """)

with col_b:
    st.info(f"""
    **📡 Most Streamed Indie Game**
    
    **{top_streamers_game['name']}** attracted **{int(top_streamers_game['streamers']):,} streamers** — 
    more than many blockbuster titles, proving that fun gameplay drives content creation.
    """)

with col_c:
    st.info(f"""
    **🚀 2025 Indie Launches**
    
    **{len(jogos_2025_indie)} indie games** launched in 2025 already appear in Twitch's top 1000, 
    vs **{len(jogos_2025_nao_indie)} non-indie** — showing how quickly indie games gain streaming traction.
    """)

col_d, col_e, col_f = st.columns(3)

with col_d:
    media_indie_2025 = jogos_2025_indie['watch_time_hours'].mean() / 1_000_000 if len(jogos_2025_indie) > 0 else 0
    media_indie_old = df_indie[df_indie['release_year'] < 2025]['watch_time_hours'].mean() / 1_000_000
    st.success(f"""
   
    **New vs Legacy Indie Games**
    
    2025 indie releases average **{media_indie_2025:.1f}M watch hours** vs 
    **{media_indie_old:.1f}M** for established titles — legacy games maintain strong audiences 
    while 2025 newcomers like R.E.P.O., Peak and Schedule I are already competing at the top.
    """)

with col_e:
    free_indie = df_indie[df_indie['price'] == 0]['watch_time_hours'].mean() / 1_000_000
    paid_indie = df_indie[df_indie['price'] > 0]['watch_time_hours'].mean() / 1_000_000
    st.success(f"""
    **💰 Free vs Paid Indie Games**
    
    Free indie games average **{free_indie:.1f}M watch hours** vs 
    **{paid_indie:.1f}M** for paid titles — lower barrier to entry drives more streaming activity.
    """)

with col_f:
    st.success(f"""
    **🏢 David vs Goliath**
    
    Indie games represent only **{pct_indie:.1f}%** of total Twitch watch hours analyzed, 
    yet **{len(df_indie)}** indie titles compete against **{len(df_nao_indie)}** major studio games.
    The top indie game (**{top_indie['name']}**) beats many AAA titles.
    """)

st.divider()

# ============================================================
# SEÇÃO 2: INDIE VS NÃO-INDIE
# ============================================================
st.header("📊 Indie vs Non-Indie — Top 20 Most Watched")
st.caption("⚠️ Games not on Steam (e.g. League of Legends, VALORANT, Fortnite) were added manually with SullyGnome data.")

top20_indie = df_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()
top20_nao = df_nao_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()
top20_indie['watch_time_hours'] = (top20_indie['watch_time_hours'] / 1_000_000).round(1)
top20_nao['watch_time_hours'] = (top20_nao['watch_time_hours'] / 1_000_000).round(1)

fig_comp = make_subplots(rows=2, cols=1,
    subplot_titles=('🎮 Top 20 Indie Games', '🏢 Top 20 Non-Indie Games'),
    vertical_spacing=0.1)

fig_comp.add_trace(go.Bar(
    x=top20_indie.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_indie.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#636EFA', name='Indie',
    text=top20_indie.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M hrs'),
    textposition='outside'), row=1, col=1)

fig_comp.add_trace(go.Bar(
    x=top20_nao.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_nao.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#EF553B', name='Non-Indie',
    text=top20_nao.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M hrs'),
    textposition='outside'), row=2, col=1)

fig_comp.update_layout(height=1100, showlegend=True)
fig_comp.update_xaxes(title_text='Watch Hours (Millions)', row=1, col=1)
fig_comp.update_xaxes(title_text='Watch Hours (Millions)', row=2, col=1)
st.plotly_chart(fig_comp, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 3: TIPO DE JOGO
# ============================================================
st.header("🕹️ Game Type vs Watch Hours (Indie Only)")

df_indie_tipos = df_indie[df_indie['tipo'] != 'Outro'].copy()
analise_tipo = df_indie_tipos.groupby('tipo').agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()

fig_tipo = px.bar(analise_tipo, x='tipo', y='media_watch_hours', color='tipo', text='qtd_jogos',
    labels={'media_watch_hours': 'Avg Watch Hours', 'tipo': 'Game Type'},
    color_discrete_sequence=px.colors.qualitative.Plotly)
fig_tipo.update_traces(texttemplate='%{text} games', textposition='outside')
fig_tipo.update_yaxes(tickformat='.2s')
st.plotly_chart(fig_tipo, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 4: FAIXA DE PREÇO
# ============================================================
st.header("💰 Price Range vs Twitch Popularity")

def faixa_preco(price):
    if pd.isna(price) or price == 0: return 'Free'
    elif price <= 20: return 'Up to $20'
    elif price <= 50: return 'Up to $50'
    else: return 'Above $50'

ordem = ['Free', 'Up to $20', 'Up to $50', 'Above $50']
col_preco1, col_preco2 = st.columns(2)

for df, label, col in [(df_indie, 'Indie', col_preco1), (df_nao_indie, 'Non-Indie', col_preco2)]:
    df_tmp = df.copy()
    df_tmp['faixa_preco'] = df_tmp['price'].apply(faixa_preco)
    analise = df_tmp.groupby('faixa_preco').agg(
        qtd_jogos=('name', 'count'),
        media_watch_hours=('watch_time_hours', 'mean'),
    ).round(0).reset_index()
    analise['faixa_preco'] = pd.Categorical(analise['faixa_preco'], categories=ordem, ordered=True)
    analise = analise.sort_values('faixa_preco')
    fig = px.bar(analise, x='faixa_preco', y='media_watch_hours', color='faixa_preco',
        text='qtd_jogos', title=f'{label} — Price Range vs Avg Watch Hours',
        labels={'faixa_preco': 'Price Range', 'media_watch_hours': 'Avg Watch Hours'})
    fig.update_traces(texttemplate='%{text} games', textposition='outside')
    fig.update_yaxes(tickformat='.2s')
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 5: TOP STREAMERS
# ============================================================
st.header("📡 Top 15 by Number of Streamers")

col_s1, col_s2 = st.columns(2)
for df, label, col in [(df_indie, 'Indie', col_s1), (df_nao_indie, 'Non-Indie', col_s2)]:
    top = df.nlargest(15, 'streamers')[['name', 'tipo', 'streamers']].copy()
    top['streamers'] = pd.to_numeric(top['streamers'], errors='coerce').fillna(0).astype(int)
    top = top.sort_values('streamers', ascending=True)
    fig = px.bar(top, x='streamers', y='name', color='tipo', orientation='h',
        title=f'{label} — Top 15 by Streamers',
        labels={'streamers': 'Number of Streamers', 'name': 'Game', 'tipo': 'Type'},
        text='streamers')
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    col.plotly_chart(fig, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 6: 2025 RELEASES VS ANTERIORES
# ============================================================
st.header("🚀 2025 Releases vs Prior Releases")

todos = pd.concat([df_indie, df_nao_indie])
todos['lancado_2025'] = todos['release_year'].apply(
    lambda x: '2025 Release' if x == 2025 else 'Prior to 2025')

analise_ano = todos.groupby(['lancado_2025', 'categoria']).agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()

fig_ano = px.bar(analise_ano, x='lancado_2025', y='media_watch_hours',
    color='categoria', barmode='group', text='qtd_jogos',
    title='2025 Releases vs Prior Releases — Avg Watch Hours on Twitch',
    labels={'lancado_2025': '', 'media_watch_hours': 'Avg Watch Hours', 'categoria': 'Category'},
    color_discrete_map={'Indie': '#636EFA', 'Não-Indie': '#EF553B'})
fig_ano.update_traces(texttemplate='%{text} games', textposition='outside')
fig_ano.update_yaxes(tickformat='.2s')
st.plotly_chart(fig_ano, use_container_width=True)

# Tabela de jogos 2025
st.subheader("🆕 2025 Game Releases in This Analysis")
col_2025a, col_2025b = st.columns(2)

for df, label, col in [(df_indie, 'Indie', col_2025a), (df_nao_indie, 'Non-Indie', col_2025b)]:
    jogos_2025 = df[df['release_year'] == 2025][['name', 'tipo', 'watch_time_hours']].copy()
    jogos_2025['watch_time_hours'] = (jogos_2025['watch_time_hours'] / 1_000_000).round(1)
    jogos_2025 = jogos_2025.sort_values('watch_time_hours', ascending=False)
    jogos_2025.columns = ['Game', 'Type', 'Watch Hours (M)']
    col.markdown(f"**{label} — {len(jogos_2025)} games**")
    col.dataframe(jogos_2025, use_container_width=True)

st.divider()

# ============================================================
# SEÇÃO 7: POSITIVE REVIEWS
# ============================================================
st.header("⭐ Positive Reviews vs Twitch Popularity (Indie)")

sem_review = df_indie[df_indie['pct_pos_total'].isna()][['name', 'watch_time_hours']].copy()
sem_review['watch_time_hours'] = (sem_review['watch_time_hours'] / 1_000_000).round(1)
sem_review = sem_review.sort_values('watch_time_hours', ascending=False)

if len(sem_review) > 0:
    jogos_sem_review = ', '.join(sem_review['name'].tolist())
    st.caption(f"⚠️ Games with no review data excluded from this chart (not sold on Steam or newly released): **{jogos_sem_review}**")

df_reviews = df_indie[df_indie['pct_pos_total'].notna() & (df_indie['pct_pos_total'] > 0)].copy()

def faixa_review(pct):
    if pct < 60: return 'Below 60%'
    elif pct < 70: return '60–70%'
    elif pct < 80: return '70–80%'
    elif pct < 90: return '80–90%'
    else: return '90–100%'

ordem_review = ['Below 60%', '60–70%', '70–80%', '80–90%', '90–100%']
df_reviews['faixa_review'] = df_reviews['pct_pos_total'].apply(faixa_review)
analise_review = df_reviews.groupby('faixa_review').agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
    media_streamers=('streamers', 'mean')
).round(0).reset_index()
analise_review['faixa_review'] = pd.Categorical(analise_review['faixa_review'], categories=ordem_review, ordered=True)
analise_review = analise_review.sort_values('faixa_review')

col_rev1, col_rev2 = st.columns(2)

fig_rev1 = px.bar(analise_review, x='faixa_review', y='media_watch_hours',
    color='faixa_review', text='qtd_jogos',
    title='Positive Review Range vs Avg Watch Hours',
    labels={'faixa_review': 'Positive Reviews', 'media_watch_hours': 'Avg Watch Hours'})
fig_rev1.update_traces(texttemplate='%{text} games', textposition='outside')
fig_rev1.update_yaxes(tickformat='.2s')
col_rev1.plotly_chart(fig_rev1, use_container_width=True)

fig_rev2 = px.bar(analise_review, x='faixa_review', y='media_streamers',
    color='faixa_review', text='qtd_jogos',
    title='Positive Review Range vs Avg Streamers',
    labels={'faixa_review': 'Positive Reviews', 'media_streamers': 'Avg Streamers'})
fig_rev2.update_traces(texttemplate='%{text} games', textposition='outside')
fig_rev2.update_yaxes(tickformat='.2s')
col_rev2.plotly_chart(fig_rev2, use_container_width=True)

# ============================================================
# SEÇÃO: STEAM COVERAGE ANALYSIS
# ============================================================
st.header("🗺️ Where Are These Games Distributed?")
st.caption("Analysis of the top 1000 most-watched games on Twitch in 2025 by distribution platform.")

disponibilidade = pd.read_csv("data/disponibilidade_steam.csv")
disponibilidade['label'] = disponibilidade['disponibilidade'].map({
    'On Steam': '🟢 On Steam',
    'Not on Steam': '🔴 Not on Steam',
    'Non-Game Content': '⬜ Non-Game Content',
    'Unknown': '⚪ Unclassified'
})

col_pie1, col_pie2 = st.columns([1, 1])

fig_pie = px.pie(
    disponibilidade,
    names='label',
    values='total_watch_hours',
    title='Watch Hours Distribution by Platform Availability',
    color='label',
    color_discrete_map={
        '🟢 On Steam': '#2ecc71',
        '🔴 Not on Steam': '#e74c3c',
        '⬜ Non-Game Content': '#95a5a6',
        '⚪ Unclassified': '#bdc3c7'
    },
    hole=0.4
)
fig_pie.update_traces(textposition='outside', textinfo='percent+label')
col_pie1.plotly_chart(fig_pie, use_container_width=True)

with col_pie2:
    st.markdown("### Key Findings")
    on_steam = disponibilidade[disponibilidade['disponibilidade'] == 'On Steam'].iloc[0]
    not_steam = disponibilidade[disponibilidade['disponibilidade'] == 'Not on Steam'].iloc[0]
    non_game = disponibilidade[disponibilidade['disponibilidade'] == 'Non-Game Content'].iloc[0]
    
    st.info(f"""
    **🟢 On Steam: {on_steam['pct_horas']:.1f}% of watch hours**
    
    {on_steam['qtd_jogos']} games available on Steam account for the majority of Twitch gaming content.
    """)
    st.error(f"""
    **🔴 Not on Steam: {not_steam['pct_horas']:.1f}% of watch hours**
    
    {not_steam['qtd_jogos']} major titles (League of Legends, Fortnite, VALORANT, all Nintendo games) 
    are distributed outside Steam — representing a significant blind spot in Steam-only analysis.
    """)
    st.warning(f"""
    **⬜ Non-Game Content: {non_game['pct_horas']:.1f}% of watch hours**
    
    Nearly 1 in 4 Twitch watch hours comes from non-gaming streams like Just Chatting, 
    IRL, Music and Talk Shows — showing Twitch is much more than a gaming platform.
    """)

st.divider()

# ============================================================
# SEÇÃO: VIEWERS VS STREAMERS — OPPORTUNITY INDEX
# ============================================================
st.header("🎯 Streaming Opportunity Index")
st.caption("Games with high viewers but few streamers = less competition for new content creators.")

df_opp = df_indie.copy()
df_opp['streamers'] = pd.to_numeric(df_opp['streamers'], errors='coerce')
df_opp['peak_viewers'] = pd.to_numeric(df_opp['peak_viewers'], errors='coerce')
df_opp = df_opp[df_opp['streamers'] > 100].copy()
df_opp['opportunity_ratio'] = (df_opp['peak_viewers'] / df_opp['streamers']).round(1)
df_opp = df_opp.nlargest(15, 'opportunity_ratio')[['name', 'tipo', 'opportunity_ratio', 'peak_viewers', 'streamers', 'watch_time_hours']].copy()
df_opp['watch_time_hours'] = (df_opp['watch_time_hours'] / 1_000_000).round(1)
df_opp = df_opp.sort_values('opportunity_ratio', ascending=True)

fig_opp = px.bar(
    df_opp,
    x='opportunity_ratio',
    y='name',
    color='tipo',
    orientation='h',
    title='Top 15 Indie Games — Viewers per Streamer Ratio (Higher = Less Competition)',
    labels={
        'opportunity_ratio': 'Viewers per Streamer',
        'name': 'Game',
        'tipo': 'Type'
    },
    text='opportunity_ratio'
)
fig_opp.update_traces(texttemplate='%{text:.0f}x', textposition='outside')
st.plotly_chart(fig_opp, use_container_width=True)

st.caption("💡 A high ratio means many viewers but few streamers — ideal for new creators looking for less saturated niches.")

st.divider()

# ============================================================
# SEÇÃO 8: TABELA EXPLORATÓRIA
# ============================================================
st.header("🔍 Explore the Data")

col_fil1, col_fil2 = st.columns(2)
tipo_filter = col_fil1.multiselect("Filter by Game Type",
    options=df_indie['tipo'].unique(), default=df_indie['tipo'].unique())
cat_filter = col_fil2.selectbox("Category", ['Indie', 'Non-Indie'])

df_base = df_indie if cat_filter == 'Indie' else df_nao_indie
colunas = ['name', 'tipo', 'price', 'watch_time_hours', 'peak_viewers', 'streamers', 'pct_pos_total', 'release_year']
df_filtrado = df_base[df_base['tipo'].isin(tipo_filter)][colunas].copy()
df_filtrado['watch_time_hours'] = (df_filtrado['watch_time_hours'] / 1_000_000).round(2)
df_filtrado = df_filtrado.sort_values('watch_time_hours', ascending=False)
df_filtrado.columns = ['Game', 'Type', 'Price ($)', 'Watch Hours (M)', 'Peak Viewers', 'Streamers', 'Positive Reviews (%)', 'Release Year']

st.dataframe(df_filtrado, use_container_width=True)

st.divider()
st.caption("Data sources: Steam API (March 2025) + SullyGnome Twitch Statistics (2025) | Built with Python, Pandas, Plotly & Streamlit")