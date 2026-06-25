from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

print("Iniciando Chrome...")
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def limpar_numero(texto):
    return re.sub(r'\n.*', '', texto).strip()

def extrair_pagina():
    """Extrai dados da página atual com tratamento de stale elements"""
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    dados = []
    for row in rows:
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                # Extrai todos os textos de uma vez
                textos = [limpar_numero(col.text) for col in cols]
                dados.append({
                    "rank": textos[0],
                    "game": textos[1],
                    "watch_time_hours": textos[2],
                    "stream_time_hours": textos[3],
                    "peak_viewers": textos[4] if len(textos) > 4 else "",
                    "peak_channels": textos[5] if len(textos) > 5 else "",
                    "streamers": textos[6] if len(textos) > 6 else "",
                    "avg_viewers": textos[7] if len(textos) > 7 else "",
                })
        except Exception:
            continue  # Ignora linha com stale element e continua
    return dados

all_data = []
page = 0
total_pages = 20

try:
    driver.get("https://sullygnome.com/games/2025/watched")
    print("Aguardando página carregar...")
    time.sleep(12)

    while page < total_pages:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        time.sleep(2)

        dados = extrair_pagina()
        all_data.extend(dados)
        print(f"Página {page + 1}: {len(dados)} linhas | Total: {len(all_data)}")

        page += 1
        if page < total_pages:
            try:
                next_btn = driver.find_element(By.ID, "tblControl_next")
                if "disabled" in next_btn.get_attribute("class"):
                    print("Última página atingida")
                    break
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(4)
            except Exception as e:
                print(f"Erro na paginação: {e}")
                break

finally:
    driver.quit()

df = pd.DataFrame(all_data)
print(f"\nTotal coletado: {len(df)} jogos")
print(df.head(5))
df.to_csv("data/sullygnome_top2000.csv", index=False)
print("\nSalvo em data/sullygnome_top2000.csv")