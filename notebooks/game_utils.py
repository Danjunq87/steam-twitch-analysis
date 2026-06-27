"""Utilitários compartilhados para cruzar nomes SullyGnome ↔ Steam."""
import re
import unicodedata


def limpar_nome(nome):
    """Normaliza nomes para comparação (remove acentos, símbolos especiais, romanos)."""
    if nome is None or (isinstance(nome, float) and nome != nome):
        return ''
    nome = unicodedata.normalize('NFKD', str(nome))
    nome = ''.join(c for c in nome if not unicodedata.combining(c))
    nome = re.sub(r'[™®©ƒΔδ•·]', '', nome)
    nome = re.sub(r'\bII\b', '2', nome)
    nome = re.sub(r'\bIII\b', '3', nome)
    nome = re.sub(r'\bIV\b', '4', nome)
    nome = re.sub(r'\bVI\b', '6', nome)
    nome = re.sub(r'\bVII\b', '7', nome)
    nome = re.sub(r'\bVIII\b', '8', nome)
    nome = re.sub(r'[^\w\s:.\'+\-]', ' ', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome.lower()


# Variantes do SullyGnome → nome canônico (mesmo jogo, grafia diferente)
ALIASES_TWITCH = {
    'METAL GEAR SOLID Δ: SNAKE EATER': 'Metal Gear Solid Delta: Snake Eater',
    'SILENT HILL ƒ': 'Silent Hill f',
    'Ghost of Yōtei': 'Ghost of Yotei',
    'HλLF-LIFE²': 'Half-Life 2',
    'TORMENTED SOULS II': 'Tormented Souls 2',
    'Tomb Raider I•II•III Remastered': 'Tomb Raider I-III Remastered',
    'TV Station Manager': 'Station Manager',
    'Car Dealer Simulator': 'Car Dealership Simulator',
    'Planet Crafter': 'The Planet Crafter',
    'Age of Empires IV': 'Age of Empires IV: Anniversary Edition',
    'Death Stranding': "DEATH STRANDING DIRECTOR'S CUT",
}

# Nome Twitch (canônico) → nome exato na Steam (quando limpar_nome não basta)
MAPEAMENTO_STEAM = {
    'age of empires iv: anniversary edition': 'Age of Empires IV: Anniversary Edition',
    "death stranding director's cut": "DEATH STRANDING DIRECTOR'S CUT",
    'station manager': 'Station Manager',
    'car dealership simulator': 'Car Dealership Simulator',
    'the planet crafter': 'The Planet Crafter',
}


def normalizar_nome_twitch(nome):
    """Aplica alias conhecido; mantém o original se não houver mapeamento."""
    if nome in ALIASES_TWITCH:
        return ALIASES_TWITCH[nome]
    return nome


def buscar_linha_twitch(twitch_df, nome):
    """Busca dados Twitch pelo nome exato, alias ou limpar_nome."""
    if nome in twitch_df['game'].values:
        return twitch_df[twitch_df['game'] == nome].iloc[0]

    alias = ALIASES_TWITCH.get(nome)
    if alias and alias in twitch_df['game'].values:
        return twitch_df[twitch_df['game'] == alias].iloc[0]

    nome_limpo = limpar_nome(nome)
    for g in twitch_df['game'].dropna().unique():
        if limpar_nome(g) == nome_limpo:
            return twitch_df[twitch_df['game'] == g].iloc[0]

    return None
