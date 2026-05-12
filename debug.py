# debug.py - Đặt trong thư mục gốc để kiểm tra ảnh
import pygame
import os
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Debug - Kiểm tra ảnh")

# Đường dẫn assets
ASSETS_PATH = "assets/images/"

def check_images():
    print("=== KIỂM TRA FILE ẢNH ===")
    
    # Danh sách cần kiểm tra
    image_paths = [
        ("fruits/apple.png", "Táo"),
        ("fruits/orange.png", "Cam"),
        ("fruits/banana.png", "Chuối"),
        ("fruits/watermelon.png", "Dưa hấu"),
        ("bombs/bomb.png", "Bom"),
        ("background/bg_level1.jpg", "Background 1"),
        ("background/bg_level2.jpg", "Background 2"),
        ("background/bg_level3.jpg", "Background 3"),
    ]
    
    found = []
    not_found = []
    
    for path, name in image_paths:
        full_path = os.path.join(ASSETS_PATH, path)
        if os.path.exists(full_path):
            found.append((name, full_path))
            print(f"✅ Tìm thấy: {name} - {full_path}")
        else:
            not_found.append((name, full_path))
            print(f"❌ Không tìm thấy: {name} - {full_path}")
    
    print(f"\nTổng cộng: {len(found)} file tìm thấy, {len(not_found)} file không tìm thấy")
    
    # Hiển thị ảnh tìm thấy
    if found:
        print("\n=== HIỂN THỊ ẢNH ===")
        y = 50
        for name, path in found[:5]:  # Chỉ hiển thị 5 ảnh đầu
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (100, 100))
                screen.blit(img, (50, y))
                text = pygame.font.Font(None, 24).render(name, True, (255, 255, 255))
                screen.blit(text, (160, y + 40))
                y += 110
            except Exception as e:
                print(f"Lỗi hiển thị {name}: {e}")
        
        pygame.display.flip()
        
        # Chờ 5 giây
        pygame.time.wait(5000)
    
    return found, not_found

if __name__ == "__main__":
    found, not_found = check_images()
    
    if not found:
        print("\n⚠️ Không tìm thấy file ảnh nào!")
        print("Tạo thư mục cấu trúc:")
        print("assets/images/fruits/apple.png")
        print("assets/images/fruits/orange.png")
        print("assets/images/fruits/banana.png")
        print("assets/images/fruits/watermelon.png")
        print("assets/images/bombs/bomb.png")
        print("assets/images/background/bg_level1.jpg")
    
    pygame.quit()
    sys.exit()
