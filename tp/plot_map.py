import re
import json
import random
import pandas as pd
from collections import defaultdict

import dash
from dash import dcc, html, Input, Output, State
import dash_leaflet as dl

# =======================
# === Dados e leituras ===
# =======================

df = pd.read_csv("data/complete_bar_data.csv", index_col="ID_ATIV_ECON_ESTABELECIMENTO")
cdb = pd.read_csv("data/complete_cdb_data.csv")

with open("data/BAIRRO_OFICIAL_bh_reprojetado.geojson", encoding="utf-8") as f:
    geojson_data = json.load(f)

# ========================
# === Classe principal ===
# ========================

class Establishment:
    def __init__(self, id, x, y, data_source):
        self.id = id
        self.x = x
        self.y = y
        self._data_source = data_source
        self._loaded = False
        self.data = None

    def load_data(self):
        if not self._loaded and self.id in self._data_source.index:
            rows = self._data_source.loc[self.id]
            self.data = rows.iloc[0].to_dict() if isinstance(rows, pd.DataFrame) else rows.to_dict()
            self._loaded = True

    def get_info(self):
        self.load_data()
        return self.data

    def __str__(self):
        return f'Establishment {self.id} @ ({self.x}, {self.y})'
    
# ==========================
# === Variáveis Globais ===
# ==========================

marker_red = {
    "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
    "shadowUrl": "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    "iconSize": [25, 41],
    "iconAnchor": [12, 41],
    "popupAnchor": [1, -34],
    "shadowSize": [41, 41]
}

marker_blue = {
    "iconUrl": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
    "shadowUrl": "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
    "iconSize": [25, 41],
    "iconAnchor": [12, 41],
    "popupAnchor": [1, -34],
    "shadowSize": [41, 41]
}

# Pontos fixos para teste do retângulo
establishments_list = [
    Establishment(id=1023, x=-19.92, y=-43.94, data_source=df),
    Establishment(id=123, x=-19.9242, y=-43.9442, data_source=df),
    Establishment(id=60651, x=-19.9243, y=-43.9445, data_source=df)
]


# ========================
# === Utilitários ===
# ========================

def extrair_coordenadas(coord_str):
    if not isinstance(coord_str, str) or ',' not in coord_str:
        return None
    try:
        lat_str, lon_str = coord_str.strip("() ").split(",")
        lat, lon = float(lat_str.strip()), float(lon_str.strip())
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
    except ValueError:
        return None
    return None

def jitter_coordinates(position, jitter_amount=1e-5):
    lat, lon = position
    return (
        lat + random.uniform(-jitter_amount, jitter_amount),
        lon + random.uniform(-jitter_amount, jitter_amount)
    )

def format_address(addr):
    addr = addr.title()
    for prep in [" De ", " Do ", " Da ", " Dos ", " Das ", " E ", " Em "]:
        addr = addr.replace(prep, prep.lower())
    return re.sub(r'\bMg\b', "MG", addr)

# =========================
# === Dados dos pontos ===
# =========================

locs = []
for idx, row in df.iterrows():
    coord = extrair_coordenadas(row.get("COORD_GEO")) or extrair_coordenadas(row.get("COORDS"))
    if coord:
        if int(row["ID_CDB"]) == 0:
            locs.append({
                "id": idx,
                "position": coord,
                "name": row.get("NOME_FANTASIA", "Desconhecido"),
                "icon": marker_blue,
                "address": row.get("ENDERECO_COMPLETO", "Desconhecido")
            })
        else:
            try:
                cdb_row = cdb.iloc[row["ID_CDB"]-1]
                locs.append({
                    "id": idx,
                    "position": coord,
                    "name": row.get("NOME_FANTASIA", "Desconhecido"),
                    "icon": marker_red,
                    "address": row.get("ENDERECO_COMPLETO", "Desconhecido"),
                    "petisco": cdb_row.get("PETISCO", "Desconhecido"),
                    "descricao": cdb_row.get("DESCRICAO", "Desconhecido"),
                    "imagem": cdb_row.get("IMAGEM", "Desconhecido")
                })
            except IndexError:
                print(f"[ERRO] ID_CDB fora do range do iloc: {row['ID_CDB']}")
                print(f"Total de linhas no DataFrame cdb: {len(cdb)}")


