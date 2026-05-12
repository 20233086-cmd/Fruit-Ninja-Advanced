import pygame
import os
import math
from src.config import IMAGES_PATH, SCREEN_WIDTH, SCREEN_HEIGHT

class ImageManager:
    """Quản lý hình ảnh - Ưu tiên load file ảnh từ assets"""
    
    def __init__(self):
        self.images = {}
        self.load_all_images()
    
    def load_all_images(self):
        """Tải tất cả hình ảnh từ assets"""
        print(f"📁 Đang tải ảnh từ: {IMAGES_PATH}")
        
        # Tạo thư mục nếu chưa có
        folders = ['fruits', 'bombs', 'swords', 'background', 'effects', 'ui', 'items']
        for folder in folders:
            os.makedirs(os.path.join(IMAGES_PATH, folder), exist_ok=True)
        
        # Backgrounds
        for i in range(1, 6):
            self._load_image(f'background/bg_level{i}', f'bg_{i}', (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Fruits
        fruits = ['apple', 'orange', 'banana', 'watermelon', 'coconut', 'pineapple']
        for fruit in fruits:
            self._load_image(f'fruits/{fruit}', fruit, (100, 80))
        
        # Bomb
        self._load_image('bombs/bomb', 'bomb', (100, 80))
        
        # Swords
        swords = [
            'basic_sword', 
            'flame_sword', 
            'lightning_sword', 
            'ice_sword', 
            'magic_sword', 
            'azure_lightning_sword',
            'dragon_fire_sword',
            'frost_soul_sword',
            'jade_demon_sword',
            'legendary_relic_sword',
            'nova_relic_sword',
            'stormborn_necro_sword'
        ]
        for sword in swords:
            self._load_image(f'swords/{sword}', sword, (80, 80))
        
        # Effects - STARS
        self._load_image('effects/star', 'star', (40, 40))
        self._load_image('effects/star_empty', 'star_empty', (40, 40))
        self._load_image('effects/explosion', 'explosion', (50, 50))
        self._load_image('effects/slice', 'slice', (100, 100))
        # Hearts (mạng)
        self._load_image('effects/heart', 'heart', (40, 40))
        self._load_image('effects/heart_empty', 'heart_empty', (40, 40))
        
        # UI
        self._load_image('ui/sound_on', 'sound_on', (60, 60))
        self._load_image('ui/sound_off', 'sound_off', (60, 60))
        self._load_image('ui/music_on', 'music_on', (30, 30))
        self._load_image('ui/music_off', 'music_off', (30, 30))
        self._load_image('ui/shop_icon', 'shop_icon', (60, 60))
        self._load_image('ui/sword_icon', 'sword_icon', (40, 40))
        self._load_image('ui/eye_open', 'eye_open', (40, 40))
        self._load_image('ui/eye_close', 'eye_close', (40, 40))

        # ITEMS
        items = [
            'double_score',
            'extra_life',
            'coin',
            'slow_motion'
        ]

        for item in items:
            self._load_image(f'items/{item}', item, (55, 55))
                
        print(f"✅ Đã tải/tạo {len(self.images)} hình ảnh")
    
    def _load_image(self, relative_path, key, size=None):
        """Tải ảnh từ file, nếu không có thì tạo mặc định"""
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        for ext in extensions:
            full_path = os.path.join(IMAGES_PATH, f"{relative_path}{ext}")
            if os.path.exists(full_path):
                try:
                    image = pygame.image.load(full_path).convert_alpha()
                    if size:
                        image = pygame.transform.scale(image, size)
                    self.images[key] = image
                    print(f"  ✅ Load: {relative_path}{ext}")
                    return True
                except Exception as e:
                    print(f"  ❌ Lỗi: {full_path} - {e}")
        
        # Không tìm thấy, tạo mặc định
        print(f"  ⚠️ Tạo mặc định: {key}")
        self._create_default_image(key, size)
        return False
    
    def _create_default_image(self, key, size=None):
        """Tạo ảnh mặc định"""
        if not size:
            size = (40, 40)
        
        surf = pygame.Surface(size, pygame.SRCALPHA)
        
        if key == 'star':
            # Sao vàng
            points = []
            for i in range(5):
                angle = i * 72 - 90
                r = size[0] // 2
                x = size[0]//2 + int(r * math.cos(math.radians(angle)))
                y = size[1]//2 + int(r * math.sin(math.radians(angle)))
                points.append((x, y))
            pygame.draw.polygon(surf, (255, 215, 0), points)
            
        elif key == 'star_empty':
            # Sao trống
            points = []
            for i in range(5):
                angle = i * 72 - 90
                r = size[0] // 2
                x = size[0]//2 + int(r * math.cos(math.radians(angle)))
                y = size[1]//2 + int(r * math.sin(math.radians(angle)))
                points.append((x, y))
            pygame.draw.polygon(surf, (100, 100, 100), points, 2)
            
        elif key == 'sound_on':
            pygame.draw.rect(surf, (0, 255, 0), surf.get_rect())
            text = pygame.font.Font(None, 20).render("🔊", True, (255, 255, 255))
            surf.blit(text, (5, 5))
            
        elif key == 'sound_off':
            pygame.draw.rect(surf, (255, 0, 0), surf.get_rect())
            text = pygame.font.Font(None, 20).render("🔇", True, (255, 255, 255))
            surf.blit(text, (5, 5))
            
        elif key == 'music_on':
            pygame.draw.rect(surf, (0, 255, 0), surf.get_rect())
            text = pygame.font.Font(None, 20).render("🎵", True, (255, 255, 255))
            surf.blit(text, (5, 5))
            
        elif key == 'music_off':
            pygame.draw.rect(surf, (255, 0, 0), surf.get_rect())
            text = pygame.font.Font(None, 20).render("🎵❌", True, (255, 255, 255))
            surf.blit(text, (5, 5))
            
        elif key == 'shop':
            pygame.draw.rect(surf, (0, 0, 255), surf.get_rect())
            text = pygame.font.Font(None, 20).render("🛒", True, (255, 255, 255))
            surf.blit(text, (5, 5))
            
        elif key == 'sword_icon':
            pygame.draw.line(surf, (192, 192, 192), (size[0]//2, 5), (size[0]//2, size[1]-5), 6)
            pygame.draw.rect(surf, (139, 69, 19), (size[0]//2-8, size[1]-15, 16, 10))
            
        else:
            pygame.draw.rect(surf, (128, 128, 128), surf.get_rect())
        
        self.images[key] = surf
    
    def get_image(self, key, default_color=None, size=None):
        """Lấy hình ảnh"""
        if key in self.images:
            return self.images[key]
        
        # Thử tìm key tương tự
        simple_key = key.split('/')[-1]
        if simple_key in self.images:
            return self.images[simple_key]
        
        # Tạo mới
        if not size:
            size = (40, 40)
        self._create_default_image(key, size)
        return self.images[key]
    
    def get_star(self, filled=True):
        """Lấy ảnh sao"""
        if filled:
            return self.get_image('star')
        return self.get_image('star_empty')
    
    def get_sword(self, sword_type):
        key = sword_type.lower()

        # nhóm kiếm cũ
        legacy_map = {
            "basic": "basic_sword",
            "flame": "flame_sword",
            "ice": "ice_sword",
            "lightning": "lightning_sword",
            "magic": "magic_sword",
        }

        # nhóm kiếm mới
        new_map = {
            "azure_lightning_sword": "azure_lightning_sword",
            "dragon_fire_sword": "dragon_fire_sword",
            "frost_soul_sword": "frost_soul_sword",
            "jade_demon_sword": "jade_demon_sword",
            "legendary_relic_sword": "legendary_relic_sword",
            "nova_relic_sword": "nova_relic_sword",
            "stormborn_necro_sword": "stormborn_necro_sword",
        }

        if key in legacy_map:
            return self.get_image(f"swords/{legacy_map[key]}", size=(80, 80))

        if key in new_map:
            return self.get_image(f"swords/{new_map[key]}", size=(80, 80))

        return self.get_image(f"swords/basic_sword", size=(80, 80))
    
    def get_heart(self, filled=True):
        """Lấy ảnh trái tim (mạng)"""
        if filled:
            return self.get_image('heart')
        return self.get_image('heart_empty')
    
    def get_eye(self, open=True):
        if open:
            return self.get_image('eye_open')
        return self.get_image('eye_close')
