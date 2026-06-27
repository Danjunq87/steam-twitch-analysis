import pandas as pd
from game_utils import limpar_nome, normalizar_nome_twitch

# Carrega dados
twitch_raw = pd.read_csv('data/sullygnome_top2000.csv')
indie = pd.read_csv('data/indie_final.csv')
nao_indie = pd.read_csv('data/naoindie_final.csv')

twitch = pd.DataFrame({
    'rank': twitch_raw['rank'],
    'game': twitch_raw['watch_time_hours'],
    'watch_time_hours': twitch_raw['stream_time_hours'],
})
twitch['game'] = twitch['game'].fillna('').apply(normalizar_nome_twitch)
twitch['game_lower'] = twitch['game'].apply(limpar_nome)
twitch['watch_time_hours'] = twitch['watch_time_hours'].str.replace(',', '').astype(float)
twitch = twitch.groupby('game', as_index=False).agg({
    'rank': 'min',
    'watch_time_hours': 'max',
    'game_lower': 'first',
})

# ============================================================
# CATEGORIAS DE NÃO-JOGOS
# ============================================================
nao_jogos = [
    'talk shows & podcasts', 'animals, aquariums, and zoos', 
    'pools, hot tubs, and beaches', 'co-working & studying',
    'rv there yet?', 'food & drink', 'makers & crafting',
    'science & technology', 'fitness & health', 'writing & reading',
    'lego & brickbuilding', 'miniatures & models', 'board games',
    'fright fest', "no, i'm not a human",
    'just chatting', 'always on', 'retro', 'irl', 'asmr', 'music', 'art',
    'sports', 'poker', 'slots', 'crypto', 'virtual casino', 'djs',
    'talk shows & podcasts', 'animals, aquariums, and zoos', 'games + demos',
    'streamer university', 'special events', 'kings league', 'la velada',
    'anime squad', 'the game awards', 'chess', 'pools, hot tubs, and beaches',
    'zevent', 'pokemon community game', "i'm only sleeping",
    'software and game development', 'co-working & studying', 'food & drink',
    'politics', 'fitness & health', 'writing & reading', 'miniatures & models',
    'science & technology', 'tabletop rpgs', 'makers & crafting', 'darts',
    'south park', 'el chavo', 'lego & brickbuilding', 'codenames',
    'stream for humanity', 'summer game fest', 'the streamer awards',
    'bdjovemaprendiz', 'tournament poker', 'streamer games', 'streamer university',
    'streamer university', 'words on stream', 'gartic phone', 'jackbox party packs',
    'dungeons & dragons', 'zlan', 'egging on', 'no, i\'m not a human',
    'casino jackpot', 'marvel contest of champions', 'fitness & health',
    'writing & reading', 'science & technology', 'tabletop rpgs',
    'baller league', 'rv there yet?', 'politics', 'active matter',
    'marvel strike force', 'kukoro: stream chat games','pokemon community game', 'pokemon trading card game', 'rise online',
    'ea sports college football 26', 'the simpsons: hit & run',
]

# ============================================================
# JOGOS FORA DA STEAM (Nintendo, Riot, Blizzard, etc)
# ============================================================
fora_steam_keywords = [
    'horizon forbidden west',
    'arena of valor', 'honor of kings', 'alliance of valiant arms',
    'just dance', 'pokedmmo', 'clone hero', 'age of mythology',
    'game of thrones: kingsroad', 'heroes of newerth',
    'ninja gaiden 4', 'final fantasy vii remake',
    'osu!', 'star wars battlefront', 'nhl 25', 'the sims 2', 'clubhouse games',
    'talk shows & podcasts', 'animals, aquariums, and zoos', 'pools, hot tubs, and beaches',
    'co-working & studying', 'rv there yet?', 'food & drink', 'makers & crafting',
    'science & technology', 'fitness & health', 'writing & reading', 'lego & brickbuilding',
    'miniatures & models', 'warhammer', 'casino', 'mystery science theater 3000',
    'dream con', "no, i'm not a human", 'dungeons & dragons', 'mamon king',
    'shine post: be your idol!', 'baller league',
    'megabonk', 'ghost of tsushima', 'grand theft auto iv', 'metal gear solid 3',
    'metal gear solid ?:', 'monster hunter freedom', 'gears of war',
    'dragon quest', 'lego party', 'shine post', 'chrono odyssey',
    'south of midnight', 'neighbors: suburban warfare',
    'star citizen', 'ghost of yotei', 'ghost of yo', 'gran turismo',
    'stellar blade', 'metal gear solid delta', 'metal gear solid ?:',
    'persona 5', 'age of empires iv',
    'arena breakout', 'tibia', 'heroes of the storm', '2xko', 'bloodborne',
    'ghost of yotei', 'standoff 2', 'pokemon go', 'osu!', 'age of empires iv',
    'f1 25', 'ea sports college football', 'marathon', 'black russia',
    'mir korabley', 'stalzone', 'kagome', 'kagome 2', 'kagome 3', 'kagome 4', 'kagome 5', 'kagome 6', 'kagome 7', 'kagome 8', 'kagome 9', 'kagome 10',
    'pokemon', 'pokémon', 'mario', 'zelda', 'splatoon', 'smash bros', 'donkey kong',
    'animal crossing', 'metroid', 'fire emblem', 'kirby', 'xenoblade',
    'league of legends', 'valorant', 'teamfight tactics', 'wild rift',
    'hearthstone', 'overwatch', 'warcraft', 'starcraft', 'diablo',
    'call of duty', 'warzone', 'fortnite', 'apex legends', 'rocket league',
    'clash royale', 'clash of clans', 'brawl stars', 'mobile legends',
    'free fire', 'pubg mobile', 'pokemon go', 'genshin impact',
    'honkai', 'wuthering waves', 'zenless zone zero', 'infinity nikki',
    'goddess of victory', 'blue protocol', 'umamusume', 'epic seven',
    'summoners war', 'crystal of atlan', 'mir ', 'lineage', 'aion',
    'mu online', 'mir4', 'knight online', 'ragnarok', 'metin2',
    'dragon ball', 'inazuma eleven', 'digimon', 'yu-gi-oh',
    'final fantasy tactics', 'mario kart world','grand theft auto v', 'grand theft auto: san andreas', 'grand theft auto: vice city',
    'grand theft auto iv', 'roblox', 'sea of thieves', 'battlefield redsec',
    'mlb the show', 'madden nfl', 'nba 2k2', 'borderlands 4', 'silent hill f',
    'maplestory worlds', 'stalzone', 'dispatch', 'off the grid',
    'rematch', 'mecha break', 'age of empires iv','silent hill f', 'grounded 2', 'little nightmares iii', 'wwe 2k25',
    'the last of us', 'football manager 26', 'europa universalis v','europa universalis iv', 'europa universalis iii', 'europa universalis ii', 'europa universalis',
]