# =================================
# === Geração de componentes HTML ===
# =================================

# info para os estabelecimentos selecionados
def generate_establishments_info(establishment_list):
    def make_card(info):
        nome = info.get("NOME_FANTASIA", "Nome não disponível").title()
        addr = format_address(info.get("ENDERECO_COMPLETO", "Endereço não disponível"))
        data_inicio = info.get("DATA_INICIO_ATIVIDADE", "").replace("-", "/") or "Data não disponível"
        alvara_raw = info.get("IND_POSSUI_ALVARA", "Não informado").lower()
        possui_alvara = {
            "sim": "✅ Sim",
            "não": "❌ Não"
        }.get(alvara_raw, "❓ Não informado")

        return html.Div([
            html.H3(nome, style={"marginBottom": "8px", "color": "#2c3e50", "fontWeight": "bold", "fontSize": "20px"}),
            html.P(f"📍 Endereço: {addr}", style={"marginBottom": "6px", "fontSize": "16px", "color": "#34495e"}),
            html.P(f"📅 Data de início: {data_inicio}", style={"marginBottom": "6px", "fontSize": "15px", "color": "#34495e"}),
            html.P(f"🛡️ Possui alvará: {possui_alvara}", style={"marginBottom": "10px", "fontSize": "15px", "color": "#27ae60" if "Sim" in possui_alvara else "#e74c3c"}),
            html.Hr(style={'borderTop': '1px solid #dcdcdc'})
        ], style={'padding': '15px', 'backgroundColor': '#fefefe', 'borderRadius': '8px', 'marginBottom': '15px', 'boxShadow': '0px 2px 8px rgba(0, 0, 0, 0.07)', 'fontFamily': 'Segoe UI, sans-serif'})

    cards = [make_card(est.get_info()) for est in establishment_list if est.get_info()]
    return html.Div(cards, style={'maxHeight': '60vh', 'overflowY': 'auto', 'padding': '10px', 'border': '1px solid #eee', 'borderRadius': '8px', 'backgroundColor': '#ffffff', 'fontFamily': 'Segoe UI, sans-serif'})

# =====================
# === Layout do Dash ===
# =====================

