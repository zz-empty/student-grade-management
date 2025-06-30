-- 创建学生成绩表
CREATE TABLE scores (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男','女') NOT NULL,
    score1 FLOAT CHECK (score1 >= 0 AND score1 <= 100),
    score2 FLOAT CHECK (score2 >= 0 AND score2 <= 100),
    score3 FLOAT CHECK (score3 >= 0 AND score3 <= 100),
    INDEX idx_name (name),
    INDEX idx_gender (gender)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建账户信息表
CREATE TABLE accounts (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    permission ENUM('admin','user') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 插入测试学生数据
INSERT INTO scores (student_id, name, gender, score1, score2, score3) VALUES
('S001', '秦始皇', '男', 85, 92, 78),
('S002', '武则天', '女', 92, 88, 95),
('S003', '李世民', '男', 78, 85, 90),
('S004', '朱元璋', '男', 88, 76, 92),
('S005', '李清照', '女', 95, 89, 93),
('S006', '曹操', '男', 82, 90, 85),
('S007', '岳飞', '男', 90, 85, 88),
('S008', '花木兰', '女', 87, 92, 90),
('S009', '诸葛亮', '男', 93, 88, 91),
('S010', '杨玉环', '女', 85, 90, 87);

-- 插入账户数据（密码使用SHA-256加密）
INSERT INTO accounts (username, password, permission) VALUES
('admin', SHA2('admin123', 256), 'admin'),
('teacher1', SHA2('teacher123', 256), 'admin'),
('student1', SHA2('student123', 256), 'user'),
('student2', SHA2('password', 256), 'user');

-- 创建视图：学生总分排名
CREATE VIEW student_rankings AS
SELECT 
    student_id,
    name,
    gender,
    score1,
    score2,
    score3,
    (score1 + score2 + score3) AS total_score,
    RANK() OVER (ORDER BY (score1 + score2 + score3) DESC) AS ranking
FROM scores;
