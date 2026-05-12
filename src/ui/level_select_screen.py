# src/ui/level_select_screen.py
import pygame
import sys
import random
from save_progress import ProgressManager
from src.config import *
from src.ui.button import Button
from src.managers.image_manager import ImageManager

class LevelSelectScreen:
    """Màn hình chọn level"""
    
    def __init__(self, db_manager, player_id, username):
        self.db_manager = db_manager
        self.player_id = player_id
        self.username = username
        self.running = True
        self.selected_level = None

        self.progress = ProgressManager()
        
        # Khởi tạo ImageManager
        self.image_manager = ImageManager()
        
        # Lấy số sao đã đạt được từ database
        self.star_ratings = self.load_star_ratings()
        
        # Tải ảnh shop
        self.shop_img = self.image_manager.get_image('ui/shop_icon', size=(60, 60))
        
        # Tải ảnh hoa quả trang trí
        self.fruit_images = {
            'apple': self.image_manager.get_image('fruits/apple', size=(40, 40)),
            'orange': self.image_manager.get_image('fruits/orange', size=(40, 40)),
            'banana': self.image_manager.get_image('fruits/banana', size=(40, 40)),
            'watermelon': self.image_manager.get_image('fruits/watermelon', size=(40, 40))
        }
        
        # Tạo nút shop với ảnh
        self.shop_btn = Button(SCREEN_WIDTH - 100, 50, 70, 70, "", GOLD, YELLOW, DARK_GRAY)
        self.shop_btn.image = self.shop_img

        # Tạo các nút level
        self.level_buttons = []
        button_positions = []

        levels_per_row = 5          # mỗi hàng 5 level
        total_levels = len(LEVEL_CONFIG)

        start_x = SCREEN_WIDTH // 2 - 450
        end_x   = SCREEN_WIDTH // 2 + 300

        row_y_start = 350
        row_gap_y = 170            # khoảng cách giữa các hàng

        gap_x = (end_x - start_x) / (levels_per_row - 1)

        for i in range(total_levels):

            row = i // levels_per_row        # hàng số mấy
            col = i % levels_per_row         # cột số mấy

            x = int(start_x + col * gap_x)
            y = row_y_start + row * row_gap_y

            button_positions.append((x, y))
        
        for i in range(1, 6):
            btn = Button(
                button_positions[i-1][0], 
                button_positions[i-1][1], 
                150, 120, 
                f"LEVEL {i}", 
                GOLD, YELLOW, DARK_GRAY
            )
            btn.level_num = i
            self.level_buttons.append(btn)
        
        self.back_btn = Button(50, SCREEN_HEIGHT - 80, 120, 40, "Thoát", RED, GOLD, DARK_GRAY)
        
        # Khởi tạo hoa quả trang trí
        self.deco_fruits = []
        self.init_decorations()
    
    def init_decorations(self):
        """Khởi tạo hoa quả trang trí"""
        fruit_list = ['apple', 'orange', 'banana', 'watermelon']
        for _ in range(12):  # 12 quả bay xung quanh
            self.deco_fruits.append({
                'type': random.choice(fruit_list),
                'x': random.randint(50, SCREEN_WIDTH - 50),
                'y': random.randint(220, SCREEN_HEIGHT - 100),
                'speed_x': random.uniform(-0.8, 0.8),
                'speed_y': random.uniform(-0.8, 0.8),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-3, 3)
            })
    
    def load_star_ratings(self):
        """Lấy số sao đã đạt được từ database"""
        ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        unlocked_levels = {1: True}  # Level 1 luôn mở
        
        if self.db_manager and self.db_manager.conn:
            try:
                # Lấy số sao
                self.db_manager.cursor.execute(
                    "SELECT level, stars FROM player_progress WHERE player_id = %s",
                    (self.player_id,)
                )
                results = self.db_manager.cursor.fetchall()
                for level, stars in results:
                    ratings[level] = stars
                    unlocked_levels[level] = True
                    # Mở khóa level tiếp theo
                    if stars >= 1 and level < 5:
                        unlocked_levels[level + 1] = True
                
                # Lấy highest_level từ players
                self.db_manager.cursor.execute(
                    "SELECT highest_level FROM players WHERE id = %s",
                    (self.player_id,)
                )
                result = self.db_manager.cursor.fetchone()
                if result:
                    highest = result[0]
                    for lvl in range(1, highest + 1):
                        unlocked_levels[lvl] = True
                        
            except Exception as e:
                print(f"Lỗi load sao: {e}")
        
        self.unlocked_levels = unlocked_levels
        print(f"🔓 Level đã mở khóa: {[l for l, u in unlocked_levels.items() if u]}")
        return ratings
    
    def run(self):
        """Chạy màn hình chọn level"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.update_decorations()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        
        return self.selected_level
    
    def update_decorations(self):
        """Cập nhật vị trí hoa quả trang trí"""
        for fruit in self.deco_fruits:
            fruit['x'] += fruit['speed_x']
            fruit['y'] += fruit['speed_y']
            fruit['rotation'] += fruit['rotation_speed']
            
            # Bật lại khi ra khỏi màn hình
            if fruit['x'] < 30:
                fruit['x'] = 30
                fruit['speed_x'] = -fruit['speed_x']
            if fruit['x'] > SCREEN_WIDTH - 30:
                fruit['x'] = SCREEN_WIDTH - 30
                fruit['speed_x'] = -fruit['speed_x']
            if fruit['y'] < 220:
                fruit['y'] = 220
                fruit['speed_y'] = -fruit['speed_y']
            if fruit['y'] > SCREEN_HEIGHT - 80:
                fruit['y'] = SCREEN_HEIGHT - 80
                fruit['speed_y'] = -fruit['speed_y']
    
    def handle_events(self):
        """Xử lý sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in self.level_buttons:
                    if btn.rect.collidepoint(event.pos):
                        self.selected_level = btn.level_num
                        self.running = False
                        return
                    
                if self.shop_btn.rect.collidepoint(event.pos):
                    self.open_shop()
                    return
                
                if self.back_btn.rect.collidepoint(event.pos):
                    self.running = False
                    return
            
            if event.type == pygame.MOUSEMOTION:
                for btn in self.level_buttons:
                    btn.is_hovered = btn.rect.collidepoint(event.pos)
                self.shop_btn.is_hovered = self.shop_btn.rect.collidepoint(event.pos)
                self.back_btn.is_hovered = self.back_btn.rect.collidepoint(event.pos)
    
    def open_shop(self):
        """Mở cửa hàng"""
        from src.game.game_controller import GameController
        temp_game = GameController(self.username, self.player_id, self.db_manager, 1)
        from src.ui.shop_screen import ShopScreen
        shop = ShopScreen(temp_game)
        shop.run()
        self.star_ratings = self.load_star_ratings()

    # ==========================================
    # SỬA TRONG draw(self)
    # THAY TOÀN BỘ HÀM draw() CŨ BẰNG PHẦN NÀY
    # ==========================================

    def draw(self):
        """Vẽ màn hình chọn level"""
        screen = pygame.display.get_surface()
        screen.fill(BLACK)

        # Background
        for i in range(SCREEN_HEIGHT):
            color_value = 50 + int(i * 100 / SCREEN_HEIGHT)
            pygame.draw.line(screen, (0, 100, color_value // 2), (0, i), (SCREEN_WIDTH, i))

        # Viền
        border_rect = pygame.Rect(20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40)
        pygame.draw.rect(screen, GOLD, border_rect, 3)

        # Tiêu đề
        title = FONT_LARGE.render("CHỌN CẤP ĐỘ", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Người chơi
        player_text = FONT_MEDIUM.render(f"Người chơi: {self.username}", True, WHITE)
        screen.blit(player_text, player_text.get_rect(center=(SCREEN_WIDTH // 2, 120)))

        # Ảnh sao
        star_img = self.image_manager.get_star(True)
        empty_star_img = self.image_manager.get_star(False)

        # Tổng sao
        total_stars = self.progress.get_total_stars()
        total_text = FONT_MEDIUM.render(f"TỔNG SỐ SAO: {total_stars}/15", True, GOLD)
        screen.blit(total_text, total_text.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        # Hiển thị tổng sao bằng ảnh
        total_show = 9
        for i in range(total_show):
            x = SCREEN_WIDTH // 2 - 180 + i * 42
            y = 195

            img = star_img if i < total_stars else empty_star_img
            img = pygame.transform.scale(img, (36, 36))
            screen.blit(img, (x, y))

        # Line
        pygame.draw.line(screen, GRAY,
                        (SCREEN_WIDTH // 2 - 350, 240),
                        (SCREEN_WIDTH // 2 + 350, 240), 2)

        # ==========================================
        # LEVEL BUTTONS
        # ==========================================
        for i, btn in enumerate(self.level_buttons):
            level_num = i + 1
            stars = self.star_ratings.get(level_num, 0)

            is_unlocked = self.unlocked_levels.get(level_num, level_num == 1)

            if not is_unlocked:
                btn.color = GRAY
                btn.hover_color = GRAY
                btn.text = f"LEVEL {level_num}"
            else:
                btn.color = GOLD
                btn.hover_color = YELLOW
                btn.text = f"LEVEL {level_num}"

            btn.draw(screen)

            # -------- Tên level ----------
            level_config = LEVEL_CONFIG[level_num]
            name_surface = FONT_TINY.render(level_config['name'], True, WHITE)
            screen.blit(name_surface,
                        name_surface.get_rect(center=(btn.rect.centerx, btn.rect.y - 18)))

            # -------- SAO TRONG BUTTON ----------
            star_size = 32
            gap = 6

            fill_star = pygame.transform.scale(star_img, (star_size, star_size))
            empty_star = pygame.transform.scale(empty_star_img, (star_size, star_size))

            total_width = star_size * 3 + gap * 2
            start_x = btn.rect.centerx - total_width // 2
            star_y = btn.rect.bottom - 42

            for s in range(3):
                x = start_x + s * (star_size + gap)

                if s < stars:
                    screen.blit(fill_star, (x, star_y))
                else:
                    screen.blit(empty_star, (x, star_y))

            # -------- DÒNG 3 SAO : xxx ĐIỂM ----------
            target = level_config['target_score_3star']

            small_star = pygame.transform.scale(star_img, (32, 32))

            num_text = FONT_TINY.render("3", True, GOLD)
            point_text = FONT_TINY.render(f": {target} điểm", True, GOLD)

            total_w = num_text.get_width() + 8 + 32 + 8 + point_text.get_width()
            sx = btn.rect.centerx - total_w // 2
            sy = btn.rect.bottom + 8

            screen.blit(num_text, (sx, sy + 6))
            screen.blit(small_star, (sx + num_text.get_width() + 8, sy))
            screen.blit(point_text,
                        (sx + num_text.get_width() + 48, sy + 6))

        # Shop
        if self.shop_img:
            pygame.draw.rect(screen, DARK_GRAY, self.shop_btn.rect)
            pygame.draw.rect(screen, GOLD, self.shop_btn.rect, 2)
            screen.blit(self.shop_img,
                        (self.shop_btn.rect.x + 5, self.shop_btn.rect.y + 5))

        # Back
        self.back_btn.draw(screen)

        # Guide
        guide = FONT_SMALL.render("Click chuột vào level để chơi | ESC thoát", True, GRAY)
        screen.blit(guide, guide.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

        # Trang trí
        self.draw_decorations(screen)
    
    def draw_decorations(self, screen):
        """Vẽ trang trí hoa quả bằng ảnh"""
        for fruit in self.deco_fruits:
            fruit_img = self.fruit_images.get(fruit['type'])
            if fruit_img:
                # Xoay ảnh
                rotated_img = pygame.transform.rotate(fruit_img, fruit['rotation'])
                rect = rotated_img.get_rect(center=(int(fruit['x']), int(fruit['y'])))
                screen.blit(rotated_img, rect)
            else:
                # Fallback nếu không có ảnh
                pygame.draw.circle(screen, GOLD, (int(fruit['x']), int(fruit['y'])), 15)
