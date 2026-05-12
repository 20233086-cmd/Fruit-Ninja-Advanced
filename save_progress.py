# save_progress.py
import json
import os

class ProgressManager:
    """Quản lý tiến trình chơi"""
    
    def __init__(self):
        self.save_file = "progress.json"
        self.progress = self.load()
    
    def load(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Đảm bảo có key swords
                    if 'swords' not in data:
                        data['swords'] = ['basic']
                    if 'current_sword' not in data:
                        data['current_sword'] = 'basic'
                    return data
            except:
                pass
        return {"stars": {1: 0, 2: 0, 3: 0}, 
                "best_scores": {1: 0, 2: 0, 3: 0},
                "swords": ['basic'],
                "current_sword": 'basic'}
    
    def add_sword(self, sword_type):
        """Thêm kiếm mới"""
        if sword_type not in self.progress['swords']:
            self.progress['swords'].append(sword_type)
            self.save()
            print(f"⚔️ Đã lưu kiếm: {sword_type}")

    def set_current_sword(self, sword_type):
        """Đặt kiếm đang dùng"""
        if sword_type in self.progress['swords']:
            self.progress['current_sword'] = sword_type
            self.save()
            print(f"⚔️ Đã đổi sang kiếm: {sword_type}")
    
    def get_current_sword(self):
        return self.progress.get('current_sword', 'basic')
    
    def get_swords(self):
        return self.progress.get('swords', ['basic'])

    def save(self):
        with open(self.save_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def get_stars(self, level):
        return self.progress["stars"].get(level, 0)
    
    def update_stars(self, level, stars):
        current = self.progress["stars"].get(level, 0)
        if stars > current:
            self.progress["stars"][level] = stars
            self.save()
            print(f"⭐ Lưu sao level {level}: {stars} sao")
            return True
        return False
    
    def get_total_stars(self):
        return sum(self.progress["stars"].values())
    
    def get_all_stars(self):
        return self.progress["stars"]
