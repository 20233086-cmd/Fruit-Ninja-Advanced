# src/ui/login_screen.py
import pygame
import sys
import random
from src.config import *
from src.ui.button import Button
from src.managers.image_manager import ImageManager

class LoginScreen:
    """Màn hình đăng nhập và đăng ký"""
    
    MODE_LOGIN = "login"
    MODE_REGISTER = "register"
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.username = ""
        self.password = ""
        self.confirm_password = ""
        self.active_input = "username"
        self.mode = self.MODE_LOGIN
        self.error_message = ""
        self.success_message = ""
        self.error_timer = 0
        self.success_timer = 0
        self.running = True
        
        # Khởi tạo ImageManager
        self.image_manager = ImageManager()
        
        # Tải ảnh hoa quả trang trí
        self.fruit_images = {
            'apple': self.image_manager.get_image('fruits/apple', size=(50, 50)),
            'orange': self.image_manager.get_image('fruits/orange', size=(50, 50)),
            'banana': self.image_manager.get_image('fruits/banana', size=(50, 50)),
            'watermelon': self.image_manager.get_image('fruits/watermelon', size=(50, 50))
        }
        
        # Trạng thái show password
        self.show_password = False
        self.show_confirm_password = False
        
        # Tạo các nút bấm
        self.login_btn = Button(SCREEN_WIDTH//2 - 150, 440, 300, 50, "ĐĂNG NHẬP", GREEN, GOLD, DARK_GRAY)
        self.register_btn = Button(SCREEN_WIDTH//2 - 150, 530, 300, 50, "ĐĂNG KÝ", BLUE, GOLD, DARK_GRAY)
        self.switch_to_register_btn = Button(SCREEN_WIDTH//2 - 225, 640, 440, 40, "CHUYỂN SANG ĐĂNG KÝ", ORANGE, GOLD, DARK_GRAY)
        self.switch_to_login_btn = Button(SCREEN_WIDTH//2 - 225, 640, 440, 40, "CHUYỂN SANG ĐĂNG NHẬP", ORANGE, GOLD, DARK_GRAY)
        
        # Nút show password
        self.eye_btn_rect = pygame.Rect(SCREEN_WIDTH//2 + 170, 295, 35, 35)
        self.eye_confirm_rect = pygame.Rect(SCREEN_WIDTH//2 + 170, 385, 35, 35)
        
        # Khởi tạo hoa quả bay
        self.init_flying_fruits()
    
    def init_flying_fruits(self):
        """Khởi tạo hoa quả bay trang trí"""
        fruit_types = ['apple', 'orange', 'banana', 'watermelon']
        self.flying_fruits = []
        for _ in range(12):
            self.flying_fruits.append({
                'type': random.choice(fruit_types),
                'x': random.randint(50, SCREEN_WIDTH - 50),
                'y': random.randint(100, SCREEN_HEIGHT - 100),
                'speed_x': random.uniform(-1, 1),
                'speed_y': random.uniform(-1, 1),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-3, 3)
            })
    
    def update_flying_fruits(self):
        """Cập nhật vị trí hoa quả bay"""
        for fruit in self.flying_fruits:
            fruit['x'] += fruit['speed_x']
            fruit['y'] += fruit['speed_y']
            fruit['rotation'] += fruit['rotation_speed']
            
            if fruit['x'] < 30:
                fruit['x'] = 30
                fruit['speed_x'] = -fruit['speed_x']
            if fruit['x'] > SCREEN_WIDTH - 30:
                fruit['x'] = SCREEN_WIDTH - 30
                fruit['speed_x'] = -fruit['speed_x']
            if fruit['y'] < 50:
                fruit['y'] = 50
                fruit['speed_y'] = -fruit['speed_y']
            if fruit['y'] > SCREEN_HEIGHT - 50:
                fruit['y'] = SCREEN_HEIGHT - 50
                fruit['speed_y'] = -fruit['speed_y']
    
    def run(self):
        """Chạy màn hình đăng nhập"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.update_flying_fruits()
            self.handle_events()
            self.draw()
            
            if self.error_timer > 0:
                self.error_timer -= 1
                if self.error_timer == 0:
                    self.error_message = ""
            
            if self.success_timer > 0:
                self.success_timer -= 1
                if self.success_timer == 0:
                    self.success_message = ""
            
            pygame.display.flip()
            clock.tick(FPS)
        
        return self.username, self.player_id
    
    def handle_events(self):
        """Xử lý sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    if self.mode == self.MODE_LOGIN:
                        inputs = ["username", "password"]
                    else:
                        inputs = ["username", "password", "confirm"]
                    
                    if self.active_input in inputs:
                        current_index = inputs.index(self.active_input)
                        next_index = (current_index + 1) % len(inputs)
                        self.active_input = inputs[next_index]
                    else:
                        self.active_input = inputs[0]
                
                elif event.key == pygame.K_RETURN:
                    if self.mode == self.MODE_LOGIN:
                        self.handle_login()
                    else:
                        self.handle_register()
                
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_input == "username":
                        self.username = self.username[:-1]
                    elif self.active_input == "password":
                        self.password = self.password[:-1]
                    elif self.active_input == "confirm":
                        self.confirm_password = self.confirm_password[:-1]
                
                else:
                    if self.active_input == "username":
                        self.username += event.unicode
                    elif self.active_input == "password":
                        self.password += event.unicode
                    elif self.active_input == "confirm":
                        self.confirm_password += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.eye_btn_rect.collidepoint(event.pos):
                    self.show_password = not self.show_password
                if self.eye_confirm_rect.collidepoint(event.pos):
                    self.show_confirm_password = not self.show_confirm_password
                
                if self.mode == self.MODE_LOGIN:
                    if self.login_btn.handle_event(event):
                        self.handle_login()
                    if self.switch_to_register_btn.handle_event(event):
                        self.mode = self.MODE_REGISTER
                        self.active_input = "username"
                        self.error_message = ""
                        self.success_message = ""
                else:
                    if self.register_btn.handle_event(event):
                        self.handle_register()
                    if self.switch_to_login_btn.handle_event(event):
                        self.mode = self.MODE_LOGIN
                        self.active_input = "username"
                        self.error_message = ""
            
            if event.type == pygame.MOUSEMOTION:
                if self.mode == self.MODE_LOGIN:
                    self.login_btn.is_hovered = self.login_btn.rect.collidepoint(event.pos)
                    self.switch_to_register_btn.is_hovered = self.switch_to_register_btn.rect.collidepoint(event.pos)
                else:
                    self.register_btn.is_hovered = self.register_btn.rect.collidepoint(event.pos)
                    self.switch_to_login_btn.is_hovered = self.switch_to_login_btn.rect.collidepoint(event.pos)
    
    def handle_login(self):
        """Xử lý đăng nhập"""
        if not self.username or not self.password:
            self.error_message = "Vui lòng nhập đầy đủ thông tin!"
            self.error_timer = 60
            return
        
        result = self.db_manager.authenticate_user(self.username, self.password)
        if result:
            self.username, self.player_id = result
            self.running = False
        else:
            self.error_message = "Sai tên đăng nhập hoặc mật khẩu!"
            self.error_timer = 60
    
    def handle_register(self):
        """Xử lý đăng ký"""
        if not self.username or not self.password:
            self.error_message = "Vui lòng nhập đầy đủ thông tin!"
            self.error_timer = 60
            return
        
        if self.password != self.confirm_password:
            self.error_message = "Mật khẩu xác nhận không khớp!"
            self.error_timer = 60
            return
        
        if len(self.password) < 4:
            self.error_message = "Mật khẩu phải có ít nhất 4 ký tự!"
            self.error_timer = 60
            return
        
        result = self.db_manager.register_user(self.username, self.password)
        if result:
            self.success_message = "Đăng ký thành công! Vui lòng đăng nhập."
            self.success_timer = 90
            self.mode = self.MODE_LOGIN
            self.username = ""
            self.password = ""
            self.confirm_password = ""
            self.active_input = "username"
        else:
            self.error_message = "Tên đăng nhập đã tồn tại!"
            self.error_timer = 60
    
    def draw(self):
        """Vẽ màn hình"""
        screen = pygame.display.get_surface()
        screen.fill(BLACK)
        
        # Vẽ background gradient
        for i in range(SCREEN_HEIGHT):
            if self.mode == self.MODE_LOGIN:
                color_value = 50 + int(i * 100 / SCREEN_HEIGHT)
                pygame.draw.line(screen, (100, 50, color_value), (0, i), (SCREEN_WIDTH, i))
            else:
                color_value = 50 + int(i * 100 / SCREEN_HEIGHT)
                pygame.draw.line(screen, (color_value, 50, 100), (0, i), (SCREEN_WIDTH, i))
        
        # Vẽ khung viền
        border_rect = pygame.Rect(40, 40, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80)
        pygame.draw.rect(screen, GOLD, border_rect, 3)
        pygame.draw.rect(screen, GOLD, border_rect.inflate(-10, -10), 1)
        
        # Tiêu đề chính
        title = FONT_LARGE.render("FRUIT NINJA", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 70))
        screen.blit(title, title_rect)
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH//2 - 200, 100), (SCREEN_WIDTH//2 + 200, 100), 2)
        
        # Vẽ hoa quả bay
        self.draw_flying_fruits(screen)
        
        # Panel chế độ
        mode_panel = pygame.Rect(SCREEN_WIDTH//2 - 100, 130, 200, 40)
        pygame.draw.rect(screen, DARK_GRAY, mode_panel, border_radius=10)
        pygame.draw.rect(screen, GOLD, mode_panel, 2, border_radius=10)
        
        if self.mode == self.MODE_LOGIN:
            mode_text = FONT_MEDIUM.render("ĐĂNG NHẬP", True, GOLD)
        else:
            mode_text = FONT_MEDIUM.render("ĐĂNG KÝ", True, GOLD)
        mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(mode_text, mode_rect)
        
        # Ô nhập liệu - ĐIỀU CHỈNH LẠI VỊ TRÍ
        # Username
        self.draw_input_field("Tên đăng nhập", self.username, 235, "username")
        
        # Password
        self.draw_input_field("Mật khẩu", self.get_password_display(self.password, self.show_password), 
                              345, "password", show_eye=True)
        
        if self.mode == self.MODE_REGISTER:
            self.draw_input_field("Xác nhận mật khẩu", 
                                 self.get_password_display(self.confirm_password, self.show_confirm_password), 
                                 455, "confirm", show_eye=True)
            self.register_btn.draw(screen)
            btn_y = 440
        else:
            self.login_btn.draw(screen)
            btn_y = 440
        
        # Nút chuyển chế độ
        if self.mode == self.MODE_LOGIN:
            self.switch_to_register_btn.rect.y = 520
            self.switch_to_register_btn.draw(screen)
        else:
            self.switch_to_login_btn.rect.y = 600
            self.switch_to_login_btn.draw(screen)
        
        # Thông báo
        if self.error_message:
            error_bg = pygame.Surface((500, 40))
            error_bg.set_alpha(200)
            error_bg.fill(RED)
            screen.blit(error_bg, (SCREEN_WIDTH//2 - 250, 490))
            error_surface = FONT_SMALL.render(self.error_message, True, WHITE)
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH//2, 510))
            screen.blit(error_surface, error_rect)
        
        if self.success_message:
            success_bg = pygame.Surface((500, 40))
            success_bg.set_alpha(200)
            success_bg.fill(GREEN)
            screen.blit(success_bg, (SCREEN_WIDTH//2 - 250, 490))
            success_surface = FONT_SMALL.render(self.success_message, True, WHITE)
            success_rect = success_surface.get_rect(center=(SCREEN_WIDTH//2, 510))
            screen.blit(success_surface, success_rect)
        
        # Hướng dẫn
        guide_text = FONT_TINY.render("TAB: Chuyển ô nhập | ENTER: Xác nhận", True, GRAY)
        guide_rect = guide_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 25))
        screen.blit(guide_text, guide_rect)
    
    def get_password_display(self, password, show):
        """Hiển thị mật khẩu hoặc dấu •"""
        if show:
            return password
        return "•" * len(password)
    
    def draw_input_field(self, label, value, y, input_id, show_eye=False):
        """Vẽ ô nhập liệu hoàn chỉnh"""
        screen = pygame.display.get_surface()
        is_active = (self.active_input == input_id)

        # =========================
        # Label
        # =========================
        label_surface = FONT_MEDIUM.render(label, True, WHITE)
        screen.blit(label_surface, (SCREEN_WIDTH//2 - 160, y - 45))

        # =========================
        # Ô nhập
        # =========================
        rect = pygame.Rect(SCREEN_WIDTH//2 - 160, y, 320, 45)

        if is_active:
            color = GOLD
            border_width = 3

            # Glow effect
            glow = pygame.Surface((rect.width + 12, rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 215, 0, 60), glow.get_rect(), border_radius=10)
            screen.blit(glow, (rect.x - 6, rect.y - 6))
        else:
            color = GRAY
            border_width = 2

        pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=8)
        pygame.draw.rect(screen, color, rect, border_width, border_radius=8)

        # =========================
        # Text cuộn khi dài
        # =========================
        left_padding = 15
        right_padding = 50 if show_eye else 15
        max_width = rect.width - left_padding - right_padding

        display_text = value
        text_surface = FONT_MEDIUM.render(display_text, True, WHITE)

        while text_surface.get_width() > max_width and len(display_text) > 0:
            display_text = display_text[1:]
            text_surface = FONT_MEDIUM.render(display_text, True, WHITE)

        text_y = rect.y + (rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (rect.x + left_padding, text_y))

        # =========================
        # Cursor nhấp nháy
        # =========================
        if is_active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = rect.x + left_padding + text_surface.get_width()

            if cursor_x > rect.right - right_padding:
                cursor_x = rect.right - right_padding

            pygame.draw.line(
                screen,
                WHITE,
                (cursor_x, rect.y + 10),
                (cursor_x, rect.y + rect.height - 10),
                2
            )

        # Eye button (dùng ảnh)
        if show_eye:
            eye_rect = pygame.Rect(rect.right - 42, rect.y + 6, 35, 35)

            # nền nhẹ
            pygame.draw.rect(screen, (60, 60, 60), eye_rect, border_radius=6)

            if input_id == "password":
                is_showing = self.show_password
            else:
                is_showing = self.show_confirm_password

            # chọn icon
            if is_showing:
                eye_img = self.image_manager.get_eye(True)   # eye_open
            else:
                eye_img = self.image_manager.get_eye(False)  # eye_close

            if eye_img:
                eye_img = pygame.transform.scale(eye_img, (32, 32))
                img_rect = eye_img.get_rect(center=eye_rect.center)
                screen.blit(eye_img, img_rect)

            # border
            pygame.draw.rect(screen, GRAY, eye_rect, 1, border_radius=6)

            # lưu vùng click
            if input_id == "password":
                self.eye_btn_rect = eye_rect
            else:
                self.eye_confirm_rect = eye_rect

            # Lưu vùng click
            if input_id == "password":
                self.eye_btn_rect = eye_rect
            else:
                self.eye_confirm_rect = eye_rect
    
    def draw_flying_fruits(self, screen):
        """Vẽ hoa quả bay bằng ảnh"""
        for fruit in self.flying_fruits:
            fruit_img = self.fruit_images.get(fruit['type'])
            if fruit_img:
                rotated_img = pygame.transform.rotate(fruit_img, fruit['rotation'])
                rect = rotated_img.get_rect(center=(int(fruit['x']), int(fruit['y'])))
                screen.blit(rotated_img, rect)
