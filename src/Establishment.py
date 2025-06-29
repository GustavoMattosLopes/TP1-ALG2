import pandas as pd

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

    @property
    def name(self):
        self.load_data()
        return self.data.get("name") if self.data else None

    @property
    def lat(self):
        self.load_data()
        return self.data.get("lat") if self.data else self.y

    @property
    def lon(self):
        self.load_data()
        return self.data.get("lon") if self.data else self.x

    def to_dict(self):
        return {
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),  # lembre de incluir o id aqui se precisar
            x=data.get("lon"),
            y=data.get("lat"),
            data_source=None  # ou repassar seu data_source se precisar
        )

    def get_info(self):
        self.load_data()
        return self.data

    def __str__(self):
        return f'Establishment {self.id} @ ({self.x}, {self.y})'


    
    
# EXEMPLO DE USO
# leia com:
# df = pd.read_csv("../data/complete_bar_data.csv",  index_col="ID_ATIV_ECON_ESTABELECIMENTO")
# e = Establishment(id=1023, x=-19.92, y=-43.94, data_source=df)
# print(e)  # mostra so coordenadas
# print(e.get_info())  # aqui ele carrega os dados do CSV na hora

