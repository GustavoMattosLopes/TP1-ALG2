import dash_leaflet as dl

def create_edit_control():
    return dl.EditControl(
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
