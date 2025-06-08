import re
import json
import random
import pandas as pd
from collections import defaultdict
from src.KdTree import KdTree

import dash
from dash import dcc, html, Input, Output, State
import dash_leaflet as dl
from src.Rectangle import Rectangle
from src.Establishment import Establishment
# =======================
# === Dados e leituras ===
# =======================

df = pd.read_csv("data/complete_bar_data.csv", index_col="ID_ATIV_ECON_ESTABELECIMENTO")
cdb = pd.read_csv("data/complete_cdb_data.csv")

with open("data/BAIRRO_OFICIAL_bh_reprojetado.geojson", encoding="utf-8") as f:
    geojson_data = json.load(f)
    
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

rectangle_list_g = []
establishments = []

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

def establishment_to_dict(est: Establishment, df, cdb, marker_blue, marker_red):
    row = df.loc[est.id]
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0] 
    base = {
        "id": est.id,
        "position": (est.x, est.y),
        "name": row.get("NOME_FANTASIA", "Desconhecido"),
        "icon": marker_blue,
        "address": row.get("ENDERECO_COMPLETO", "Desconhecido"),
    }

    if int(row["ID_CDB"]) > 0:
        try:
            cdb_row = cdb.iloc[int(row["ID_CDB"]) - 1]
            base.update({
                "icon": marker_red,
                "petisco": cdb_row.get("PETISCO", "Desconhecido"),
                "descricao": cdb_row.get("DESCRICAO", "Desconhecido"),
                "imagem": cdb_row.get("IMAGEM", "Desconhecido")
            })
        except IndexError:
            print(f"[ERRO] ID_CDB fora do range do iloc: {row['ID_CDB']}")
            print(f"Total de linhas no DataFrame cdb: {len(cdb)}")

    return base

# =========================
# === Dados dos pontos ===
# =========================

locs = []
maior = -100000
menor = 1000000
for idx, row in df.iterrows():
    coord = extrair_coordenadas(row.get("COORD_GEO")) or extrair_coordenadas(row.get("COORDS"))
    if coord:
        if int(row["ID_CDB"]) == 0:
            establishments.append(Establishment(idx, coord[0] , coord[1] , df))
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
                establishments.append(Establishment(idx, coord[0] , coord[1] , df))
            except IndexError:
                print(f"[ERRO] ID_CDB fora do range do iloc: {row['ID_CDB']}")
                print(f"Total de linhas no DataFrame cdb: {len(cdb)}")


# Criando a Kd-tree
kdtree = KdTree(establishments)

# =================================
# === Geração de componentes HTML ===
# =================================

# info para os estabelecimentos selecionados
def generate_establishments_info(establishment_list):
    def make_card(info):
        # Nome
        nome_raw = info.get("NOME_FANTASIA")
        nome = nome_raw.title() if isinstance(nome_raw, str) else "Nome não disponível"

        # Endereço
        endereco_raw = info.get("ENDERECO_COMPLETO")
        addr = format_address(endereco_raw if isinstance(endereco_raw, str) else "Endereço não disponível")

        # Data de início
        data_inicio_raw = info.get("DATA_INICIO_ATIVIDADE")
        if isinstance(data_inicio_raw, str):
            data_inicio = data_inicio_raw.replace("-", "/") or "Data não disponível"
        else:
            data_inicio = "Data não disponível"

        # Alvará
        alvara_raw = info.get("IND_POSSUI_ALVARA")
        if isinstance(alvara_raw, str):
            alvara_raw = alvara_raw.lower()
        else:
            alvara_raw = "não informado"
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

    if not cards:
        return html.Div("Não há área selecionada", style={
            'padding': '20px',
            'textAlign': 'center',
            'color': '#7f8c8d',
            'fontStyle': 'italic',
            'fontFamily': 'Segoe UI, sans-serif'
        })
    return html.Div(cards, style={'maxHeight': '60vh', 'overflowY': 'auto', 'padding': '10px', 'border': '1px solid #eee', 'borderRadius': '8px', 'backgroundColor': '#ffffff', 'fontFamily': 'Segoe UI, sans-serif'})

