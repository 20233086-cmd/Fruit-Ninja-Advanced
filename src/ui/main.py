import pygame
import sys
from src.config import *
from src.database.db_manager import DatabaseManager
from src.ui.login_screen import LoginScreen
from src.ui.level_select_screen import LevelSelectScreen
from src.game.game_controller import GameController

def main():
    """Hàm chính"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fruit Ninja Advanced")
    
    # Khởi tạo database
    db = DatabaseManager()
    
    # Màn hình đăng nhập
    login = LoginScreen(db)
    username, player_id = login.run()
    
    if not username or not player_id:
        db.close()
        pygame.quit()
        sys.exit()
    
    # Vòng lặp chính cho game
    while True:
        # Màn hình chọn level
        level_select = LevelSelectScreen(db, player_id, username)
        selected_level = level_select.run()
        
        if not selected_level:
            break
        
        # Chạy game với level đã chọn
        game = GameController(username, player_id, db, selected_level)
        stars = game.run()
        
        # Cập nhật lại thông tin sao sau khi chơi
        print(f"Hoan thanh level {selected_level} voi {stars} sao!")
        
        # Hỏi người chơi có muốn tiếp tục không
        # Nếu muốn, vòng lặp sẽ quay lại màn hình chọn level
    
    db.close()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
