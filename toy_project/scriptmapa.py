import json
import pandas as pd
import dash
from dash import html, Output, Input, State, ALL
import dash_leaflet as dl
import random
from dash import dcc
import re

import pandas as pd

df = pd.read_csv("../data/complete_bar_data.csv",  index_col="ID_ATIV_ECON_ESTABELECIMENTO")

class Establishment:
    def __init__(self, id, x, y, data_source):
        self.id = id
        self.x = x
        self.y = y
        self._data_source = data_source
        self._loaded = False
        self.data = None

    def load_data(self):
        if not self._loaded:
            if self.id in self._data_source.index:
                rows = self._data_source.loc[self.id]
                if isinstance(rows, pd.DataFrame):
                    # Pega só a primeira linha para evitar o dicionário aninhado
                    self.data = rows.iloc[0].to_dict()
                else:
                    self.data = rows.to_dict()
                self._loaded = True

    def get_info(self):
        self.load_data()
        return self.data

    def __str__(self):
        return f'Establishment {self.id} @ ({self.x}, {self.y})'



establishments_list = [
    Establishment(id=1023, x=-19.92, y=-43.94, data_source=df),
    Establishment(id=123, x=-19.9242, y=-43.9442, data_source=df),
    Establishment(id=60651, x=-19.9243, y=-43.9445, data_source=df) 
]



def bounds_overlap(bounds1, bounds2, tol=0.05):
    """Retorna True se bounds1 e bounds2 se sobrepõem com alguma tolerância"""
    if not bounds1 or not bounds2:
        return False

    (lat_s1, lon_w1), (lat_n1, lon_e1) = bounds1
    (lat_s2, lon_w2), (lat_n2, lon_e2) = bounds2

    lat_overlap = (lat_s1 - tol) <= lat_n2 and (lat_n1 + tol) >= lat_s2
    lon_overlap = (lon_w1 - tol) <= lon_e2 and (lon_e1 + tol) >= lon_w2
    return lat_overlap and lon_overlap



df = pd.read_csv("../data/complete_bar_data.csv")

with open("../data/BAIRRO_OFICIAL_bh.geojson", encoding='utf-8') as f:
    BAIRRO_OFICIAL_geojson = json.load(f)

def extrair_coordenadas(coord_str):
    if not isinstance(coord_str, str) or ',' not in coord_str:
        return None
    coord_str = coord_str.strip("() ")
    lat_str, lon_str = coord_str.split(",")
    try:
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return (lat, lon)
    except ValueError:
        return None
    return None


locs = []
for idx, row in df.iterrows():
    coord = extrair_coordenadas(row["COORDS"])
    if coord is None or (pd.isna(coord[0]) or pd.isna(coord[1])):
        coord = extrair_coordenadas(row["COORD_GEO"])
    if coord:
        locs.append({
            "id": idx,  
            "position": coord,
            "name": row["NOME_FANTASIA"]
        })


