import pandas as pd
import ast
import re
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# 1. CARREGA OS DADOS
# ============================================================
steam = pd.read_csv("data/games_march2025_cleaned.csv")
twitch_raw = pd.read_csv("data/sullygnome_top2000.csv")

# Corrige alinhamento das colunas da Twitch
twitch = pd.DataFrame({
    'rank': twitch_raw['rank'],
    'game': twitch_raw['watch_time_hours'],
    'watch_time_hours': twitch_raw['stream_time_hours'],
    'stream_time_hours': twitch_raw['peak_viewers'],
    'peak_viewers': twitch_raw['peak_channels'],
    'peak_channels': twitch_raw['streamers'],
    'streamers': twitch_raw['avg_viewers'],
})

print(f"Steam: {steam.shape[0]} jogos")
print(f"Twitch: {twitch.shape[0]} jogos")
print(twitch.head(3))

# ============================================================
# 2. CLASSIFICA TIPO E INDIE
# ============================================================
def parse_field(value):
    try:
        return ast.literal_eval(value)
    except:
        return []

def classificar_tipo(categories_str, tags_str):
    cats = parse_field(categories_str) if pd.notna(categories_str) else []
    tags = parse_field(tags_str) if pd.notna(tags_str) else {}
    combinado = ' '.join(cats).lower() + ' ' + ' '.join(tags.keys()).lower() if isinstance(tags, dict) else ''
    if 'massively multiplayer' in combinado or 'mmo' in combinado:
        return 'MMO'
    elif 'multi-player' in combinado or 'multiplayer' in combinado or 'co-op' in combinado:
        return 'Multiplayer'
    elif 'single-player' in combinado or 'singleplayer' in combinado:
        return 'Single Player'
    else:
        return 'Outro'

def is_indie(genres_str):
    genres = parse_field(genres_str) if pd.notna(genres_str) else []
    return 'Indie' in genres

steam['tipo'] = steam.apply(lambda row: classificar_tipo(row['categories'], row['tags']), axis=1)
steam['indie'] = steam['genres'].apply(is_indie)

print("\nTipos:")
print(steam['tipo'].value_counts())
print(f"\nIndies: {steam['indie'].sum()}")

# ============================================================
# 3. CRUZA STEAM COM TWITCH
# ============================================================
nao_jogos = ['just chatting', 'always on', 'retro', 'irl', 'asmr',
             'music', 'art', 'sports', 'chess', 'poker', 'slots',
             'crypto', 'virtual casino', 'djs', 'talk shows & podcasts',
             'animals, aquariums, and zoos', 'games + demos', 'streamer university']

# Normaliza nomes
steam['name_lower'] = steam['name'].str.lower().str.strip()
twitch['game_lower'] = twitch['game'].fillna('').str.lower().str.strip()

# Merge geral
merged_all = steam.merge(twitch, left_on='name_lower', right_on='game_lower', how='inner')

# Remove não-jogos
merged_all = merged_all[~merged_all['name_lower'].isin(nao_jogos)].copy()

# Limpa números
for col in ['watch_time_hours', 'peak_viewers', 'peak_channels', 'streamers']:
    merged_all[col] = merged_all[col].str.replace(',', '').astype(float)

# Jogos indie sem tag que precisam ser corrigidos manualmente
indie_manual = ['among us', 'bloons td 6', 'r.e.p.o.']
merged_all.loc[merged_all['name_lower'].isin(indie_manual), 'indie'] = True

# Remove duplicata do Among Us (mantém o maior)
merged_all = merged_all.sort_values('watch_time_hours', ascending=False)
merged_all = merged_all.drop_duplicates(subset='name', keep='first')

# Corrige Peak para Multiplayer (jogo co-op de escalada)
merged_all.loc[merged_all['name'] == 'Peak', 'tipo'] = 'Multiplayer'

print(f"Após deduplicação: {len(merged_all)} jogos")
# Separa indie e não-indie
df_indie = merged_all[merged_all['indie']].copy()
df_nao_indie = merged_all[~merged_all['indie']].copy()

df_indie['categoria'] = 'Indie'
df_nao_indie['categoria'] = 'Não-Indie'

print(f"\nIndie na Twitch: {len(df_indie)}")
print(f"Não-Indie na Twitch: {len(df_nao_indie)}")

# Verifica jogos corrigidos
print("\nJogos corrigidos manualmente:")
print(merged_all[merged_all['name_lower'].isin(indie_manual)][['name', 'indie', 'watch_time_hours']])

# ============================================================
# 4. ANÁLISES E GRÁFICOS
# ============================================================

# --- Gráfico 1: Tipo de jogo vs horas assistidas ---
analise_tipo = df_indie.groupby('tipo').agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()

fig1 = px.bar(
    analise_tipo, x='tipo', y='media_watch_hours', color='tipo', text='qtd_jogos',
    title='Média de Horas Assistidas na Twitch por Tipo de Jogo Indie (2025)',
    labels={'media_watch_hours': 'Média de Horas Assistidas (Mi)', 'tipo': 'Tipo de Jogo'}
)
fig1.update_traces(texttemplate='%{text} jogos', textposition='outside')
fig1.update_yaxes(tickvals=[0,10000000,20000000,30000000,40000000,50000000,60000000],
                  ticktext=['0','10Mi','20Mi','30Mi','40Mi','50Mi','60Mi'])
