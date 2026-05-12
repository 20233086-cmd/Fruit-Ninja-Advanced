# src/ui/button.py
import pygame
from src.config import *

class Button:
    """Lớp nút bấm"""
    
    def __init__(self, x, y, width, height, text, color=WHITE, hover_color=GOLD, bg_color=DARK_GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.bg_color = bg_color
        self.is_hovered = False
        self.level_num = None
        self.image = None  # Thêm ảnh cho nút
    
    def handle_event(self, event):
        """Xử lý sự kiện click"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
    
    def draw(self, screen):
        """Vẽ nút"""
        # Màu nền
        bg = self.bg_color
        text_color = self.hover_color if self.is_hovered else self.color
        border_color = self.hover_color if self.is_hovered else self.color
        
        # Vẽ bóng đổ
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, BLACK, shadow_rect)
        
        # Vẽ nền
        pygame.draw.rect(screen, bg, self.rect)
        # Vẽ viền
        pygame.draw.rect(screen, border_color, self.rect, 3)
        
        # Vẽ ảnh nếu có
        if self.image:
            img_rect = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, img_rect)
        elif self.text:
            # Vẽ chữ
            lines = self.text.split('\n')
            y_offset = 0
            for line in lines:
                text_surface = FONT_MEDIUM.render(line, True, text_color)
                text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + y_offset))
                screen.blit(text_surface, text_rect)
                y_offset += 30
        
        # Hiệu ứng hover
        if self.is_hovered:
            highlight = pygame.Surface((self.rect.width, self.rect.height))
            highlight.set_alpha(50)
            highlight.fill((255, 255, 255))
            screen.blit(highlight, self.rect)