def classificar_disponibilidade(game_lower, jogos_steam):
    if game_lower in nao_jogos:
        return 'Non-Game Content'
    if game_lower in jogos_steam:
        return 'On Steam'
    for kw in fora_steam_keywords:
        if kw in game_lower:
            return 'Not on Steam'
    return 'Unknown'

jogos_steam = list(indie['name'].apply(limpar_nome)) + list(nao_indie['name'].apply(limpar_nome))
twitch['disponibilidade'] = twitch['game_lower'].apply(
    lambda x: classificar_disponibilidade(x, jogos_steam))

# ============================================================
# ANÁLISE POR DISPONIBILIDADE
# ============================================================
analise = twitch.groupby('disponibilidade').agg(
    qtd_jogos=('game', 'count'),
    total_watch_hours=('watch_time_hours', 'sum')
).reset_index()
analise['total_watch_hours_bi'] = (analise['total_watch_hours'] / 1_000_000_000).round(2)
analise['pct_horas'] = (analise['total_watch_hours'] / analise['total_watch_hours'].sum() * 100).round(1)

print("=== DISTRIBUIÇÃO POR DISPONIBILIDADE (Top 1000 SullyGnome) ===")
print(analise[['disponibilidade', 'qtd_jogos', 'total_watch_hours_bi', 'pct_horas']].to_string(index=False))

# Salva para o dashboard
analise.to_csv('data/disponibilidade_steam.csv', index=False)

# ============================================================
# LISTA DE UNKNOWN PARA REVISÃO MANUAL
# ============================================================
unknown = twitch[twitch['disponibilidade'] == 'Unknown'].sort_values('watch_time_hours', ascending=False)
print(f"\n=== JOGOS UNKNOWN PARA REVISÃO: {len(unknown)} ===")
print(unknown[['rank', 'game', 'watch_time_hours', 'disponibilidade']].head(50).to_string(index=False))
unknown.to_csv('data/jogos_unknown.csv', index=False)
print("\nSalvo em data/jogos_unknown.csv")

# Substitui o bloco fuzzy por este mais rápido
from rapidfuzz import process, fuzz

steam = pd.read_csv('data/games_march2025_cleaned.csv')
# Usa só os 20k jogos mais populares para acelerar
steam_top = steam.nlargest(20000, 'recommendations') if 'recommendations' in steam.columns else steam.head(20000)
steam_names = steam_top['name'].str.lower().str.strip().tolist()

unknown_games = twitch[twitch['disponibilidade'] == 'Unknown'].copy()
# Processa só os top 100 unknown por horas assistidas
unknown_top = unknown_games.nlargest(100, 'watch_time_hours')

resultados = []
for _, row in unknown_top.iterrows():
    match = process.extractOne(
        row['game_lower'],
        steam_names,
        scorer=fuzz.ratio,
        score_cutoff=85
    )
    if match:
        resultados.append({
            'twitch_name': row['game'],
            'steam_match': match[0],
            'score': match[1],
            'watch_time_hours': row['watch_time_hours'],
            'rank': row['rank']
        })

df_matches = pd.DataFrame(resultados).sort_values('watch_time_hours', ascending=False)
print(f"\n=== JOGOS UNKNOWN COM MATCH NA STEAM: {len(df_matches)} ===")
print(df_matches.to_string(index=False))
df_matches.to_csv('data/jogos_fuzzy_matches.csv', index=False)
print("\nSalvo em data/jogos_fuzzy_matches.csv")