fig1.write_html("assets/grafico_tipo.html")
print("Gráfico 1 salvo!")

# --- Gráfico 2: Faixa de preço ---
def faixa_preco(price):
    if price == 0: return 'Gratuito'
    elif price <= 10: return 'Até $10'
    elif price <= 20: return 'Até $20'
    elif price <= 30: return 'Até $30'
    else: return 'Acima de $30'

df_indie['faixa_preco'] = df_indie['price'].apply(faixa_preco)
analise_preco = df_indie.groupby('faixa_preco').agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()
ordem = ['Gratuito', 'Até $10', 'Até $20', 'Até $30', 'Acima de $30']
analise_preco['faixa_preco'] = pd.Categorical(analise_preco['faixa_preco'], categories=ordem, ordered=True)
analise_preco = analise_preco.sort_values('faixa_preco')

fig2 = px.bar(
    analise_preco, x='faixa_preco', y='media_watch_hours', color='faixa_preco', text='qtd_jogos',
    title='Faixa de Preço vs Média de Horas Assistidas na Twitch — Jogos Indie (2025)',
    labels={'faixa_preco': 'Faixa de Preço', 'media_watch_hours': 'Média de Horas Assistidas'}
)
fig2.update_traces(texttemplate='%{text} jogos', textposition='outside')
fig2.update_yaxes(tickformat='.0s')
fig2.write_html("assets/grafico_preco_faixas.html")
print("Gráfico 2 salvo!")

# --- Gráfico 3: Top 15 streamers ---
top_streamers = df_indie.nlargest(15, 'streamers')[['name', 'tipo', 'streamers']].copy()
top_streamers['streamers'] = top_streamers['streamers'].astype(int)

fig3 = px.bar(
    top_streamers, x='streamers', y='name', color='tipo', orientation='h',
    title='Top 15 Jogos Indie com Mais Streamers na Twitch (2025)',
    labels={'streamers': 'Número de Streamers', 'name': 'Jogo', 'tipo': 'Tipo'},
    text='streamers'
)
fig3.update_traces(texttemplate='%{text:,}', textposition='outside')
fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
fig3.write_html("assets/grafico_streamers.html")
print("Gráfico 3 salvo!")

# --- Gráfico 4: Indie vs Não-Indie ---
top20_indie = df_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours', 'categoria']].copy()
top20_nao = df_nao_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours', 'categoria']].copy()
top20_indie['watch_time_hours'] = (top20_indie['watch_time_hours'] / 1_000_000).round(1)
top20_nao['watch_time_hours'] = (top20_nao['watch_time_hours'] / 1_000_000).round(1)
top20_indie_sorted = top20_indie.sort_values('watch_time_hours', ascending=True)
top20_nao_sorted = top20_nao.sort_values('watch_time_hours', ascending=True)

fig4 = make_subplots(rows=2, cols=1,
    subplot_titles=('🎮 Top 20 Jogos Indie', '🏢 Top 20 Jogos Não-Indie'),
    vertical_spacing=0.12)
fig4.add_trace(go.Bar(
    x=top20_indie_sorted['watch_time_hours'], y=top20_indie_sorted['name'],
    orientation='h', marker_color='#636EFA', name='Indie',
    text=top20_indie_sorted['watch_time_hours'].apply(lambda x: f'{x:.0f}Mi'),
    textposition='outside'), row=1, col=1)
fig4.add_trace(go.Bar(
    x=top20_nao_sorted['watch_time_hours'], y=top20_nao_sorted['name'],
    orientation='h', marker_color='#EF553B', name='Não-Indie',
    text=top20_nao_sorted['watch_time_hours'].apply(lambda x: f'{x:.0f}Mi'),
    textposition='outside'), row=2, col=1)
fig4.update_layout(title='Top 20 Indie vs Não-Indie — Horas Assistidas na Twitch (2025)', height=1000)
fig4.write_html("assets/grafico_comparacao_final.html")
print("Gráfico 4 salvo!")

# ============================================================
# 5. RESUMO FINAL
# ============================================================
total_indie = df_indie['watch_time_hours'].sum()
total_nao_indie = df_nao_indie['watch_time_hours'].sum()
total_geral = total_indie + total_nao_indie

print("\n========== RESUMO ==========")
print(f"Jogos Indie analisados: {len(df_indie)}")
print(f"Jogos Não-Indie analisados: {len(df_nao_indie)}")
print(f"% Indie do total de horas: {total_indie/total_geral*100:.1f}%")
print(f"% Não-Indie do total de horas: {total_nao_indie/total_geral*100:.1f}%")
print("\nTop 5 Indie:")
print(df_indie.nlargest(5, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].to_string(index=False))

# Salva datasets finais
df_indie.to_csv("data/indie_final.csv", index=False)
df_nao_indie.to_csv("data/naoindie_final.csv", index=False)
print("\nDatasets salvos!")