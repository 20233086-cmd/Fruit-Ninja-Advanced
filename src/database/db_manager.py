import mysql.connector
from src.config import DB_CONFIG

class DatabaseManager:
    """Quản lý kết nối và thao tác database"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Kết nối database"""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Kết nối database thành công!")
            self.create_tables()
        except Exception as e:
            print(f"❌ Không thể kết nối database: {e}")
            self.conn = None
    
    def create_tables(self):
        """Tạo bảng nếu chưa có"""
        if not self.conn:
            return
        
        # Bảng players
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                total_score INT DEFAULT 0,
                total_coins INT DEFAULT 0,
                highest_level INT DEFAULT 1,
                current_sword VARCHAR(50) DEFAULT 'basic',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bảng high_scores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS high_scores (
                id INT PRIMARY KEY AUTO_INCREMENT,
                player_id INT,
                score INT,
                level INT,
                coins_earned INT,
                play_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
            )
        """)
        
        # Bảng player_progress để lưu số sao
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_progress (
                id INT PRIMARY KEY AUTO_INCREMENT,
                player_id INT,
                level INT,
                stars INT DEFAULT 0,
                best_score INT DEFAULT 0,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                UNIQUE KEY unique_progress (player_id, level)
            )
        """)
        
        # Bảng player_items để lưu vật phẩm đã mua
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_items (
                id INT PRIMARY KEY AUTO_INCREMENT,
                player_id INT,
                item_type VARCHAR(50),
                item_name VARCHAR(50),
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
                UNIQUE KEY unique_item (player_id, item_type, item_name)
            )
        """)
        
        self.conn.commit()
        print("✅ Đã tạo/cập nhật các bảng")
    
    def authenticate_user(self, username, password):
        """Xác thực người dùng"""
        if not self.conn:
            return None
        
        self.cursor.execute(
            "SELECT id, username FROM players WHERE username = %s AND password = %s",
            (username, password)
        )
        result = self.cursor.fetchone()
        
        if result:
            return result[1], result[0]
        return None
    
    def register_user(self, username, password):
        """Đăng ký người dùng mới"""
        if not self.conn:
            return None
        
        try:
            self.cursor.execute(
                "INSERT INTO players (username, password) VALUES (%s, %s)",
                (username, password)
            )
            self.conn.commit()
            return username, self.cursor.lastrowid
        except mysql.connector.IntegrityError:
            return None
    
    def save_score(self, player_id, score, level, coins):
        """Lưu điểm số"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO high_scores (player_id, score, level, coins_earned) 
                VALUES (%s, %s, %s, %s)
            """, (player_id, score, level, coins))
            
            self.cursor.execute("""
                UPDATE players SET total_score = total_score + %s, total_coins = total_coins + %s 
                WHERE id = %s
            """, (score, coins, player_id))
            
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi lưu điểm: {e}")
    
    def get_high_scores(self, limit=10):
        """Lấy bảng xếp hạng"""
        if not self.conn:
            return []
        
        try:
            self.cursor.execute("""
                SELECT p.username, hs.score, hs.level, hs.play_date
                FROM high_scores hs
                JOIN players p ON hs.player_id = p.id
                ORDER BY hs.score DESC LIMIT %s
            """, (limit,))
            return self.cursor.fetchall()
        except:
            return []
    
    def get_user_coins(self, player_id):
        """Lấy số xu của người dùng"""
        if not self.conn:
            return 0
        
        try:
            self.cursor.execute(
                "SELECT total_coins FROM players WHERE id = %s",
                (player_id,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0
    
    def update_user_coins(self, player_id, coins):
        """Cập nhật số xu"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute(
                "UPDATE players SET total_coins = %s WHERE id = %s",
                (coins, player_id)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi cập nhật xu: {e}")
    
    def save_star_rating(self, player_id, level, stars):
        """Lưu số sao đạt được"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute(
                "SELECT stars FROM player_progress WHERE player_id = %s AND level = %s",
                (player_id, level)
            )
            result = self.cursor.fetchone()
            
            if result:
                old_stars = result[0]
                if stars > old_stars:
                    self.cursor.execute(
                        "UPDATE player_progress SET stars = %s WHERE player_id = %s AND level = %s",
                        (stars, player_id, level)
                    )
                    print(f"✅ Cập nhật sao level {level}: {old_stars} -> {stars}")
            else:
                self.cursor.execute(
                    "INSERT INTO player_progress (player_id, level, stars) VALUES (%s, %s, %s)",
                    (player_id, level, stars)
                )
                print(f"✅ Lưu sao mới level {level}: {stars}")
            
            self.conn.commit()
        except Exception as e:
            print(f"Lỗi lưu sao: {e}")
    
    def save_purchased_sword(self, player_id, sword_type):
        """Lưu kiếm đã mua"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute(
                "SELECT id FROM player_items WHERE player_id = %s AND item_type = 'sword' AND item_name = %s",
                (player_id, sword_type)
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    "INSERT INTO player_items (player_id, item_type, item_name) VALUES (%s, 'sword', %s)",
                    (player_id, sword_type)
                )
                self.conn.commit()
                print(f"✅ Đã lưu kiếm: {sword_type}")
        except Exception as e:
            print(f"Lỗi lưu kiếm: {e}")
    
    def get_purchased_swords(self, player_id):
        """Lấy danh sách kiếm đã mua"""
        if not self.conn:
            return ['basic']
        
        try:
            self.cursor.execute(
                "SELECT item_name FROM player_items WHERE player_id = %s AND item_type = 'sword'",
                (player_id,)
            )
            swords = [row[0] for row in self.cursor.fetchall()]
            if 'basic' not in swords:
                swords.append('basic')
            print(f"📋 Kiếm đã mua: {swords}")
            return swords
        except Exception as e:
            print(f"Lỗi lấy kiếm: {e}")
            return ['basic']
    
    def get_current_sword(self, player_id):
        """Lấy kiếm đang dùng"""
        if not self.conn:
            return 'basic'
        
        try:
            self.cursor.execute(
                "SELECT current_sword FROM players WHERE id = %s",
                (player_id,)
            )
            result = self.cursor.fetchone()
            if result and result[0]:
                return result[0]
        except:
            pass
        return 'basic'
    
    def update_current_sword(self, player_id, sword_type):
        """Cập nhật kiếm đang dùng"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute(
                "UPDATE players SET current_sword = %s WHERE id = %s",
                (sword_type, player_id)
            )
            self.conn.commit()
            print(f"✅ Đã cập nhật kiếm đang dùng: {sword_type}")
        except Exception as e:
            print(f"Lỗi cập nhật kiếm: {e}")
    
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

    def close(self):
        """Đóng kết nối"""
        if self.conn:
            self.cursor.close()
            self.conn.close()
