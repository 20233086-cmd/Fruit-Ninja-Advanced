# src/ui/shop_screen.py
import pygame
import sys
from src.config import *
from src.ui.button import Button

class ShopScreen:
    """Cửa hàng mua/đổi vật phẩm"""
    
    def __init__(self, game_controller):
        self.game = game_controller
        self.running = True
        self.image_manager = game_controller.image_manager

        #CUỘN SHOP KHI NHIỀU KIẾM
        self.scroll_y = 0
        self.max_scroll = 0
        self.scroll_speed = 40
        
        # Danh sách kiếm có thể mua
        self.swords_for_sale = [
            {'type': 'basic', 'name': 'Kiếm Cơ Bản', 'price': 0, 'multiplier': 1.0, 'color': (192, 192, 192)},
            {'type': 'flame', 'name': 'Kiếm Lửa', 'price': 500, 'multiplier': 1.5, 'color': (255, 100, 0)},
            {'type': 'lightning', 'name': 'Kiếm Sét', 'price': 1000, 'multiplier': 2.0, 'color': (255, 255, 0)},
            {'type':'ice','name':'Kiếm Băng','price':1800,'multiplier':2.5,'color':(100,220,255)},
            {'type':'magic','name':'Kiếm Ma Thuật','price':3000,'multiplier':3.0,'color':(180,0,255)},
            {'type': 'azure_lightning_sword', 'name': 'Azure Lightning', 'price': 3500, 'multiplier': 3.2, 'color': (100, 180, 255)},
            {'type': 'dragon_fire_sword', 'name': 'Dragon Fire', 'price': 4000, 'multiplier': 3.5, 'color': (255, 80, 0)},
            {'type': 'frost_soul_sword', 'name': 'Frost Soul', 'price': 4200, 'multiplier': 3.7, 'color': (120, 220, 255)},
            {'type': 'jade_demon_sword', 'name': 'Jade Demon', 'price': 4500, 'multiplier': 4.0, 'color': (0, 255, 120)},
            {'type': 'legendary_relic_sword', 'name': 'Legendary Relic', 'price': 5000, 'multiplier': 4.5, 'color': (255, 215, 0)},
            {'type': 'nova_relic_sword', 'name': 'Nova Relic', 'price': 5500, 'multiplier': 5.0, 'color': (255, 0, 255)},
            {'type': 'stormborn_necro_sword', 'name': 'Stormborn Necro', 'price': 6000, 'multiplier': 5.5, 'color': (80, 80, 255)},
        ]
        
        # Tải ảnh kiếm
        self.sword_images = {}
        for sword in self.swords_for_sale:
            img = self.image_manager.get_sword(sword["type"])
            self.sword_images[sword['type']] = img
        
        # Tạo các nút hành động (MUA/ĐỔI)
        self.action_buttons = []
        for i, sword in enumerate(self.swords_for_sale):
            btn = Button(
                SCREEN_WIDTH//2 + 180, 
                200 + i * 90, 
                100, 50, 
                "Mua", 
                GREEN, GOLD, DARK_GRAY
            )
            btn.sword_index = i
            self.action_buttons.append(btn)
        
        self.close_btn = Button(SCREEN_WIDTH - 100, 50, 80, 40, "Đóng", RED, GOLD, DARK_GRAY)
        # thông báo popup
        self.message = ""
        self.message_color = WHITE
        self.message_timer = 0
    
    def show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_timer = 120   # hiện 2 giây (60 FPS)

    def run(self):
        """Chạy cửa hàng"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        
        return self.game
    
    def handle_events(self):
        """Xử lý sự kiện"""

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_DOWN:
                    self.scroll_y -= self.scroll_speed

                elif event.key == pygame.K_UP:
                    self.scroll_y += self.scroll_speed

            if event.type == pygame.MOUSEBUTTONDOWN:

                # click trái
                if event.button == 1:

                    for btn in self.action_buttons:
                        if btn.rect.collidepoint(event.pos):
                            sword = self.swords_for_sale[btn.sword_index]
                            self.handle_action(sword)

                    if self.close_btn.rect.collidepoint(event.pos):
                        self.running = False

                # lăn xuống
                elif event.button == 5:
                    self.scroll_y -= self.scroll_speed

                # lăn lên
                elif event.button == 4:
                    self.scroll_y += self.scroll_speed

            if event.type == pygame.MOUSEMOTION:
                for btn in self.action_buttons:
                    btn.is_hovered = btn.rect.collidepoint(event.pos)

                self.close_btn.is_hovered = self.close_btn.rect.collidepoint(event.pos)

        # Giới hạn cuộn
        self.scroll_y = min(0, self.scroll_y)
        self.scroll_y = max(-self.max_scroll, self.scroll_y)

    def handle_action(self, sword):
        sword_type = sword['type']
        price = sword['price']

        # đang dùng
        if sword_type == self.game.current_sword.type:
            self.show_message("Bạn đang dùng kiếm này!", YELLOW)
            return

        # đã mua -> đổi
        if sword_type in self.game.purchased_swords:

            if sword_type in self.game.swords:
                self.game.current_sword = self.game.swords[sword_type]

            if self.game.db_manager and self.game.db_manager.conn:
                self.game.db_manager.update_current_sword(
                    self.game.player_id, sword_type
                )

            self.show_message("Đổi kiếm thành công!", GREEN)
            return

        # mua mới
        if self.game.state.coins >= price:

            self.game.state.coins -= price
            self.game.purchased_swords.append(sword_type)

            if sword_type in self.game.swords:
                self.game.current_sword = self.game.swords[sword_type]

            if self.game.db_manager and self.game.db_manager.conn:
                self.game.db_manager.save_purchased_sword(
                    self.game.player_id, sword_type
                )
                self.game.db_manager.update_user_coins(
                    self.game.player_id, self.game.state.coins
                )
                self.game.db_manager.update_current_sword(
                    self.game.player_id, sword_type
                )

            self.show_message(
                f"Mua {sword['name']} thành công!",
                GREEN
            )

        else:
            self.show_message(
                f"Không đủ xu! Cần {price}",
                RED
            )
    
    # ================================
    # THAY TOÀN BỘ hàm draw(self)
    # UI đẹp hơn + căn chỉnh chuẩn hơn
    # ================================

    # CHỈ CẦN thay toàn bộ text không dấu trong hàm draw()

    def draw(self):
        """Vẽ cửa hàng đẹp hơn"""
        screen = pygame.display.get_surface()
        start_y = 180 + self.scroll_y
        item_height = 140
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(215)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        shop_rect = pygame.Rect(70, 40, SCREEN_WIDTH - 140, SCREEN_HEIGHT - 80)

        pygame.draw.rect(screen, (35, 35, 35), shop_rect, border_radius=18)
        pygame.draw.rect(screen, GOLD, shop_rect, 4, border_radius=18)

        # =============================
        # TIÊU ĐỀ
        # =============================
        title = FONT_LARGE.render("CỬA HÀNG KIẾM", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(title, title_rect)

        pygame.draw.line(screen, GOLD,
                        (SCREEN_WIDTH//2 - 250, 110),
                        (SCREEN_WIDTH//2 + 250, 110), 2)

        # =============================
        # COINS
        # =============================
        coins_text = FONT_MEDIUM.render(
            f"XU HIỆN CÓ: {self.game.state.coins}",
            True,
            (255, 220, 80)
        )
        screen.blit(coins_text, (100, 130))

        for i, sword in enumerate(self.swords_for_sale):

            y = start_y + i * item_height

            # bỏ qua item nằm ngoài màn hình
            shop_top = 255
            shop_bottom = SCREEN_HEIGHT - 150

            if y + 90 < shop_top or y > shop_bottom:
                continue

            is_owned = sword['type'] in self.game.purchased_swords
            is_equipped = sword['type'] == self.game.current_sword.type

            if is_equipped:
                bg = (25, 80, 25)
                btn_text = "ĐANG DÙNG"
                btn_color = GRAY
                status = "TRANG BỊ"
                status_color = GREEN

            elif is_owned:
                bg = (25, 55, 95)
                btn_text = "ĐỔI"
                btn_color = BLUE
                status = "ĐÃ MỞ KHÓA"
                status_color = CYAN

            else:
                bg = (55, 55, 55)
                btn_text = "MUA"
                btn_color = GREEN
                status = f"{sword['price']} XU"
                status_color = GOLD

            item_rect = pygame.Rect(100, y, SCREEN_WIDTH - 200, 90)

            pygame.draw.rect(screen, bg, item_rect, border_radius=14)
            pygame.draw.rect(screen, GRAY, item_rect, 2, border_radius=14)

            sword_img = self.sword_images.get(sword['type'])

            if sword_img is None:
                sword_img = self.image_manager.get_sword(sword['type'])
            if sword_img:
                screen.blit(sword_img, (120, y + 5))

            name = FONT_MEDIUM.render(sword['name'], True, WHITE)
            screen.blit(name, (210, y + 15))

            multi = FONT_SMALL.render(
                f"x{sword['multiplier']} điểm",
                True,
                CYAN
            )
            screen.blit(multi, (210, y + 48))

            st = FONT_SMALL.render(status, True, status_color)
            screen.blit(st, (520, y + 35))

            btn = self.action_buttons[i]
            btn.text = btn_text
            btn.color = btn_color
            btn.hover_color = GOLD
            btn.rect.x = SCREEN_WIDTH - 325
            btn.rect.y = y + 18
            btn.rect.width = 210
            btn.rect.height = 52

            btn.draw(screen)

        # =============================
        # NÚT ĐÓNG
        # =============================
        self.close_btn.text = "ĐÓNG"
        self.close_btn.rect.x = SCREEN_WIDTH - 195
        self.close_btn.rect.y = 55
        self.close_btn.rect.width = 100
        self.close_btn.rect.height = 45
        self.close_btn.draw(screen)

        # =============================
        # FOOTER
        # =============================
        guide = FONT_TINY.render(
            "ESC để đóng | MUA = mở khóa | ĐỔI = đổi kiếm",
            True,
            GRAY
        )
        guide_rect = guide.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 25))
        screen.blit(guide, guide_rect)

        # =============================
        # SCROLL BAR
        # =============================

        content_height = len(self.swords_for_sale) * item_height
        visible_height = SCREEN_HEIGHT - 250

        self.max_scroll = max(0, content_height - visible_height)

        if self.max_scroll > 0:

            bar_x = SCREEN_WIDTH - 90
            bar_y = 170
            bar_h = 460

            pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, 10, bar_h), border_radius=10)

            thumb_h = max(60, bar_h * visible_height / content_height)

            thumb_y = bar_y + (-self.scroll_y / self.max_scroll) * (bar_h - thumb_h)

            pygame.draw.rect(screen, GOLD, (bar_x, thumb_y, 10, thumb_h), border_radius=10)

        # =============================
        # THÔNG BÁO
        # =============================
        if self.message_timer > 0:

            self.message_timer -= 1

            msg_bg = pygame.Rect(
                SCREEN_WIDTH//2 - 220,
                SCREEN_HEIGHT - 80,
                440,
                45
            )

            pygame.draw.rect(screen, BLACK, msg_bg, border_radius=10)
            pygame.draw.rect(screen, self.message_color, msg_bg, 2, border_radius=10)

            msg = FONT_SMALL.render(
                self.message,
                True,
                self.message_color
            )

            msg_rect = msg.get_rect(center=msg_bg.center)
            screen.blit(msg, msg_rect)
