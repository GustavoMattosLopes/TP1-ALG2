import pandas as pd

data = pd.read_csv("dados_filtrados.csv")
cdb = pd.read_csv("bares_cdb2025.csv")

missing_addresses = [
    address for address in cdb["Endereço"]
    if address not in data["ENDERECO_COMPLETO"].values
]

print("Endereços não encontrados:")
for addr in missing_addresses:
    print(addr)