class Level:
    """Lớp cấp độ"""
    
    LEVELS = {
        1: {'spawn_rate': 45, 'speed': 1.0, 'bomb_chance': 0.15, 'special_chance': 0.05},
        2: {'spawn_rate': 35, 'speed': 1.3, 'bomb_chance': 0.20, 'special_chance': 0.08},
        3: {'spawn_rate': 25, 'speed': 1.6, 'bomb_chance': 0.25, 'special_chance': 0.10},
        4: {'spawn_rate': 18, 'speed': 1.9, 'bomb_chance': 0.30, 'special_chance': 0.12},
        5: {'spawn_rate': 12, 'speed': 2.2, 'bomb_chance': 0.35, 'special_chance': 0.15}
    }
    
    def __init__(self, level_num):
        self.level_num = level_num

        # chống lỗi nếu level không tồn tại
        if level_num not in self.LEVELS:
            level_num = 1

        data = self.LEVELS[level_num]

        self.spawn_rate = data['spawn_rate']
        self.speed = data['speed']
        self.bomb_chance = data['bomb_chance']
        self.special_chance = data['special_chance']
        self.background = f'bg_{level_num}'
    
    def get_next_level(self):
        """Lấy cấp độ tiếp theo"""
        if self.level_num < 5:
            return Level(self.level_num + 1)
        return None