app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Store(id="store-random-ids", data={"zoom": 0, "ids": []}),
    dcc.Store(id="store-markers-cache", data={}),
    html.Link(href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap", rel="stylesheet"),

    html.Div([
        html.H1("Mapa Interativo de Bares em BH", style={'fontFamily': "'Poppins', sans-serif", 'fontSize': '36px', 'fontWeight': '600', 'textAlign': 'center', 'color': '#2c3e50', 'margin': '5px'}),
        html.H3("Explore a cidade dos bares!", style={'fontFamily': "'Poppins', sans-serif", 'fontSize': '20px', 'textAlign': 'center', 'color': '#7f8c8d'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderBottom': '1px solid #ddd'}),

    dl.Map(
        center=[-19.92, -43.94],
        zoom=12,
        id="map",
        children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson_data, options=dict(style=dict(color="#555", weight=1, opacity=0.4, fill=False))),
            dl.LayerGroup(id="markers")
        ],
        style={'width': '100%', 'height': '80vh'}
    ),

    html.H2("Estabelecimentos na Área Selecionada", style={'marginTop': '30px'}),
    html.Div(id="list-all-info", style={'marginTop': '10px'})
])

# ====================
# === Callbacks Dash ===
# ====================

@app.callback(
    Output("list-all-info", "children"),
    Input("map", "zoom")
)
def update_establishments_info(zoom):
    return generate_establishments_info(establishments_list)

@app.callback(
    Output("markers", "children"),
    Output("store-random-ids", "data"),
    Output("store-markers-cache", "data"),
    Input("map", "zoom"),
    Input("map", "bounds"),
    State("store-random-ids", "data"),
    State("store-markers-cache", "data")
)
def update_markers(zoom, bounds, store_data, cache_data):
    if not zoom or not bounds:
        return [], {"zoom": zoom, "ids": []}, []

    lat_s, lon_w = bounds[0]
    lat_n, lon_e = bounds[1]
    lat_margin = (lat_n - lat_s) * 0.3
    lon_margin = (lon_e - lon_w) * 0.3

    visible = [
        loc for loc in locs
        if (lat_s - lat_margin) <= loc["position"][0] <= (lat_n + lat_margin) and
           (lon_w - lon_margin) <= loc["position"][1] <= (lon_e + lon_margin)
    ]

    visible_dict = {loc["id"]: loc for loc in visible}
    visible_ids = set(visible_dict)

    store_data = store_data or {"zoom": zoom, "ids": []}
    cache_data = cache_data or {"zoom": zoom, "ids": []}
    prev_zoom = store_data.get("zoom", zoom)
    current_ids = set(store_data.get("ids", []))

    thresholds = {12: 20, 14: 50, 16: 75, 17: 100}
    max_n = next((v for k, v in sorted(thresholds.items()) if zoom <= k), None)

    reused_ids = current_ids & visible_ids if zoom >= prev_zoom else set()
    new_candidates = list(visible_ids - reused_ids)
    selected_new_ids = random.sample(new_candidates, min(max_n - len(reused_ids), len(new_candidates))) if max_n else new_candidates
    final_ids = list(reused_ids) + selected_new_ids

    position_counts = defaultdict(int)
    for loc_id in final_ids:
        position_counts[visible_dict[loc_id]["position"]] += 1

    markers = []
    for loc_id in final_ids:
        if str(loc_id) in cache_data:
            markers.append(cache_data[str(loc_id)])
            continue
        pos = visible_dict[loc_id]["position"]
        count = position_counts[pos]
        jittered = jitter_coordinates(pos) if count > 1 else pos

        est = Establishment(id=loc_id, x=pos[0], y=pos[1], data_source=df)
        is_cdb = est.get_info().get("ID_CDB")

        popup_content = (
            html.Div([
                html.H4(visible_dict[loc_id]["name"], style={"margin": "5px 0", "textAlign": "center"}),
                html.Hr(),
                html.P(visible_dict[loc_id]["address"], style={"margin": "5px 0", "textAlign": "center"}),
            ],
            style={
                "border": "2px solid #007BFF",
                "borderRadius": "10px",
                "padding": "10px",
                "backgroundColor": "white",
                "boxShadow": "2px 2px 6px rgba(0,0,0,0.3)",
                "textAlign": "center",
                "width": "200px"
            }) if is_cdb == 0 else html.Div([
                html.H4(visible_dict[loc_id]["name"], style={"margin": "5px 0", "textAlign": "center"}),
                html.Hr(),
                html.P(visible_dict[loc_id]["address"], style={"margin": "5px 0", "textAlign": "center"}),
                html.Br(),
                html.B("Petisco Comida di Buteco:", style={"color": "#d35400"}),
                html.B(f"{visible_dict[loc_id]["petisco"]}", style={"display": "block", "margin-bottom": "5px"}),
                html.I(visible_dict[loc_id]["descricao"], style={"display": "block", "font-size": "13px", "margin-bottom": "5px"}),
                html.A(
                    html.Img(
                        src=visible_dict[loc_id]["imagem"],
                        style={
                            "width": "180px",
                            "height": "auto",
                            "border": "2px solid #555",
                            "border-radius": "8px",
                            "margin-top": "8px",
                            "box-shadow": "2px 2px 5px rgba(0,0,0,0.3)"
                        }
                    ),
                    href=visible_dict[loc_id]["imagem"],
                    target="_blank",
                )
            ],
            style={
                "text-align": "center",
                "padding": "10px",
                "border": "2px solid #ccc",
                "border-radius": "10px",
                "background-color": "white",
                "box-shadow": "2px 2px 8px rgba(0,0,0,0.2)"
            })
        )

        marker = dl.Marker(
            id=f"marker-{loc_id}",
            position=jittered,
            icon=visible_dict[loc_id]["icon"],
            children=[dl.Popup(popup_content)]
        )
        
        markers.append(marker)
        cache_data[str(loc_id)] = marker

    return markers, {"zoom": zoom, "ids": final_ids}, cache_data

if __name__ == '__main__':
    app.run(debug=True)
