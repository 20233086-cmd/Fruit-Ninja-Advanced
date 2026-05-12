import pygame
from src.config import SOUNDS_PATH
import os

class SoundManager:
    """Quản lý âm thanh"""
    
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_on = True
        self.sfx_on = True
        self.load_sounds()
    
    def load_sounds(self):
        """Tải các file âm thanh"""
        sound_files = {
            'slice': 'slice.wav',
            'bomb': 'bomb.wav',
            'explosion': 'explosion.wav',
            'coin': 'coin.wav',
            'level_up': 'level_up.wav'
        }
        
        for name, filename in sound_files.items():
            path = os.path.join(SOUNDS_PATH, filename)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(self.sfx_volume)
    
    def play_sfx(self, name):
        """Chơi hiệu ứng âm thanh"""
        if self.sfx_on and name in self.sounds:
            self.sounds[name].play()
    
    def play_music(self):
        """Chơi nhạc nền"""
        if self.music_on:
            music_path = os.path.join(SOUNDS_PATH, 'background_music.mp3')
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1)
    
    def stop_music(self):
        """Dừng nhạc nền"""
        pygame.mixer.music.stop()
    
    def toggle_music(self):
        """Bật/tắt nhạc nền"""
        self.music_on = not self.music_on
        if self.music_on:
            self.play_music()
        else:
            self.stop_music()
    
    def toggle_sfx(self):
        """Bật/tắt hiệu ứng âm thanh"""
        self.sfx_on = not self.sfx_on
        volume = self.sfx_volume if self.sfx_on else 0
        for sound in self.sounds.values():
            sound.set_volume(volume)