def generate_establishments_info(establishment_list):
    cards = []
    for est in establishment_list:
        info = est.get_info()
        if not info:
            continue

        nome = info.get("NOME_FANTASIA", "Nome não disponível").title()

        addr = info.get("ENDERECO_COMPLETO", "Endereço não disponível").title()
        preposicoes = [" De ", " Do ", " Da ", " Dos ", " Das ", " E ", " Em "]
        for prep in preposicoes:
            addr = addr.replace(prep, prep.lower())

        addr = re.sub(rf'\b{"MG".title()}\b', "MG", addr)

        data_inicio = info.get("DATA_INICIO_ATIVIDADE", "")
        if data_inicio:
            data_inicio = data_inicio.replace("-", "/")
        else:
            data_inicio = "Data não disponível"

        possui_alvara = info.get("IND_POSSUI_ALVARA", "Não informado").lower()
        possui_alvara = {
            "sim": "✅ Sim",
            "não": "❌ Não"
        }.get(possui_alvara, "❓ Não informado")

        card = html.Div([
            html.H3(f"{nome}", style={
                "marginBottom": "8px",
                "color": "#2c3e50",
                "fontWeight": "bold",
                "fontSize": "20px"
            }),

            html.P(f"📍 Endereço: {addr}", style={
                "marginBottom": "6px",
                "fontSize": "16px",
                "color": "#34495e"
            }),

            html.P(f"📅 Data de início: {data_inicio}", style={
                "marginBottom": "6px",
                "fontSize": "15px",
                "color": "#34495e"
            }),

            html.P(f"🛡️ Possui alvará: {possui_alvara}", style={
                "marginBottom": "10px",
                "fontSize": "15px",
                "color": "#27ae60" if "Sim" in possui_alvara else "#e74c3c"
            }),

            html.Hr(style={'borderTop': '1px solid #dcdcdc'})
        ], style={
            'padding': '15px',
            'backgroundColor': '#fefefe',
            'borderRadius': '8px',
            'marginBottom': '15px',
            'boxShadow': '0px 2px 8px rgba(0, 0, 0, 0.07)',
            'fontFamily': 'Segoe UI, sans-serif'
        })

        cards.append(card)

    return html.Div(cards, style={
        'maxHeight': '60vh',
        'overflowY': 'auto',
        'padding': '10px',
        'border': '1px solid #eee',
        'borderRadius': '8px',
        'backgroundColor': '#ffffff',
        'fontFamily': 'Segoe UI, sans-serif'
    })

app = dash.Dash(__name__, suppress_callback_exceptions=True)


app.layout = html.Div([
    dcc.Store(id="store-random-ids", data={"zoom": 0, "ids": []}),  # armazenamento
    html.H1("Mapa Interativo de Bares em BH"),

    html.Div([
        dl.Map(
            center=[-19.92, -43.94],
            zoom=12,
            id="map",
            children=[
                dl.TileLayer(),
                dl.GeoJSON(data=BAIRRO_OFICIAL_geojson),
                dl.LayerGroup(id="markers")
            ],
            style={'width': '100%', 'height': '80vh'}
        )
    ]),

    html.H2("Estabelecimentos na Área Selecionada", style={'marginTop': '30px'}),
    html.Div(id="list-all-info", style={'marginTop': '10px'})
])

@app.callback(
    Output("list-all-info", "children"),
    Input("map", "zoom")
)
def update_establishments_info(zoom):
    return generate_establishments_info(establishments_list)


import random

@app.callback(
    Output("markers", "children"),
    Output("store-random-ids", "data"),
    Input("map", "zoom"),
    Input("map", "bounds"),
    State("store-random-ids", "data")
)
def update_markers(zoom, bounds, store_data):
    if zoom is None or bounds is None:
        return [], store_data

    lat_south, lon_west = bounds[0]
    lat_north, lon_east = bounds[1]
    lat_margin = (lat_north - lat_south) * 0.2
    lon_margin = (lon_east - lon_west) * 0.2

    visible = [
        loc for loc in locs
        if (lat_south - lat_margin) <= loc["position"][0] <= (lat_north + lat_margin)
        and (lon_west - lon_margin) <= loc["position"][1] <= (lon_east + lon_margin)
    ]

    if zoom < 12:
        max_n = 20
    elif zoom < 14:
        max_n = 50
    elif zoom < 16:
        max_n = 100
    elif zoom < 17:
        max_n = 400
    else:
        max_n = 600

    same_zoom = store_data and store_data.get("zoom") == zoom
    if same_zoom and store_data.get("ids"):
        ids_to_show = set(store_data["ids"])
        filtered = [loc for loc in visible if loc["id"] in ids_to_show]
    else:
        if len(visible) > max_n:
            sampled = random.sample(visible, max_n)
        else:
            sampled = visible
        filtered = sampled
        store_data = {
            "zoom": zoom,
            "ids": [loc["id"] for loc in sampled]
        }

    return [
        dl.Marker(
            position=loc["position"],
            children=dl.Tooltip(loc["name"]),
            id={"type": "marker", "index": loc["id"]},
            n_clicks=0
        )
        for loc in filtered
    ], store_data




if __name__ == '__main__':
    app.run(debug=True)
