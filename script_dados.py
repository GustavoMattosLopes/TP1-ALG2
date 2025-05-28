import pandas as pd
from time import sleep
import requests
from tqdm import tqdm

# Carregando dados
df_final = pd.read_csv("comida_di_buteco/dados_com_cdb.csv")
df_final["COORDS"] = ""

# Arquivos de log
log_file = open("logs/log_geolocalizacao.txt", "w", encoding="utf-8")
falhas_file = open("logs/enderecos_nao_encontrados.txt", "w", encoding="utf-8")

def log(mensagem):
    """Escreve a mensagem no log de terminal e no log_file."""
    print(mensagem, flush=True)
    log_file.write(mensagem + "\n")

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
        log(f"⚠️ Erro ao geocodificar: {endereco} - {e}")
    return None

# Progresso
total = len(df_final)
percent_step = 5
next_percent = percent_step

for i, row in df_final.iterrows():
    endereco = row["ENDERECO_COMPLETO"]

    nome_fantasia = row.get("NOME_FANTASIA", "").strip()
    nome_real = row.get("NOME", "").strip()
    nome = nome_real if nome_fantasia.upper() == "ESTABELECIMENTO SEM NOME" else nome_fantasia

    if pd.notna(endereco) and endereco.strip() != "":
        coord = obter_coordenadas(endereco)
        df_final.at[i, "COORDS"] = coord

        if coord:
            log(f"[{i}] OK - {nome} | {endereco} → {coord}")
        else:
            log(f"[{i}] ERRO - {nome} / {nome_fantasia} | {endereco} → Coordenadas não encontradas")
            falhas_file.write(f"{nome} | {endereco}\n")
    else:
        log(f"[{i}] ERRO - Endereço vazio para {nome}")
        falhas_file.write(f"{nome} | Endereço vazio\n")

    progresso_percentual = int((i + 1) / total * 100)
    if progresso_percentual >= next_percent:
        log(f"📍 Progresso: {progresso_percentual}% concluído.")
        next_percent += percent_step

    sleep(1)

# Salvando resultado
df_final.to_csv("data/dados_com_coordenadas.csv", index=False, encoding="utf-8")

log_file.close()
falhas_file.close()
log("✅ Processo finalizado.")
