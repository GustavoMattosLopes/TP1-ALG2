import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "https://www.otempo.com.br/gastronomia/comida-di-buteco/2025/2025/04/03/confira-todos-os-125-bares-participantes-do-comida-di-buteco-belo-horizonte-divididos-por-regiao"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

bares = []

for h2 in soup.find_all("h2"):
    nome_bar = h2.get_text(strip=True)

    img_url = None
    p_img = h2.find_next_sibling("p")
    if p_img:
        strong = p_img.find("strong")
        if strong:
            img_tag = strong.find("img")
            if img_tag:
                img_url = img_tag.get("src")
        if not img_url:
            img_tag = p_img.find("img")
            if img_tag:
                img_url = img_tag.get("src")

    dados_p = p_img.find_next_sibling("p") if p_img else None
    petisco = descricao = endereco = None

    if dados_p:
        partes = str(dados_p).split("<br/>")
        for parte in partes:
            soup_part = BeautifulSoup(parte, "html.parser")
            texto = soup_part.get_text(separator=" ", strip=True)

            if re.search(r"^Petisco[: ]", texto, re.I):
                petisco = re.sub(r"^Petisco[: ]", "", texto, flags=re.I).strip()

            elif re.search(r"^Descrição do petisco[: ]", texto, re.I):
                descricao = re.sub(r"^Descrição do petisco[: ]", "", texto, flags=re.I).strip()

            elif re.search(r"^Endereço[: ]", texto, re.I):
                endereco = re.sub(r"^Endereço[: ]", "", texto, flags=re.I).strip()

    bares.append({
        "Nome": nome_bar,
        "Imagem": img_url,
        "Petisco": petisco,
        "Descrição do petisco": descricao,
        "Endereço": endereco,
    })

df = pd.DataFrame(bares)

print(df.head())

df.to_csv("bares_comida_di_buteco_2025.csv", index=False, encoding="utf-8-sig", sep=";")