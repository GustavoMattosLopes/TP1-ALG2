import dash
from dash import html
import dash_leaflet as dl
from dash.dependencies import Output, Input

app = dash.Dash(__name__)

app.layout = html.Div([
    dl.Map(center=[-19.9, -43.9], zoom=12, style={'width': '100%', 'height': '500px'}, children=[
        dl.TileLayer(),
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
                edit={'edit': True, 'remove': True}
            )
        ])
    ]),
    html.Div(id="output")
])

@app.callback(
    Output("output", "children"),
    Input("edit_control", "geojson")
)
def handle_draw(feature_collection):
    print('w')
    if feature_collection is None or not feature_collection.get("features"):
        return "Nenhum retângulo desenhado."
    rectangles = []
    for feature in feature_collection["features"]:
        geometry = feature.get("geometry", {})
        if geometry.get("type") == "Polygon":
            coordinates = geometry.get("coordinates", [])
            if coordinates:
                rectangles.append(coordinates[0])
    return f"Retângulos desenhados: {rectangles}"

if __name__ == "__main__":
    app.run(debug=True)
