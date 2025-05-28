import pandas as pd

data = pd.read_csv("dados_filtrados.csv")
cdb = pd.read_csv("bares_cdb2025.csv")

data["NOME_FANTASIA"] = data["NOME_FANTASIA"].str.upper().str.strip()
data["ENDERECO_COMPLETO"] = data["ENDERECO_COMPLETO"].str.upper().str.strip()

cdb["Nome"] = cdb["Nome"].str.upper().str.strip()
cdb["Endereço"] = cdb["Endereço"].str.upper().str.strip()

nomes_ref = set(data["NOME_FANTASIA"])
enderecos_ref = set(data["ENDERECO_COMPLETO"])

nao_encontrados = []

for _, row in cdb.iterrows():
    nome = row["Nome"]
    endereco = row["Endereço"]

    if (endereco not in enderecos_ref):
        nao_encontrados.append({
            "Nome": nome,
            "Endereço": endereco
        })

for item in nao_encontrados:
    print(f'{item["Nome"]} - {item["Endereço"]}')

pd.DataFrame(nao_encontrados).to_csv("nao_encontrados.csv", index=False, encoding="utf-8-sig")