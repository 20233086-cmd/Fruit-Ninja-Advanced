import pygame
import os
import sys

# Hàm lấy đường dẫn đúng cho dù chạy từ đâu
def get_base_path():
    """Lấy đường dẫn gốc của dự án"""
    if getattr(sys, 'frozen', False):
        # Chạy từ file exe
        return os.path.dirname(sys.executable)
    else:
        # Chạy từ script Python - lấy đường dẫn thư mục gốc
        current_file = os.path.abspath(__file__)
        # Đi lên 2 cấp từ src/config.py lên thư mục gốc
        return os.path.dirname(os.path.dirname(current_file))

BASE_PATH = get_base_path()

# Kích thước màn hình
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)

# Font chữ
pygame.init()

def load_font(size, bold=False):
    font_paths = [
        os.path.join(BASE_PATH, "assets/fonts/arial.ttf"),
        "arial.ttf",
        "c:/Windows/Fonts/arial.ttf",
        "c:/Windows/Fonts/tahoma.ttf",
        "c:/Windows/Fonts/segouiwp.ttf",
        "c:/Windows/Fonts/verdana.ttf",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                if bold:
                    return pygame.font.Font(path, size)
                else:
                    return pygame.font.Font(path, size)
            except:
                continue
    
    return pygame.font.Font(None, size)

FONT_LARGE = load_font(48, True)
FONT_MEDIUM = load_font(32, False)
FONT_SMALL = load_font(24, False)
FONT_TINY = load_font(18, False)

# Đường dẫn assets - SỬ DỤNG BASE_PATH
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
IMAGES_PATH = os.path.join(ASSETS_PATH, "images")
SOUNDS_PATH = os.path.join(ASSETS_PATH, "sounds")

# Tạo thư mục nếu chưa có
os.makedirs(IMAGES_PATH, exist_ok=True)
os.makedirs(SOUNDS_PATH, exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "fruits"), exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "bombs"), exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "background"), exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "swords"), exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "effects"), exist_ok=True)
os.makedirs(os.path.join(IMAGES_PATH, "items"), exist_ok=True)

print(f"BASE_PATH: {BASE_PATH}")
print(f"IMAGES_PATH: {IMAGES_PATH}")
print(f"Thư mục ảnh tồn tại: {os.path.exists(IMAGES_PATH)}")

# Cấu hình database
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'fruit_ninja_db'
}

# Cấu hình level
# Cấu hình level - THAY ĐỔI TARGET COINS THÀNH TARGET SCORE
LEVEL_CONFIG = {
    1: {
        'name': 'Khu rừng nhiệt đới',
        'time': 60,
        'spawn_rate': 45,
        'speed': 1.0,
        'bomb_chance': 0.15,
        'special_chance': 0.05,
        'target_score_1star': 100,    # Cần 100 điểm để 1 sao
        'target_score_2star': 250,    # Cần 250 điểm để 2 sao
        'target_score_3star': 500     # Cần 500 điểm để 3 sao
    },
    2: {
        'name': 'Sa mạc',
        'time': 50,
        'spawn_rate': 35,
        'speed': 1.3,
        'bomb_chance': 0.20,
        'special_chance': 0.08,
        'target_score_1star': 200,
        'target_score_2star': 450,
        'target_score_3star': 800
    },
    3: {
        'name': 'Núi băng',
        'time': 40,
        'spawn_rate': 25,
        'speed': 1.6,
        'bomb_chance': 0.25,
        'special_chance': 0.10,
        'target_score_1star': 300,
        'target_score_2star': 600,
        'target_score_3star': 1000
    },
     4:{
        'name':'Thành phố bóng tối',
        'time':35,
        'spawn_rate':20,
        'speed':2.0,
        'bomb_chance':0.30,
        'special_chance':0.12,
        'target_score_1star':500,
        'target_score_2star':1000,
        'target_score_3star':1600
    },

    5:{
        'name':'Địa ngục dung nham',
        'time':30,
        'spawn_rate':15,
        'speed':2.4,
        'bomb_chance':0.35,
        'special_chance':0.15,
        'target_score_1star':800,
        'target_score_2star':1500,
        'target_score_3star':2200
    }
}
