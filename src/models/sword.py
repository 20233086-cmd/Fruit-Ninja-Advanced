class Sword:
    """Lớp đại diện cho kiếm"""
    
    SWORDS = {
        'basic': {'name': 'Kiếm Cơ Bản', 'multiplier': 1.0, 'color': (255, 255, 255), 'price': 0},
        'flame': {'name': 'Kiếm Lửa', 'multiplier': 1.5, 'color': (255, 100, 0), 'price': 500},
        'lightning': {'name': 'Kiếm Sét', 'multiplier': 2.0, 'color': (255, 255, 0), 'price': 1000},
        'ice': {'name': 'Kiếm Băng', 'multiplier': 2.5, 'color': (100, 220, 255), 'price': 1800},
        'magic': {'name': 'Kiếm Ma Thuật', 'multiplier': 3.0, 'color': (180, 0, 255), 'price': 3000}
    }

    EFFECTS = {
        "basic": {
            "color": (255, 255, 255),
            "particle": "normal",
            "shake": 0,
            "trail": False
        },
        "flame": {
            "color": (255, 80, 0),
            "particle": "fire",
            "shake": 3,
            "trail": True
        },
        "ice": {
            "color": (180, 240, 255),
            "particle": "ice",
            "shake": 1,
            "trail": True
        },
        "lightning": {
            "color": (255, 255, 0),
            "particle": "electric",
            "shake": 8,
            "trail": True
        },
        "magic": {
            "color": (200, 0, 255),
            "particle": "magic",
            "shake": 4,
            "trail": True
        },
        "azure_lightning_sword": {
            "shake": 4,
            "particle": "electric_blue"
        },

        "dragon_fire_sword": {
            "shake": 5,
            "particle": "dragon_fire"
        },

        "frost_soul_sword": {
            "shake": 4,
            "particle": "frost_soul"
        },

        "jade_demon_sword": {
            "shake": 3,
            "particle": "jade"
        },

        "legendary_relic_sword": {
            "shake": 6,
            "particle": "gold_burst"
        },

        "nova_relic_sword": {
            "shake": 7,
            "particle": "nova"
        },

        "stormborn_necro_sword": {
            "shake": 6,
            "particle": "dark_storm"
        }
    }
    
    def __init__(self, sword_type='basic'):
        self.type = sword_type
        self.name = self.SWORDS[sword_type]['name']
        self.multiplier = self.SWORDS[sword_type]['multiplier']
        self.color = self.SWORDS[sword_type]['color']
        self.price = self.SWORDS[sword_type]['price']
    
    @classmethod
    def get_all_swords(cls):
        """Lấy danh sách tất cả kiếm"""
        return [cls(sword_type) for sword_type in cls.SWORDS.keys()]
