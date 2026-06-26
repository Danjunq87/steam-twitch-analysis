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

print(f"Indies: {steam['indie'].sum()}")

# ============================================================
# 3. CRUZA STEAM COM TWITCH
# ============================================================
nao_jogos = ['just chatting', 'always on', 'retro', 'irl', 'asmr',
             'music', 'art', 'sports', 'chess', 'poker', 'slots',
             'crypto', 'virtual casino', 'djs', 'talk shows & podcasts',
             'animals, aquariums, and zoos', 'games + demos', 'streamer university',
             'special events', 'kings league', 'la velada', 'anime squad',
             'always on', 'stream university', 'the game awards']

import re

def limpar_nome(nome):
    if pd.isna(nome):
        return ''
    nome = re.sub(r'[™®©ƒ]', '', nome)
    # Converte romanos comuns para números
    nome = re.sub(r'\bII\b', '2', nome)
    nome = re.sub(r'\bIII\b', '3', nome)
    nome = re.sub(r'\bIV\b', '4', nome)
    nome = re.sub(r'\bVI\b', '6', nome)
    nome = re.sub(r'\bVII\b', '7', nome)
    nome = re.sub(r'\bVIII\b', '8', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome.lower()

steam['name_lower'] = steam['name'].apply(limpar_nome)
twitch['game_lower'] = twitch['game'].fillna('').apply(limpar_nome)

merged_all = steam.merge(twitch, left_on='name_lower', right_on='game_lower', how='inner')
merged_all = merged_all[~merged_all['name_lower'].isin(nao_jogos)].copy()

# Limpa números
for col in ['watch_time_hours', 'peak_viewers', 'peak_channels', 'streamers']:
    merged_all[col] = merged_all[col].str.replace(',', '').astype(float)

# Correções manuais de indie
indie_manual = ['among us', 'bloons td 6', 'r.e.p.o.']
merged_all.loc[merged_all['name_lower'].isin(indie_manual), 'indie'] = True

# Move Rocket League para não-indie (adquirido pela Epic)
merged_all.loc[merged_all['name_lower'].str.contains('rocket league', na=False), 'indie'] = False

# Move Fall Guys para não-indie (adquirido pela Epic)
merged_all.loc[merged_all['name_lower'] == 'fall guys', 'indie'] = False

# Correções de tipo
merged_all.loc[merged_all['name'] == 'Peak', 'tipo'] = 'Multiplayer'
merged_all.loc[merged_all['name'] == 'Marvel Rivals', 'tipo'] = 'Multiplayer'

correcoes_tipo = {
    'Palia': 'MMO',
    'Perfect World': 'MMO',
    'Sky: Children of the Light': 'MMO',
    'Fear & Hunger 2: Termina': 'Single Player',
    'Goose Goose Duck': 'Multiplayer',
    'ORDER 13': 'Multiplayer',
    'Artifact': 'Multiplayer',
    'Supermarket Together': 'Multiplayer',
}
for jogo, tipo in correcoes_tipo.items():
    merged_all.loc[merged_all['name'] == jogo, 'tipo'] = tipo

# Correções MMO -> Multiplayer
falsos_mmo = [
    'Rust', 'Path of Exile', 'ARK: Survival Ascended', 'ARK: Survival Evolved',
    'Last Epoch', 'The Isle', 'SCUM', 'Raft', 'Golf With Your Friends',
    'Hell Let Loose', 'Stumble Guys', 'Squad', 'Deadside',
    'Kukoro: Stream chat games'
]
merged_all.loc[merged_all['name'].isin(falsos_mmo), 'tipo'] = 'Multiplayer'

# Correções MMO -> Multiplayer nos não-indie
falsos_mmo_nao_indie = [
    'Path of Exile 2', 'DayZ', 'VRChat', 'Warframe',
    'Marbles on Stream', 'War Thunder', 'World of Warships',
    'iRacing', 'SMITE 2', 'Fall Guys', 'NARAKA: BLADEPOINT',
    'Gray Zone Warfare', 'Russian Fishing 4', 'V Rising',
    'Conan Exiles', 'CarX Drift Racing Online', 'Crossout', 'Fallout 76'
]
merged_all.loc[merged_all['name'].isin(falsos_mmo_nao_indie), 'tipo'] = 'Multiplayer'

# Deduplicação
merged_all = merged_all.sort_values('watch_time_hours', ascending=False)
merged_all = merged_all.drop_duplicates(subset='name', keep='first')

print(f"Após deduplicação: {len(merged_all)} jogos")

# ============================================================
# 4. ADICIONA JOGOS NÃO DISPONÍVEIS NA STEAM
# ============================================================
jogos_faltando = [
    {'name': "Tom Clancy's The Division 2", 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2019-03-15'},
    {'name': 'The Elder Scrolls Online', 'tipo': 'MMO', 'indie': False, 'price': 0.0, 'release_date': '2014-04-04'},
    {'name': 'Call of Duty: Warzone', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2020-03-10'},
    {'name': 'Call of Duty: Black Ops 6', 'tipo': 'Multiplayer', 'indie': False, 'price': 69.99, 'release_date': '2024-10-25'},
    {'name': 'Call of Duty: Black Ops 7', 'tipo': 'Multiplayer', 'indie': False, 'price': 69.99, 'release_date': '2025-10-31'},
    {'name': 'League of Legends', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2009-10-27'},
    {'name': 'VALORANT', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2020-06-02'},
    {'name': 'Fortnite', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2017-07-25'},
    {'name': 'Minecraft', 'tipo': 'Multiplayer', 'indie': False, 'price': 26.95, 'release_date': '2011-11-18'},
    {'name': 'World of Warcraft', 'tipo': 'MMO', 'indie': False, 'price': 0.0, 'release_date': '2004-11-23'},
    {'name': 'Counter-Strike', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2012-08-21'},
    {'name': 'Escape from Tarkov', 'tipo': 'Multiplayer', 'indie': False, 'price': 44.99, 'release_date': '2016-08-04'},
    {'name': 'Apex Legends', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2019-02-04'},
    {'name': 'Overwatch', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2016-05-24'},
    {'name': 'Teamfight Tactics', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2019-06-26'},
    {'name': 'Rainbow Six Siege', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2015-12-01'},
    {'name': 'Hearthstone', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2014-03-11'},
    {'name': 'Rocket League', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2015-07-07'},
    {'name': 'EA Sports FC 25', 'tipo': 'Multiplayer', 'indie': False, 'price': 69.99, 'release_date': '2024-09-27'},
    {'name': 'EA Sports FC 26', 'tipo': 'Multiplayer', 'indie': False, 'price': 69.99, 'release_date': '2025-09-26'},
    {'name': 'Street Fighter 6', 'tipo': 'Multiplayer', 'indie': False, 'price': 59.99, 'release_date': '2023-06-02'},
    {'name': 'ARC Raiders', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2025-05-22'},
    {'name': 'Battlefield 6', 'tipo': 'Multiplayer', 'indie': False, 'price': 0.0, 'release_date': '2025-06-05'},
]

twitch_completo = pd.DataFrame({
    'game': twitch_raw['watch_time_hours'],
    'watch_time_hours': twitch_raw['stream_time_hours'],
    'peak_viewers': twitch_raw['peak_channels'],
    'streamers': twitch_raw['avg_viewers'],
})

for jogo in jogos_faltando:
    twitch_row = twitch_completo[twitch_completo['game'] == jogo['name']]
    if len(twitch_row) > 0:
        row = twitch_row.iloc[0]
        jogo['watch_time_hours'] = float(str(row['watch_time_hours']).replace(',', ''))
        jogo['peak_viewers'] = float(str(row['peak_viewers']).replace(',', ''))
        jogo['streamers'] = float(str(row['streamers']).replace(',', ''))
        jogo['pct_pos_total'] = None
        jogo['estimated_owners'] = None
        jogo['metacritic_score'] = None
        jogo['peak_ccu'] = None
        jogo['positive'] = None
        jogo['negative'] = None
        jogo['categoria'] = 'Não-Indie'

df_extras = pd.DataFrame([j for j in jogos_faltando if 'watch_time_hours' in j])
print(f"Jogos extras adicionados: {len(df_extras)}")

merged_all = pd.concat([merged_all, df_extras], ignore_index=True)

# ============================================================
# 5. SEPARA INDIE E NÃO-INDIE
# ============================================================
df_indie = merged_all[merged_all['indie'] == True].copy()
df_nao_indie = merged_all[merged_all['indie'] == False].copy()

df_indie['categoria'] = 'Indie'
df_nao_indie['categoria'] = 'Não-Indie'

# Trata reviews inválidos
df_indie['pct_pos_total'] = pd.to_numeric(df_indie['pct_pos_total'], errors='coerce')
df_indie.loc[df_indie['pct_pos_total'] == -1, 'pct_pos_total'] = None

# Extrai ano de lançamento
df_indie['release_year'] = pd.to_datetime(df_indie['release_date'], errors='coerce').dt.year
df_nao_indie['release_year'] = pd.to_datetime(df_nao_indie['release_date'], errors='coerce').dt.year

print(f"\nIndie na Twitch: {len(df_indie)}")
print(f"Não-Indie na Twitch: {len(df_nao_indie)}")

total_indie = df_indie['watch_time_hours'].sum()
total_nao_indie = df_nao_indie['watch_time_hours'].sum()
total_geral = total_indie + total_nao_indie
print(f"% Indie: {total_indie/total_geral*100:.1f}%")
print(f"% Não-Indie: {total_nao_indie/total_geral*100:.1f}%")

# ============================================================
# 6. SALVA DATASETS
# ============================================================
df_indie.to_csv("data/indie_final.csv", index=False)
df_nao_indie.to_csv("data/naoindie_final.csv", index=False)
print("\nDatasets salvos!")

# ============================================================
# 7. GRÁFICOS
# ============================================================

# Gráfico 1: Indie vs Não-Indie
top20_indie = df_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()
top20_nao = df_nao_indie.nlargest(20, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours']].copy()
top20_indie['watch_time_hours'] = (top20_indie['watch_time_hours'] / 1_000_000).round(1)
top20_nao['watch_time_hours'] = (top20_nao['watch_time_hours'] / 1_000_000).round(1)

fig1 = make_subplots(rows=2, cols=1,
    subplot_titles=('🎮 Top 20 Indie Games', '🏢 Top 20 Non-Indie Games'),
    vertical_spacing=0.12)
fig1.add_trace(go.Bar(
    x=top20_indie.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_indie.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#636EFA', name='Indie',
    text=top20_indie.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M hrs'),
    textposition='outside'), row=1, col=1)
fig1.add_trace(go.Bar(
    x=top20_nao.sort_values('watch_time_hours')['watch_time_hours'],
    y=top20_nao.sort_values('watch_time_hours')['name'],
    orientation='h', marker_color='#EF553B', name='Non-Indie',
    text=top20_nao.sort_values('watch_time_hours')['watch_time_hours'].apply(lambda x: f'{x:.0f}M hrs'),
    textposition='outside'), row=2, col=1)
fig1.update_layout(height=1100, showlegend=True)
fig1.write_html("assets/grafico_comparacao_final.html")
print("Gráfico 1 salvo!")

# Gráfico 2: Tipo de jogo
df_indie_tipos = df_indie[df_indie['tipo'] != 'Outro'].copy()
analise_tipo = df_indie_tipos.groupby('tipo').agg(
    qtd_jogos=('name', 'count'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()
fig2 = px.bar(analise_tipo, x='tipo', y='media_watch_hours', color='tipo', text='qtd_jogos',
    labels={'media_watch_hours': 'Avg Watch Hours', 'tipo': 'Game Type'})
fig2.update_traces(texttemplate='%{text} games', textposition='outside')
fig2.update_yaxes(tickformat='.2s')
fig2.write_html("assets/grafico_tipo.html")
print("Gráfico 2 salvo!")

# Gráfico 3: Faixa de preço
def faixa_preco(price):
    if pd.isna(price) or price == 0: return 'Free'
    elif price <= 20: return 'Up to $20'
    elif price <= 50: return 'Up to $50'
    else: return 'Above $50'

ordem = ['Free', 'Up to $20', 'Up to $50', 'Above $50']

for df, label, fname in [
    (df_indie, 'Indie', 'assets/grafico_preco_indie.html'),
    (df_nao_indie, 'Non-Indie', 'assets/grafico_preco_naoindie.html')
]:
    df = df.copy()
    df['faixa_preco'] = df['price'].apply(faixa_preco)
    analise = df.groupby('faixa_preco').agg(
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
    fig.write_html(fname)
print("Gráfico 3 salvo!")

# Gráfico 4: Streamers
for df, label, fname in [
    (df_indie, 'Indie', 'assets/grafico_streamers_indie.html'),
    (df_nao_indie, 'Non-Indie', 'assets/grafico_streamers_naoindie.html')
]:
    top = df.nlargest(15, 'streamers')[['name', 'tipo', 'streamers']].copy()
    top['streamers'] = pd.to_numeric(top['streamers'], errors='coerce').fillna(0).astype(int)
    top = top.sort_values('streamers', ascending=True)
    fig = px.bar(top, x='streamers', y='name', color='tipo', orientation='h',
        title=f'{label} — Top 15 by Streamers',
        labels={'streamers': 'Number of Streamers', 'name': 'Game', 'tipo': 'Type'},
        text='streamers')
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig.write_html(fname)
print("Gráfico 4 salvo!")

# Gráfico 5: Jogos 2025 vs anteriores
todos = pd.concat([df_indie, df_nao_indie])
todos['lancado_2025'] = todos['release_year'].apply(lambda x: '2025 Release' if x == 2025 else 'Prior to 2025')
analise_ano = todos.groupby(['lancado_2025', 'categoria']).agg(
    qtd_jogos=('name', 'count'),
    total_watch_hours=('watch_time_hours', 'sum'),
    media_watch_hours=('watch_time_hours', 'mean'),
).round(0).reset_index()
fig5 = px.bar(analise_ano, x='lancado_2025', y='media_watch_hours',
    color='categoria', barmode='group',
    text='qtd_jogos',
    title='2025 Releases vs Prior Releases — Avg Watch Hours on Twitch',
    labels={'lancado_2025': 'Release Year', 'media_watch_hours': 'Avg Watch Hours', 'categoria': 'Category'})
fig5.update_traces(texttemplate='%{text} games', textposition='outside')
fig5.update_yaxes(tickformat='.2s')
fig5.write_html("assets/grafico_2025_vs_anteriores.html")
print("Gráfico 5 salvo!")

print("\n✅ Todos os gráficos salvos!")
print(f"\nTop 5 Indie:")
print(df_indie.nlargest(5, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours', 'release_year']].to_string(index=False))
print(f"\nTop 5 Não-Indie:")
print(df_nao_indie.nlargest(5, 'watch_time_hours')[['name', 'tipo', 'watch_time_hours', 'release_year']].to_string(index=False))