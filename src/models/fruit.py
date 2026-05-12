import pygame
import math
import random
from src.config import *

class Fruit:
    """Lớp đại diện cho trái cây"""
    
    FRUIT_TYPES = {
        'apple': {'points': 10, 'color': RED, 'speed': 1.0},
        'orange': {'points': 10, 'color': ORANGE, 'speed': 1.0},
        'banana': {'points': 15, 'color': YELLOW, 'speed': 1.2},
        'watermelon': {'points': 20, 'color': GREEN, 'speed': 0.8},
        'coconut':    {'points': 25, 'color': BROWN,  'speed': 0.9},
        'pineapple':  {'points': 30, 'color': GOLD,   'speed': 1.1}
    }
    
    def __init__(self, x, y, vx, vy, fruit_type, image_manager):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.type = fruit_type
        self.radius = 35
        self.gravity = 0.5
        self.image_manager = image_manager
        self.points = self.FRUIT_TYPES[fruit_type]['points']
        self.is_sliced = False
        self.slice_angle = 0
        self.slice_time = 0
        
        # Lấy ảnh - dùng key đơn giản
        self.original_image = image_manager.get_image(fruit_type)
        if self.original_image:
            print(f"✅ Fruit {fruit_type}: đã lấy ảnh thành công")
        else:
            print(f"❌ Fruit {fruit_type}: không lấy được ảnh")
        
        # Hiệu ứng xoay
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-8, 8)
    
    def update(self, time_scale=1.0):
        """Cập nhật vị trí"""
        if not self.is_sliced:
            self.vx *= 0.99
            self.vy += self.gravity * time_scale
            self.x += self.vx * time_scale
            self.y += self.vy * time_scale
            self.rotation += self.rotation_speed * time_scale
        else:
            self.vy += self.gravity * 2
            self.x += self.vx
            self.y += self.vy
            self.slice_time += 1
        
        return not self.is_sliced
    
    def draw(self, screen):
        """Vẽ trái cây"""
        if not self.is_sliced and self.original_image:
            # Xoay và vẽ
            rotated_image = pygame.transform.rotate(self.original_image, self.rotation)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        elif not self.is_sliced:
            # Fallback: vẽ hình tròn
            color = self.FRUIT_TYPES[self.type]['color']
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
            # Vẽ chữ
            text = FONT_SMALL.render(self.type[0].upper(), True, WHITE)
            screen.blit(text, (self.x - 10, self.y - 10))
        else:
            # Vẽ hiệu ứng chém đôi
            if self.slice_time < 30:
                self.draw_sliced(screen)
    
    def draw_sliced(self, screen):
        """Vẽ trái cây bị chém đôi"""
        color = self.FRUIT_TYPES[self.type]['color']
        
        # Vẽ 2 nửa
        for offset in [-15, 15]:
            angle_rad = math.radians(self.slice_angle)
            dx = math.cos(angle_rad) * offset
            dy = math.sin(angle_rad) * offset
            pygame.draw.circle(screen, color, (int(self.x + dx), int(self.y + dy)), self.radius // 2)
            pygame.draw.circle(screen, WHITE, (int(self.x + dx), int(self.y + dy)), self.radius // 2, 2)
        
        # Tia lửa
        for i in range(8):
            angle = self.slice_angle + random.randint(-20, 20)
            end_x = self.x + math.cos(math.radians(angle)) * 25
            end_y = self.y + math.sin(math.radians(angle)) * 25
            pygame.draw.line(screen, GOLD, (self.x, self.y), (end_x, end_y), 2)
    
    def slice(self, angle):
        """Xử lý khi bị chém"""
        self.is_sliced = True
        self.slice_angle = angle
        self.vy = random.uniform(3, 6)
        self.vx = math.cos(math.radians(angle)) * random.uniform(5, 10)
    
    def is_off_screen(self):
        return (self.y - self.radius > SCREEN_HEIGHT or 
                self.x + self.radius < 0 or 
                self.x - self.radius > SCREEN_WIDTH or
                self.y + self.radius < 0)
