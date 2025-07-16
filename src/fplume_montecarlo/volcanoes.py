"""
Define geographical features of volcanoes in the world
"""

class Volcano:

    def __init__(self, name, height, latitude, longitude):
        self.name = name
        self.height = height  # in meters
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"Volcano(name={self.name}, height={self.height}, lat={self.latitude}, lon={self.longitude})"
    
ETNA = Volcano("Etna", height=3350, latitude=37.75, longitude=15.0)
VESUVIUS = Volcano("Vesuvius", height=1281, latitude=40.822, longitude=14.426)

# Registry for lookup by name
VOLCANOES = {
    "Etna": ETNA,
    "Vesuvius": VESUVIUS,
}
