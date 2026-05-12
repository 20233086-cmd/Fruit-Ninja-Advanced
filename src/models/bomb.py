# src/models/bomb.py
import pygame
import random
import math
from src.config import *

class Bomb:
    """Lớp đại diện cho bom"""
    
    def __init__(self, x, y, vx, vy, image_manager):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 35
        self.gravity = 0.5
        self.damage = 1
        self.image_manager = image_manager
        
        # Lấy ảnh bomb từ thư mục bombs
        self.image = image_manager.get_image('bombs/bomb')
        
        # Lấy ảnh nổ từ effects
        self.explosion_img = image_manager.get_image('effects/explosion', default_color=RED, size=(80, 80))
        
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.is_exploded = False
        self.explosion_timer = 0
        self.has_damaged = False  # Thêm flag để chỉ gây sát thương 1 lần
    
    def update(self, time_scale=1.0):
        if not self.is_exploded:
            self.vx *= 0.99
            self.vy += self.gravity * time_scale
            self.x += self.vx * time_scale
            self.y += self.vy * time_scale
            self.rotation += self.rotation_speed * time_scale
        else:
            self.explosion_timer += 1
            return self.explosion_timer < 20
        return True
    
    def draw(self, screen):
        if self.is_exploded:
            # Vẽ hiệu ứng nổ - KHÔNG CÓ HITBOX
            if self.explosion_img:
                scale = 1.0
                if self.explosion_timer < 5:
                    scale = 0.5 + self.explosion_timer * 0.1
                elif self.explosion_timer > 15:
                    scale = 2.0 - (self.explosion_timer - 15) * 0.1
                else:
                    scale = 1.0
                
                size = int(80 * scale)
                scaled_img = pygame.transform.scale(self.explosion_img, (size, size))
                rect = scaled_img.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(scaled_img, rect)
            else:
                radius = 30 + self.explosion_timer
                alpha = max(0, 255 - self.explosion_timer * 15)
                color = (255, 100 - self.explosion_timer * 5, 0)
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
            return
        
        if self.image:
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            # Fallback vẽ bom đơn giản
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius, 3)
            pygame.draw.line(screen, RED, (self.x, self.y - self.radius), (self.x, self.y - self.radius - 15), 4)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y - self.radius - 15)), 6)
            pygame.draw.circle(screen, WHITE, (self.x - 12, self.y - 5), 5)
            pygame.draw.circle(screen, WHITE, (self.x + 12, self.y - 5), 5)
            pygame.draw.circle(screen, BLACK, (self.x - 12, self.y - 5), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 12, self.y - 5), 2)
    
    def explode(self):
        """Kích hoạt hiệu ứng nổ"""
        self.is_exploded = True
        self.explosion_timer = 0
        self.radius = 0  # Đặt radius = 0 để không còn hitbox
        print(f"💥 Bom nổ tại ({self.x}, {self.y})")
    
    def can_damage(self):
        """Kiểm tra xem bom có thể gây sát thương không"""
        return not self.is_exploded and not self.has_damaged
    
    def apply_damage(self):
        """Đánh dấu đã gây sát thương"""
        self.has_damaged = True
    
    def is_off_screen(self):
        if self.is_exploded:
            return self.explosion_timer >= 20
        return (self.y - self.radius > SCREEN_HEIGHT or 
                self.x + self.radius < 0 or 
                self.x - self.radius > SCREEN_WIDTH)