# =====================
# === Layout do Dash ===
# =====================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Store(id="store-random-ids", data={"zoom": 0, "ids": []}),
    dcc.Store(id="store-markers-cache", data={}),
    dcc.Store(id="rectangle-list", data=[]),
    dcc.Store(id="past-rectangle-list", data=[]),
    dcc.Store(id="has-rectangle", data=False),
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
            dl.LayerGroup(id="markers"),
            dl.FeatureGroup([
            dl.EditControl(
                id="edit_control",
                draw={
                    'rectangle': True,
                    'polygon': False,
                    'circle': False,
                    'marker': False,
                    'polyline': False,
                    'circlemarker': False
                },
                edit={'edit': True, 'remove': True},
                
            )
        ])

        ],
        
        style={'width': '100%', 'height': '80vh'},
            
    ),

    html.H2("Estabelecimentos na Área Selecionada", style={'marginTop': '30px'}),
    html.Div(id="list-all-info", style={'marginTop': '10px'}),
    html.Div(id="rectangle_data", style={"display": "none"})

])

# ====================
# === Callbacks Dash ===
# ====================

@app.callback(
    Output("list-all-info", "children"),
    Output("rectangle-list", "data"),
    Output("has-rectangle", "data"),
    Input("map", "zoom"),
    Input("edit_control", "geojson"),
    State("list-all-info", "children"),
    prevent_initial_call=True
)

def update_establishments_info(zoom, feature_collection, actual):
    global rectangle_list_g
    global exist_rectangles
    if feature_collection is None or not feature_collection.get("features"):
        return generate_establishments_info([]), [], False
    
    rectangles = []
    for feature in feature_collection["features"]:
        geometry = feature.get("geometry", {})
        if geometry.get("type") == "Polygon":
            coordinates = geometry.get("coordinates", [])
            if coordinates:
                rectangles.append(coordinates[0])

    if(len(rectangles) > 1):
        return dash.no_update
    
    xmax = max(rectangles[0], key=lambda x: x[1])[1]
    xmin = min(rectangles[0], key=lambda x: x[1])[1]
    ymax = max(rectangles[0], key=lambda x: x[0])[0]
    ymin = min(rectangles[0], key=lambda x: x[0])[0]

    establishments_query = kdtree.query(Rectangle(xmin, xmax, ymin, ymax))
    rectangle_list_g = establishments_query.copy()
    rectangle_list_g = [
        establishment_to_dict(est, df, cdb, marker_blue, marker_red)
        for est in establishments_query
    ]
    ids_in_rectangle = [e.id for e in establishments_query]

    return generate_establishments_info(establishments_query), ids_in_rectangle, True

@app.callback(
    Output("markers", "children"),
    Output("store-random-ids", "data"),
    Output("store-markers-cache", "data"),
    Output("past-rectangle-list", "data"),
    Input("map", "zoom"),
    Input("map", "bounds"),
    Input("has-rectangle", "data"),
    State("store-random-ids", "data"),
    State("store-markers-cache", "data"),
    State("rectangle-list", "data"),
    State("past-rectangle-list", "data")
)
def update_markers(zoom, bounds, has_rectangle, store_data, cache_data, rectangle_list, past_rectangle_list):
    if not zoom or not bounds:
        return [], {"zoom": zoom, "ids": []}, [], []
    
    if has_rectangle:
        past_rectangle_list = rectangle_list.copy()

    lat_s, lon_w = bounds[0]
    lat_n, lon_e = bounds[1]
    lat_margin = (lat_n - lat_s) * 0.3
    lon_margin = (lon_e - lon_w) * 0.3

    print("1", type(locs), type(locs[0]), locs[0])

    if has_rectangle:
        visible = [
            loc for loc in rectangle_list_g
            if (lat_s - lat_margin) <= loc["position"][0] <= (lat_n + lat_margin) and
            (lon_w - lon_margin) <= loc["position"][1] <= (lon_e + lon_margin)
        ]
    else:
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
        cached_marker = cache_data.get(str(loc_id))

        if cached_marker:
            markers.append(cached_marker)
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
                html.B(f"{visible_dict[loc_id]['petisco']}", style={"display": "block", "margin-bottom": "5px"}),
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

        icon_name = visible_dict[loc_id]["icon"]

        marker = dl.Marker(
            id=f"marker-{loc_id}",
            position=jittered,
            icon=icon_name,
            children=[dl.Popup(popup_content)]
        )
        
        markers.append(marker)
        cache_data[str(loc_id)] = marker

    return markers, {"zoom": zoom, "ids": final_ids}, cache_data, past_rectangle_list

if __name__ == '__main__':
    app.run_server(debug=False)
