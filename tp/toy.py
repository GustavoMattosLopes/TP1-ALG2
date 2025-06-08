import dash
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output, State
import json

app = dash.Dash(__name__)

# Estilo para o container do mapa
map_style = {
    'width': '100%', 
    'height': '80vh',
    'margin': "auto",
    'display': "block"
}

app.layout = html.Div([
    html.H1("Selecione uma Área no Mapa", style={'textAlign': 'center'}),
    dl.Map(
        [
            dl.TileLayer(),
            dl.FeatureGroup([
                # Controles de desenho
                dl.EditControl(
                    id="edit_control",
                    draw={
                        "rectangle": True,
                        "polygon": False,
                        "polyline": False,
                        "circle": False,
                        "marker": False,
                        "circlemarker": False
                    },
                    edit={"remove": True}
                )
            ])
        ],
        id="map",
        style=map_style,
        center=[-15.788, -47.879],  # Centro do Brasil
        zoom=4
    ),
    html.Div(id="rectangle_data", style={'display': 'none'}),
    html.Div(id="deleted_rectangles", style={'display': 'none'}),
    html.Div([
        html.H3("Coordenadas do Retângulo:"),
        html.Pre(id="coordinates_display")
    ], style={'margin': '20px'}),
    html.Div(id="foda", style={'display': 'none'}),

])

@app.callback(
    Output("rectangle_data", "children"),
    Input("edit_control", "geojson"),
    prevent_initial_call=True
)
def capture_rectangle(geojson):
    if geojson and geojson['type'] == 'FeatureCollection':
        for feature in geojson['features']:
            if feature['geometry']['type'] == 'Polygon':
                return json.dumps(feature['geometry']['coordinates'])
    return None

@app.callback(
    Output("foda", "children"),
    Input("edit_control", "geojson"),
    State("rectangle_data", "children"),
    prevent_initial_call=True
)
def detect_deleted_rectangle(new_geojson, current_rectangles):
    ctx = dash.callback_context
    
    # Só executa se for triggered pela mudança no geojson
    if not ctx.triggered:
        return dash.no_update
    
    if current_rectangles and (new_geojson is None or len(new_geojson['features']) < 1):
        # Retângulo foi deletado - imprime no console do Python
        print("olá")
        return "deleted"
    return ""

@app.callback(
    Output("coordinates_display", "children"),
    Input("rectangle_data", "children")
)
def display_coordinates(data):
    if data:
        coords = json.loads(data)
        return f"Coordenadas do retângulo:\n{coords}"
    return "Nenhuma área selecionada ainda"

if __name__ == '__main__':
    app.run(debug=True)