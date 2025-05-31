import pandas as pd
import dash_leaflet as dl
from dash import Dash, html

df = pd.read_csv("data/complete_bar_data.csv")
df = df[:1000]

cdb = pd.read_csv("data/complete_cdb_data.csv")

df[["LAT", "LON"]] = df["COORD_GEO"].str.strip("()").str.split(",", expand=True)

df["LAT"] = df["LAT"].str.strip().astype(float)
df["LON"] = df["LON"].str.strip().astype(float)

df = df.dropna(subset=["LAT", "LON"])

center = [df["LAT"].mean(), df["LON"].mean()]

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


markers = []
for _, row in df.iterrows():
    name = row['NOME_FANTASIA'] if row['NOME_FANTASIA'] == "ESTABELECIMENTO SEM NOME" else row['NOME']
    address = row["ENDERECO_COMPLETO"]
    if int(row["ID_CDB"]) == 0:
        markers.append(
            dl.Marker(
                position=[row["LAT"], row["LON"]],
                icon=marker_blue,
                children=[
                    dl.Popup(
                        html.Div([
                            html.H4(name, style={"margin": "5px 0", "textAlign": "center"}),
                            html.Hr(),
                            html.P(address, style={"margin": "5px 0", "textAlign": "center"}),
                        ],
                        style={
                            "border": "2px solid #007BFF",
                            "borderRadius": "10px",
                            "padding": "10px",
                            "backgroundColor": "white",
                            "boxShadow": "2px 2px 6px rgba(0,0,0,0.3)",
                            "textAlign": "center",
                            "width": "200px"
                        })
                    )
                ],
            )
        )
    else:
        cdb_row = cdb.iloc[row["ID_CDB"]]
        markers.append(
            dl.Marker(
                position=[row["LAT"], row["LON"]],
                icon=marker_red,
                children=[
                    dl.Popup([
                        html.Div([
                            html.H4(name, style={"margin": "5px 0", "textAlign": "center"}),
                            html.Hr(),
                            html.P(address, style={"margin": "5px 0", "textAlign": "center"}),
                            html.Br(),
                            html.B("Petisco Comida di Buteco:", style={"color": "#d35400"}),
                            html.B(f"{cdb_row['PETISCO']}", style={"display": "block", "margin-bottom": "5px"}),
                            html.I(cdb_row["DESCRICAO"], style={"display": "block", "font-size": "13px", "margin-bottom": "5px"}),
                            html.A(
                                html.Img(
                                    src=cdb_row["IMAGEM"],
                                    style={
                                        "width": "180px",
                                        "height": "auto",
                                        "border": "2px solid #555",
                                        "border-radius": "8px",
                                        "margin-top": "8px",
                                        "box-shadow": "2px 2px 5px rgba(0,0,0,0.3)"
                                    }
                                ),
                                href=cdb_row["IMAGEM"],
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
                    ])

                ],
            )
        )

app = Dash(__name__)
app.layout = dl.Map(
    children=[
        dl.TileLayer(),
        dl.LayerGroup(markers)
    ],
    center=center,
    zoom=12,
    style={"width": "100%", "height": "80vh", "margin": "auto", "display": "block"},
)

if __name__ == "__main__":
    app.run(debug=True)