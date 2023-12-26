import json

class Tile:
    def __init__(self, tile_type, variant, pos):
        self.type = tile_type
        self.variant = variant
        self.pos = list(pos)
    
    def get_dict(self):
        return json.loads(json.dumps(self, cls=TileEncoder, indent=4))
    
    def __repr__(self):
        return str({
            'type': self.type,
            'variant': self.variant,
            'pos': self.pos
        })

class TileEncoder(json.JSONEncoder):
    def default(self, obj):
        return {
            'type': obj.type,
            'variant': obj.variant,
            'pos': obj.pos
        }