import pygame
import random
from src.config import *

class Particle:
    """Hạt cho hiệu ứng"""
    
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
    
    def update(self):
        """Cập nhật hạt"""
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, screen):
        """Vẽ hạt"""
        if self.age < self.lifetime:
            alpha = 255 * (1 - self.age / self.lifetime)
            color = tuple(min(255, c * alpha//255) for c in self.color)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

class ParticleManager:
    """Quản lý hiệu ứng hạt"""
    
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color=ORANGE):
        """Tạo hiệu ứng nổ"""
        for _ in range(20):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-5, 5)
            lifetime = random.randint(10, 20)
            self.particles.append(Particle(x, y, vx, vy, color, lifetime))
    
    def update(self):
        """Cập nhật tất cả hạt"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Vẽ tất cả hạt"""
        for particle in self.particles:
            particle.draw(screen)
