# run.py - Đặt ở thư mục gốc
import sys
import os

# Thêm đường dẫn
sys.path.insert(0, os.path.dirname(__file__))

# Chạy game
from src.main import main

if __name__ == "__main__":
    main()
