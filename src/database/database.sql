-- Tạo database
CREATE DATABASE IF NOT EXISTS fruit_ninja_db;
USE fruit_ninja_db;

-- =====================================================
-- Bảng người chơi
-- =====================================================
CREATE TABLE IF NOT EXISTS players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    total_score INT DEFAULT 0,
    total_coins INT DEFAULT 0,
    highest_level INT DEFAULT 1,
    current_sword VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Bảng lưu điểm cao
-- =====================================================
CREATE TABLE IF NOT EXISTS high_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT,
    score INT,
    level INT,
    coins_earned INT,
    play_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- =====================================================
-- Bảng lưu tiến trình (số sao của từng level)
-- =====================================================
CREATE TABLE IF NOT EXISTS player_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT,
    level INT,
    stars INT DEFAULT 0,
    best_score INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    UNIQUE KEY unique_progress (player_id, level)
);

-- =====================================================
-- Bảng lưu vật phẩm đã mua
-- =====================================================
CREATE TABLE IF NOT EXISTS player_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT,
    item_type VARCHAR(50),
    item_name VARCHAR(50),
    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    UNIQUE KEY unique_item (player_id, item_type, item_name)
);

-- =====================================================
-- Bảng nhiệm vụ
-- =====================================================
CREATE TABLE IF NOT EXISTS quests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quest_name VARCHAR(100),
    quest_description TEXT,
    required_score INT,
    reward_coins INT,
    reward_item VARCHAR(50)
);

-- =====================================================
-- Thêm dữ liệu mẫu cho nhiệm vụ
-- =====================================================
INSERT INTO quests (quest_name, quest_description, required_score, reward_coins, reward_item) VALUES
('Tân thủ', 'Đạt 100 điểm', 100, 50, NULL),
('Cao thủ', 'Đạt 500 điểm', 500, 100, 'flame'),
('Huyền thoại', 'Đạt 1000 điểm', 1000, 200, 'lightning')
ON DUPLICATE KEY UPDATE 
    quest_name = VALUES(quest_name),
    quest_description = VALUES(quest_description),
    required_score = VALUES(required_score),
    reward_coins = VALUES(reward_coins),
    reward_item = VALUES(reward_item);

-- =====================================================
-- Thêm dữ liệu mẫu cho người chơi (tùy chọn)
-- =====================================================
-- Tài khoản mặc định: username: admin, password: 123456
INSERT INTO players (username, password, total_coins, highest_level, current_sword) VALUES
('admin', '123456', 2000, 1, 'basic')
ON DUPLICATE KEY UPDATE 
    username = VALUES(username);

-- =====================================================
-- Thêm dữ liệu mẫu cho vật phẩm (tùy chọn)
-- =====================================================
-- Mặc định mỗi người chơi có kiếm cơ bản
INSERT INTO player_items (player_id, item_type, item_name) 
SELECT id, 'sword', 'basic' FROM players WHERE NOT EXISTS (
    SELECT 1 FROM player_items WHERE player_id = players.id AND item_name = 'basic'
);

-- =====================================================
-- Tạo view cho bảng xếp hạng
-- =====================================================
CREATE OR REPLACE VIEW v_leaderboard AS
SELECT 
    p.username,
    p.total_score,
    p.total_coins,
    p.highest_level,
    (SELECT SUM(stars) FROM player_progress WHERE player_id = p.id) as total_stars
FROM players p
ORDER BY p.total_score DESC
LIMIT 10;

-- =====================================================
-- Tạo trigger tự động cập nhật highest_level
-- =====================================================
DELIMITER $$
CREATE TRIGGER update_highest_level
AFTER INSERT ON player_progress
FOR EACH ROW
BEGIN
    UPDATE players 
    SET highest_level = GREATEST(highest_level, NEW.level)
    WHERE id = NEW.player_id;
END$$
DELIMITER ;

-- =====================================================
-- Kiểm tra dữ liệu
-- =====================================================
SELECT '✅ Database initialized successfully!' AS Status;
SELECT * FROM players;
SELECT * FROM quests;
