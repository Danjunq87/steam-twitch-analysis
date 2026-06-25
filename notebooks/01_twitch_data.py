import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega as chaves do .env
load_dotenv()
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# Gera token de acesso
def get_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    return response.json()["access_token"]

# Pega os jogos mais assistidos
def get_top_games(token, limit=100):
    url = "https://api.twitch.tv/helix/games/top"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    games = []
    params = {"first": 100}
    
    while len(games) < limit:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        games.extend(data["data"])
        
        if "cursor" not in data.get("pagination", {}):
            break
        params["after"] = data["pagination"]["cursor"]
    
    return games[:limit]

# Executa
token = get_token()
print("Token gerado com sucesso!")

games = get_top_games(token, limit=500)
df = pd.DataFrame(games)
print(f"Total de jogos puxados: {len(df)}")
print(df.head())

# Salva os dados
df.to_csv("data/twitch_top_games.csv", index=False)
print("Dados salvos em data/twitch_top_games.csv")