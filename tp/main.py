import pandas as pd
import dash_leaflet as dl
from dash import Dash, html

df = pd.read_csv("dataset.csv")

df = df.dropna(subset=["LAT", "LON"]).head()

center = [df["LAT"].mean(), df["LON"].mean()]

markers = []
for _, row in df.iterrows():
    markers.append(
        dl.Marker(
            position=[row["LAT"], row["LON"]],
            children=[
                dl.Popup([
                    html.B(f"ID: {row['ID_ATIV_ECON_ESTABELECIMENTO']}"),
                    html.Br(),
                    html.Span(f"{row['NOME_FANTASIA'] or row['NOME']}"),
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