import pygame
import random
from src.config import *

class SpecialItem:
    """Vật phẩm đặc biệt"""

    ITEM_TYPES = {
        'double_score': {'duration': 300, 'effect': 'double_score'},
        'extra_life': {'duration': 0, 'effect': 'extra_life'},
        'coin': {'duration': 0, 'effect': 'coin'},
        'slow_motion': {'duration': 300, 'effect': 'slow_motion'}
    }

    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.radius = 30

        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-15, -11)

        self.gravity = 0.45
        self.lifetime = 220
        self.duration = self.ITEM_TYPES[item_type]['duration']

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

    def draw(self, screen, image_manager=None):
        """Vẽ item bằng ảnh thật"""

        if image_manager:
            img = image_manager.get_image(
                f"items/{self.type}",
                size=(75, 75)
            )

            if img:
                rect = img.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(img, rect)
                return

        # fallback nếu thiếu ảnh
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return self.y - self.radius > SCREEN_HEIGHT or self.lifetime <= 0

    def apply_effect(self, game_state):

        effect = self.ITEM_TYPES[self.type]['effect']

        if effect == 'double_score':
            game_state.double_score = True
            game_state.double_score_timer = self.duration

        elif effect == 'extra_life':
            game_state.lives += 1

        elif effect == 'coin':
            game_state.coins += 50

        elif effect == 'slow_motion':
            game_state.slow_motion = True
            game_state.slow_motion_timer = self.duration

        return game_state
