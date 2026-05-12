# src/game/game_controller.py
import pygame
import random
import math
import time
import sys
from save_progress import ProgressManager
from src.config import *
from src.models.fruit import Fruit
from src.models.bomb import Bomb
from src.models.special_item import SpecialItem
from src.models.level import Level
from src.models.sword import Sword
from src.models.quest import Quest
from src.managers.sound_manager import SoundManager
from src.managers.image_manager import ImageManager
from src.managers.particle_manager import ParticleManager
from src.managers.collision_manager import CollisionManager

class GameState:
    """Trạng thái game"""
    
    def __init__(self, level_num=1):
        self.score = 0
        self.lives = 3  # 3 mạng
        self.coins = 0
        self.combo = 0
        self.combo_timer = 0
        self.double_score = False
        self.double_score_timer = 0
        self.slow_motion = False
        self.slow_motion_timer = 0
        self.game_over = False
        self.current_level = level_num
        self.start_time = time.time()
        self.time_left = LEVEL_CONFIG[level_num]['time']
        self.stars_earned = 0
        self.screen_shake = 0

class SliceEffect:
    """Hiệu ứng vết chém"""
    
    def __init__(self, points, color):
        self.points = points
        self.color = color
        self.lifetime = 18
        self.age = 0
        self.thickness = 8

    def update(self):
        self.age += 1
        return self.age < self.lifetime

    def draw(self, screen):
        if len(self.points) < 2:
            return

        alpha = max(0, 255 - self.age * 15)
        width = max(1, self.thickness - self.age // 2)

        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, self.color, self.points[i], self.points[i+1], width)
            pygame.draw.line(screen, WHITE, self.points[i], self.points[i+1], max(1, width//3))

class GameController:
    """Điều khiển chính của game"""
    
    def __init__(self, username, player_id, db_manager, level_num=1):
        self.username = username
        self.player_id = player_id
        self.db_manager = db_manager
        self.sound_manager = SoundManager()
        self.image_manager = ImageManager()
        self.particle_manager = ParticleManager()
        
        # Game objects
        self.fruits = []
        self.bombs = []
        self.special_items = []
        self.slice_effects = []
        self.state = GameState(level_num)
        
        # Game settings
        self.level_config = LEVEL_CONFIG[level_num]
        self.level = Level(level_num)
        
        # Load kiếm đã mua từ database
        self.purchased_swords = self.db_manager.get_purchased_swords(player_id)
        
        # Khởi tạo các loại kiếm (chỉ 1 lần)
        all_swords = Sword.get_all_swords()
        self.swords = {}

        # nạp toàn bộ kiếm, không chỉ kiếm đã mua
        for sword in all_swords:
            self.swords[sword.type] = sword
        
        # Lấy kiếm đang dùng
        current_sword_type = self.db_manager.get_current_sword(player_id)
        if current_sword_type in self.swords:
            self.current_sword = self.swords[current_sword_type]
        else:
            self.current_sword = self.swords['basic']
        
        # Lấy ảnh kiếm
        self.sword_images = {
            'basic': self.image_manager.get_sword('basic_sword'),
            'flame': self.image_manager.get_sword('flame_sword'),
            'lightning': self.image_manager.get_sword('lightning_sword'),
            'ice': self.image_manager.get_sword('ice_sword'),
            'magic': self.image_manager.get_sword('magic_sword')
        }
        
        print(f"⚔️ Kiếm đã mua: {list(self.swords.keys())}")
        print(f"⚔️ Kiếm đang dùng: {self.current_sword.name}")
        
        self.progress = ProgressManager()
        
        # Spawning
        self.spawn_timer = 0
        self.spawn_delay = 20
        
        # Slicing
        self.mouse_pressed = False
        self.mouse_points = []
        self.last_slice_time = 0
        
        # UI buttons
        self.sound_button_rect = pygame.Rect(SCREEN_WIDTH - 109, 0, 30, 30)
        self.music_button_rect = pygame.Rect(SCREEN_WIDTH - 40, 10, 30, 30)
        self.shop_button_rect = pygame.Rect(SCREEN_WIDTH - 160, 8, 44, 44)
        
        # Tải ảnh UI
        self.sound_on_img = self.image_manager.get_image('ui/sound_on', size=(50, 50))
        self.sound_off_img = self.image_manager.get_image('ui/sound_off', size=(50, 50))
        self.music_on_img = self.image_manager.get_image('ui/music_on', size=(50, 50))
        self.music_off_img = self.image_manager.get_image('ui/music_off', size=(50, 50))
        self.shop_img = self.image_manager.get_image('ui/shop_icon', size=(50, 50))

        # Load user coins
        self.state.coins = self.db_manager.get_user_coins(player_id)
        
        # Start music
        self.sound_manager.play_music()
        
        # Spawn vài trái cây ban đầu
        for _ in range(3):
            self.spawn_object()
        
        print(f"❤️ Bắt đầu game với {self.state.lives} mạng")
    
    def spawn_object(self):
        """Tạo vật thể mới từ dưới lên"""
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = SCREEN_HEIGHT - 30
        
        vx = random.uniform(-4, 4)
        vy = random.uniform(-18, -12)
        
        rand = random.random()
        
        if rand < self.level_config['special_chance']:
            item_type = random.choice(['double_score', 'extra_life', 'coin', 'slow_motion'])
            self.special_items.append(SpecialItem(x, y, item_type))
        elif rand < self.level_config['special_chance'] + self.level_config['bomb_chance']:
            self.bombs.append(Bomb(x, y, vx, vy, self.image_manager))
        else:
            fruit_type = random.choice(['apple', 'orange', 'banana', 'watermelon', 'coconut', 'pineapple'])
            fruit = Fruit(x, y, vx, vy, fruit_type, self.image_manager)
            self.fruits.append(fruit)
    
    def update_timers(self):
        """Cập nhật các timer"""
        elapsed = time.time() - self.state.start_time
        self.state.time_left = max(0, LEVEL_CONFIG[self.state.current_level]['time'] - int(elapsed))
        
        if self.state.time_left <= 0 and not self.state.game_over:
            self.state.game_over = True
            self.calculate_stars()
            self.save_game_result()
        
        if self.state.combo_timer > 0:
            self.state.combo_timer -= 1
            if self.state.combo_timer == 0:
                self.state.combo = 0
        
        if self.state.double_score_timer > 0:
            self.state.double_score_timer -= 1
            if self.state.double_score_timer == 0:
                self.state.double_score = False
        
        if self.state.slow_motion_timer > 0:
            self.state.slow_motion_timer -= 1
            if self.state.slow_motion_timer == 0:
                self.state.slow_motion = False
    
    def calculate_stars(self):
        """Tính số sao đạt được dựa trên ĐIỂM (score)"""
        score = self.state.score
        targets = LEVEL_CONFIG[self.state.current_level]
        
        print(f"📊 Điểm đạt được: {score}")
        print(f"🎯 Mục tiêu: 1⭐={targets['target_score_1star']}, 2⭐={targets['target_score_2star']}, 3⭐={targets['target_score_3star']}")
        
        if score >= targets['target_score_3star']:
            self.state.stars_earned = 3
            print(f"⭐ Đạt 3 sao! (cần {targets['target_score_3star']} điểm)")
        elif score >= targets['target_score_2star']:
            self.state.stars_earned = 2
            print(f"⭐⭐ Đạt 2 sao! (cần {targets['target_score_2star']} điểm)")
        elif score >= targets['target_score_1star']:
            self.state.stars_earned = 1
            print(f"⭐ Đạt 1 sao! (cần {targets['target_score_1star']} điểm)")
        else:
            self.state.stars_earned = 0
            print(f"❌ Chưa đạt sao! (cần {targets['target_score_1star']} điểm)")
        
        return self.state.stars_earned
    
    def process_slice(self, start_pos, end_pos):
        """Xử lý chém"""
        if not start_pos or not end_pos:
            return
        
        # Tính góc chém
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        
        # Thêm hiệu ứng vết chém
        self.slice_effects.append(
            SliceEffect([start_pos, end_pos], self.current_sword.color)
        )

        self.trigger_sword_effect(self.current_sword.type, end_pos)
        self.sound_manager.play_sfx('slice')
        
        # Kiểm tra chém trái cây
        fruits_to_remove = []
        for fruit in self.fruits[:]:
            dist = CollisionManager.point_to_line_distance(fruit.x, fruit.y, start_pos, end_pos)
            if dist < fruit.radius:
                fruits_to_remove.append(fruit)
                fruit.slice(angle)
                self.sound_manager.play_sfx('explosion')
                
                # Tính điểm cho trái cây
                fruit_points = fruit.points
                if self.state.double_score:
                    fruit_points *= 2
                fruit_points = int(fruit_points * self.current_sword.multiplier)
                
                self.state.score += fruit_points
                self.state.coins += fruit_points // 10
                self.state.combo += 1
                self.state.combo_timer = 60
                
                fruit_color = Fruit.FRUIT_TYPES[fruit.type]['color']
                self.particle_manager.create_explosion(fruit.x, fruit.y, fruit_color)
                
                if random.random() < 0.3:
                    self.state.coins += 5
                    self.sound_manager.play_sfx('coin')
        
        # Xóa trái cây đã chém
        for fruit in fruits_to_remove:
            if fruit in self.fruits:
                self.fruits.remove(fruit)
        
        # Kiểm tra chém bom - CHỈ BOM THẬT MỚI TÍNH
        bomb_hit = False
        for bomb in self.bombs[:]:
            if bomb_hit:
                break
            
            # CHỈ KIỂM TRA NẾU BOM CHƯA NỔ
            if hasattr(bomb, 'can_damage') and bomb.can_damage():
                dist = CollisionManager.point_to_line_distance(bomb.x, bomb.y, start_pos, end_pos)
                if dist < bomb.radius:
                    bomb_hit = True
                    bomb.apply_damage()
                    bomb.explode()
                    self.sound_manager.play_sfx('bomb')
                    self.state.lives -= 1
                    self.state.combo = 0
                    
                    print(f"💥 TRÚNG BOM! Mất 1 mạng. Còn {self.state.lives}/3 mạng")
                    
                    if self.state.lives <= 0:
                        print(f"💀 GAME OVER - Hết mạng!")
                        self.state.game_over = True
                        self.calculate_stars()
                        self.save_game_result()
                        return True
        
        # Kiểm tra chém vật phẩm
        for item in self.special_items[:]:
            dist = CollisionManager.point_to_line_distance(item.x, item.y, start_pos, end_pos)
            if dist < item.radius:
                self.special_items.remove(item)
                self.state = item.apply_effect(self.state)
                self.sound_manager.play_sfx('coin')
        
        if len(fruits_to_remove) > 0:
            print(f"🍎 Đã chém {len(fruits_to_remove)} trái cây! Điểm: {self.state.score}")
        
        return len(fruits_to_remove) > 0
    
    def save_game_result(self):
        """Lưu kết quả game"""
        # Lưu vào database nếu có
        if self.db_manager and self.db_manager.conn:
            self.db_manager.save_score(self.player_id, self.state.score, 
                                    self.state.current_level, self.state.coins)
            self.db_manager.update_user_coins(self.player_id, self.state.coins)
            self.db_manager.save_star_rating(self.player_id, self.state.current_level, self.state.stars_earned)
            
            # Mở khóa level tiếp theo nếu đạt ít nhất 1 sao
            if self.state.stars_earned >= 1 and self.state.current_level < 5:
                self.db_manager.unlock_level(self.player_id, self.state.current_level + 1)
        
        # Lưu vào file JSON
        self.progress.update_stars(self.state.current_level, self.state.stars_earned)
        print(f"✅ Đã lưu: Level {self.state.current_level} đạt {self.state.stars_earned} sao")
    
    def unlock_level(self, player_id, level):
        """Mở khóa level mới"""
        if not self.conn:
            return
        
        try:
            # Cập nhật highest_level cho người chơi
            self.cursor.execute(
                "UPDATE players SET highest_level = GREATEST(highest_level, %s) WHERE id = %s",
                (level, player_id)
            )
            self.conn.commit()
            print(f"🔓 Đã mở khóa level {level}")
        except Exception as e:
            print(f"Lỗi mở khóa level: {e}")

    def update(self):
        """Cập nhật game"""
        if self.state.game_over:
            return
        
        self.update_timers()
        
        time_scale = 0.5 if self.state.slow_motion else 1.0
        
        # Spawn objects
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            self.spawn_object()
            if random.random() < 0.4:
                self.spawn_object()
        
        # Update objects
        for fruit in self.fruits[:]:
            fruit.update(time_scale)
            if fruit.is_off_screen():
                self.fruits.remove(fruit)
        
        for bomb in self.bombs[:]:
            bomb.update(time_scale)
            # Xóa bom sau khi hiệu ứng nổ kết thúc
            if bomb.is_off_screen():
                self.bombs.remove(bomb)
        
        for item in self.special_items[:]:
            item.update()
            if item.is_off_screen():
                self.special_items.remove(item)
        
        # Update hiệu ứng
        self.particle_manager.update()
        self.slice_effects = [eff for eff in self.slice_effects if eff.update()]
    
    def draw(self):
        """Vẽ game"""
        offset_x = 0
        offset_y = 0

        if self.state.screen_shake > 0:
            self.state.screen_shake -= 1
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
        screen = pygame.display.get_surface()
        
        # Background với ảnh từ level
        bg_key = f'bg_{self.state.current_level}'
        bg_image = self.image_manager.get_image(bg_key, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(bg_image, (offset_x, offset_y))
        
        # Vẽ các vật thể
        for fruit in self.fruits:
            fruit.draw(screen)
        for bomb in self.bombs:
            bomb.draw(screen)
        for item in self.special_items:
            item.draw(screen, self.image_manager)
        
        # Vẽ hiệu ứng hạt
        self.particle_manager.draw(screen)
        
        # Vẽ hiệu ứng vết chém
        for effect in self.slice_effects:
            effect.draw(screen)
        
        # Vết chém hiện tại
        if self.mouse_pressed and len(self.mouse_points) > 1:
            for i in range(len(self.mouse_points) - 1):
                pygame.draw.line(screen, self.current_sword.color,
                               self.mouse_points[i], self.mouse_points[i+1], 8)
                pygame.draw.line(screen, WHITE,
                               self.mouse_points[i], self.mouse_points[i+1], 3)
        
        # UI
        self.draw_ui()
        
        # Game over
        if self.state.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Vẽ UI"""
        screen = pygame.display.get_surface()
        
        # Khung thông tin
        info_bg = pygame.Surface((300, 180))
        info_bg.set_alpha(128)
        info_bg.fill(BLACK)
        screen.blit(info_bg, (10, 10))
        
        # Hiển thị thông tin
        score_text = FONT_MEDIUM.render(f"Điểm: {self.state.score}", True, WHITE)
        coins_text = FONT_MEDIUM.render(f"Xu: {self.state.coins}", True, GOLD)
        # Text "Mạng:"
        lives_text = FONT_MEDIUM.render("Mạng:", True, WHITE)
        screen.blit(lives_text, (20, 100))

        heart_full = self.image_manager.get_heart(True)
        heart_empty = self.image_manager.get_heart(False)

        full_size = 48
        empty_size = 32

        x = 130
        y_full = 92        # ❤️ tim đỏ giữ nguyên
        y_empty = 102       # 🤍 tim rỗng xuống 10px

        for i in range(3):

            if i < self.state.lives:
                img = pygame.transform.scale(heart_full, (full_size, full_size))
                screen.blit(img, (x + i * 45, y_full))

            else:
                img = pygame.transform.scale(heart_empty, (empty_size, empty_size))
                screen.blit(img, (x + i * 45, y_empty))

        time_text = FONT_MEDIUM.render(f"Thời gian: {self.state.time_left}s", True, CYAN)
        
        screen.blit(score_text, (20, 20))
        screen.blit(coins_text, (20, 60))
        
        screen.blit(time_text, (20, 140))
        
        # Hiển thị level
        level_text = FONT_MEDIUM.render(f"Level {self.state.current_level}", True, GOLD)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        screen.blit(level_text, level_rect)
        
        # Thanh thời gian
        time_percent = self.state.time_left / LEVEL_CONFIG[self.state.current_level]['time']
        time_bar_width = int(400 * time_percent)
        time_bar_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 60, time_bar_width, 20)
        pygame.draw.rect(screen, CYAN, time_bar_rect)
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - 200, 60, 400, 20), 2)
        
        # Combo
        if self.state.combo > 1:
            combo_text = FONT_LARGE.render(f"{self.state.combo} COMBO!", True, GOLD)
            combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(combo_text, combo_rect)
        
        # Double score
        if self.state.double_score:
            ds_text = FONT_MEDIUM.render("DOUBLE SCORE!", True, GOLD)
            ds_rect = ds_text.get_rect(center=(SCREEN_WIDTH//2, 100))
            screen.blit(ds_text, ds_rect)
        
        # Vẽ nút âm thanh (dùng ảnh)
        if self.sound_manager.sfx_on:
            sound_img = self.sound_on_img
        else:
            sound_img = self.sound_off_img
        
        if sound_img:
            screen.blit(sound_img, self.sound_button_rect)
        else:
            # Fallback nếu không có ảnh
            pygame.draw.rect(screen, DARK_GRAY, self.sound_button_rect)
            sound_text = FONT_SMALL.render("🔊" if self.sound_manager.sfx_on else "🔇", True, WHITE)
            screen.blit(sound_text, (self.sound_button_rect.x + 5, self.sound_button_rect.y + 5))
        
        # Vẽ nút nhạc (dùng ảnh)
        if self.sound_manager.music_on:
            music_img = self.music_on_img
        else:
            music_img = self.music_off_img
        
        if music_img:
            screen.blit(music_img, self.music_button_rect)
        else:
            pygame.draw.rect(screen, DARK_GRAY, self.music_button_rect)
            music_text = FONT_SMALL.render("🎵" if self.sound_manager.music_on else "🎵❌", True, WHITE)
            screen.blit(music_text, (self.music_button_rect.x + 5, self.music_button_rect.y + 5))
        
        # Vẽ nút shop (dùng ảnh)
        if self.shop_img:
            #screen.blit(self.shop_img, self.shop_button_rect)
            pygame.draw.rect(screen, DARK_GRAY, self.shop_button_rect, border_radius=8)
            pygame.draw.rect(screen, GOLD, self.shop_button_rect, 2, border_radius=8)

            img_rect = self.shop_img.get_rect(center=self.shop_button_rect.center)
            screen.blit(self.shop_img, img_rect)
        else:
            pygame.draw.rect(screen, DARK_GRAY, self.shop_button_rect)
            shop_text = FONT_SMALL.render("🛒", True, WHITE)
            screen.blit(shop_text, (self.shop_button_rect.x + 5, self.shop_button_rect.y + 5))
    
    def draw_game_over(self):
        """Vẽ màn hình game over"""
        screen = pygame.display.get_surface()
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Tiêu đề
        result_text = FONT_LARGE.render("KẾT THÚC", True, GOLD)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(result_text, result_rect)
        
        # Điểm đạt được
        score_text = FONT_LARGE.render(f"{self.state.score} ĐIỂM", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(score_text, score_rect)
        
        # Xu kiếm được
        coins_text = FONT_MEDIUM.render(f"Xu nhận được: {self.state.coins}", True, GOLD)
        coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH//2, 240))
        screen.blit(coins_text, coins_rect)
        
        # Mục tiêu điểm
        targets = LEVEL_CONFIG[self.state.current_level]
        target_3star = targets['target_score_3star']
        target_2star = targets['target_score_2star']
        target_1star = targets['target_score_1star']
        
        # =============================
        # MỤC TIÊU DÙNG 1 ẢNH SAO
        # =============================
        star_small = pygame.transform.scale(
            self.image_manager.get_star(True), (32, 32)
        )

        base_y = 285
        start_x = SCREEN_WIDTH // 2 - 250

        title = FONT_SMALL.render("Mục tiêu:", True, GRAY)
        screen.blit(title, (start_x, base_y))

        x = start_x + 95

        # -------- 1 sao ----------
        num1 = FONT_SMALL.render("1", True, GOLD)
        screen.blit(num1, (x, base_y))

        screen.blit(star_small, (x + 18, base_y - 3))

        txt1 = FONT_SMALL.render(f"= {target_1star}", True, WHITE)
        screen.blit(txt1, (x + 48, base_y))

        # -------- 2 sao ----------
        x += 150

        num2 = FONT_SMALL.render("2", True, GOLD)
        screen.blit(num2, (x, base_y))

        screen.blit(star_small, (x + 18, base_y - 3))

        txt2 = FONT_SMALL.render(f"= {target_2star}", True, WHITE)
        screen.blit(txt2, (x + 48, base_y))

        # -------- 3 sao ----------
        x += 150

        num3 = FONT_SMALL.render("3", True, GOLD)
        screen.blit(num3, (x, base_y))

        screen.blit(star_small, (x + 18, base_y - 3))

        txt3 = FONT_SMALL.render(f"= {target_3star}", True, WHITE)
        screen.blit(txt3, (x + 48, base_y))
        
        # Vẽ sao
        # =========================
        # VẼ SAO BẰNG ẢNH
        # =========================
        star_img = self.image_manager.get_star(True)
        empty_star_img = self.image_manager.get_star(False)

        star_size = 65
        gap = 25

        fill_star = pygame.transform.scale(star_img, (star_size, star_size))
        empty_star = pygame.transform.scale(empty_star_img, (star_size, star_size))

        total_width = star_size * 3 + gap * 2
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        star_y = 340

        for i in range(3):
            x = start_x + i * (star_size + gap)

            if i < self.state.stars_earned:
                screen.blit(fill_star, (x, star_y))
            else:
                screen.blit(empty_star, (x, star_y))
        
        # Thông báo số sao
        if self.state.stars_earned == 3:
            msg = f"Tuyệt vời! 3 SAO - {self.state.score}/{target_3star} điểm"
            msg_color = GOLD
        elif self.state.stars_earned == 2:
            msg = f"Tốt! 2 SAO - {self.state.score}/{target_2star} điểm"
            msg_color = YELLOW
        elif self.state.stars_earned == 1:
            msg = f"Đạt yêu cầu! 1 SAO - {self.state.score}/{target_1star} điểm"
            msg_color = WHITE
        else:
            msg = f"Chưa đạt sao. Cần {target_1star - self.state.score} điểm nữa!"
            msg_color = RED
        
        msg_surface = FONT_MEDIUM.render(msg, True, msg_color)
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH//2, 430))
        screen.blit(msg_surface, msg_rect)
        
        # Nút bấm
        from src.ui.button import Button
        
        # Kiểm tra xem có level tiếp theo không
        next_level = self.state.current_level + 1

        # Chỉ mở nút next khi đạt ít nhất 1 sao
        has_next_level = (
            self.state.stars_earned >= 1
            and next_level <= 5
        )
        
        # Vị trí các nút
        if has_next_level:
            # Có next level: 3 nút
            replay_btn = Button(SCREEN_WIDTH//2 - 220, 510, 120, 50, "Chơi lại", GREEN, GOLD, DARK_GRAY)
            next_btn = Button(SCREEN_WIDTH//2 - 85, 510, 170, 50, f"LEVEL {next_level}", BLUE, GOLD, DARK_GRAY)
            back_btn = Button(SCREEN_WIDTH//2 + 100, 510, 195, 50, "Chọn cấp độ", ORANGE, GOLD, DARK_GRAY)
            
            replay_btn.draw(screen)
            next_btn.draw(screen)
            back_btn.draw(screen)
            
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if replay_btn.rect.collidepoint(event.pos):
                            waiting = False
                            self.__init__(self.username, self.player_id, self.db_manager, self.state.current_level)
                            return True
                        
                        if next_btn.rect.collidepoint(event.pos):
                            waiting = False
                            self.__init__(self.username, self.player_id, self.db_manager, next_level)
                            return True
                        
                        if back_btn.rect.collidepoint(event.pos):
                            waiting = False
                            return False
                
                pygame.display.flip()
                pygame.time.Clock().tick(FPS)
            
            return True
            
        else:
            # Không có next level (đã qua level 3): 2 nút
            replay_btn = Button(SCREEN_WIDTH//2 - 140, 510, 120, 50, "Chơi lại", GREEN, GOLD, DARK_GRAY)
            back_btn = Button(SCREEN_WIDTH//2 + 20, 510, 195, 50, "Chọn cấp độ", BLUE, GOLD, DARK_GRAY)
            
            replay_btn.draw(screen)
            back_btn.draw(screen)
            
            # Hiển thị thông báo hoàn thành game
            complete_text = FONT_MEDIUM.render("Chúc mừng! Bạn đã hoàn thành tất cả cấp độ!", True, GOLD)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 490))
            screen.blit(complete_text, complete_rect)
            
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if replay_btn.rect.collidepoint(event.pos):
                            waiting = False
                            self.__init__(self.username, self.player_id, self.db_manager, self.state.current_level)
                            return True
                        
                        if back_btn.rect.collidepoint(event.pos):
                            waiting = False
                            return False
                
                pygame.display.flip()
                pygame.time.Clock().tick(FPS)
            
            return True
    
    def handle_events(self):
        """Xử lý sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_s:
                    self.open_shop()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.sound_button_rect.collidepoint(event.pos):
                        self.sound_manager.toggle_sfx()
                    elif self.music_button_rect.collidepoint(event.pos):
                        self.sound_manager.toggle_music()
                    elif self.shop_button_rect.collidepoint(event.pos):
                        self.open_shop()
                    else:
                        self.mouse_pressed = True
                        self.mouse_points = [event.pos]
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
                    self.mouse_points = []
            
            if event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    current_pos = event.pos
                    if self.mouse_points:
                        last_pos = self.mouse_points[-1]
                        dist = ((current_pos[0] - last_pos[0])**2 + (current_pos[1] - last_pos[1])**2)**0.5
                        if dist > 5:
                            self.process_slice(last_pos, current_pos)
                    self.mouse_points.append(current_pos)
                    if len(self.mouse_points) > 20:
                        self.mouse_points.pop(0)
        
        return True
    
    def open_shop(self):
        """Mở cửa hàng"""
        from src.ui.shop_screen import ShopScreen
        shop = ShopScreen(self)
        shop.run()
        self.draw_ui()

    def run(self):
        """Chạy game loop"""
        clock = pygame.time.Clock()
        running = True
        should_continue = True
        
        while running and should_continue:
            running = self.handle_events()
            self.update()
            self.draw()
            
            if self.state.game_over:
                should_continue = self.draw_game_over()
                if not should_continue:
                    running = False
            
            clock.tick(FPS)
        
        return self.state.stars_earned
    
    def trigger_sword_effect(self, sword_type, pos):
        fx = Sword.EFFECTS[sword_type]

        self.state.screen_shake = fx["shake"]

        p = fx["particle"]

        if p == "fire":
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 80, 0))

        elif p == "dragon_fire":
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 50, 0))
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 180, 0))
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 255, 100))

        elif p == "electric_blue":
            self.particle_manager.create_explosion(pos[0], pos[1], (80, 180, 255))
            self.particle_manager.create_explosion(pos[0], pos[1], (0, 120, 255))

        elif p == "ice":
            self.particle_manager.create_explosion(pos[0], pos[1], (180, 240, 255))
            self.state.slow_motion = True
            self.state.slow_motion_timer = 100

        elif p == "frost_soul":
            self.particle_manager.create_explosion(pos[0], pos[1], (150, 220, 255))
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 255, 255))
            self.state.slow_motion = True
            self.state.slow_motion_timer = 120

        elif p == "jade":
            self.particle_manager.create_explosion(pos[0], pos[1], (0, 255, 120))

        elif p == "gold_burst":
            self.particle_manager.create_explosion(pos[0], pos[1], (255, 215, 0))
            self.state.double_score = True
            self.state.double_score_timer = 150

        elif p == "nova":
            for _ in range(6):
                self.particle_manager.create_explosion(pos[0], pos[1], (255, 0, 255))

        elif p == "dark_storm":
            self.particle_manager.create_explosion(pos[0], pos[1], (80, 80, 255))
            self.particle_manager.create_explosion(pos[0], pos[1], (30, 30, 30))

        elif p == "magic":
            self.particle_manager.create_explosion(pos[0], pos[1], (200, 0, 255))
            self.state.double_score = True
            self.state.double_score_timer = 120
