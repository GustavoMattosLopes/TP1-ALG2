# dado que ja temos os dados pré-processados e só precisamos pegar os endereços

import pandas as pd
from time import sleep
from datetime import datetime
import requests


def obter_coordenadas(endereco):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": endereco,
        "format": "json",
        "limit": 1
    }
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()
        if data:
            return f"{data[0]['lat']}, {data[0]['lon']}"
    except Exception as e:
        print(f"Erro ao geocodificar: {endereco} - {e}")
    return None


df_final = pd.read_csv("data/dados_filtrados.csv")
df_final["COORD_GEO"] = ""

log_file = open("logs/log_geolocalizacao.txt", "w", encoding="utf-8")
falhas_file = open("logs/enderecos_nao_encontrados.txt", "w", encoding="utf-8")

for i, row in df_final.iterrows():
    endereco = row["ENDERECO_COMPLETO"]
    nome = row["NOME_FANTASIA"]

    if pd.notna(endereco) and endereco.strip() != "":
        coord = obter_coordenadas(endereco)
        df_final.at[i, "COORD_GEO"] = coord

        if coord:
            log_file.write(f"[{i}] OK - {nome} | {endereco} → {coord}\n")
        else:
            log_file.write(f"[{i}] ERRO - {nome} | {endereco} → Coordenadas não encontradas\n")
            falhas_file.write(f"{nome} | {endereco}\n")
    else:
        log_file.write(f"[{i}] ERRO - Endereço vazio para {nome}\n")
        falhas_file.write(f"{nome} | Endereço vazio\n")

    # print(f"{i+1}/{len(df_final)} - Processado")
    sleep(1)

df_final.to_csv("data/dados_com_coordenadas.csv", index=False, encoding="utf-8")

log_file.close()
falhas_file.close()
print("Processo finalizado.")
