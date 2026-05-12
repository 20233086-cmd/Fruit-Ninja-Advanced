class Quest:
    """Lớp nhiệm vụ"""
    
    def __init__(self, quest_id, name, description, target_score, reward_coins, reward_item=None):
        self.id = quest_id
        self.name = name
        self.description = description
        self.target_score = target_score
        self.reward_coins = reward_coins
        self.reward_item = reward_item
        self.completed = False
    
    def check_complete(self, score):
        """Kiểm tra hoàn thành nhiệm vụ"""
        if not self.completed and score >= self.target_score:
            self.completed = True
            return True
        return False
    
    @classmethod
    def get_default_quests(cls):
        """Tạo danh sách nhiệm vụ mặc định"""
        return [
            cls(1, "Tân thủ", "Đạt 100 điểm", 100, 50),
            cls(2, "Cao thủ", "Đạt 500 điểm", 500, 100, "flame"),
            cls(3, "Huyền thoại", "Đạt 1000 điểm", 1000, 200, "lightning")
        ]
