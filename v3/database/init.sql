-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- 设置存储引擎和字符集
SET default_storage_engine = InnoDB;
SET NAMES utf8mb4;

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
    permission ENUM('admin','user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL DEFAULT NULL,
    INDEX idx_permission (permission)
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

-- 创建统计函数
DELIMITER //

-- 获取科目统计信息
CREATE FUNCTION get_subject_stats(subject INT)
RETURNS JSON
BEGIN
    DECLARE result JSON;
    
    SELECT JSON_OBJECT(
        'average', AVG(CASE subject
            WHEN 1 THEN score1
            WHEN 2 THEN score2
            WHEN 3 THEN score3
        END),
        'max', MAX(CASE subject
            WHEN 1 THEN score1
            WHEN 2 THEN score2
            WHEN 3 THEN score3
        END),
        'min', MIN(CASE subject
            WHEN 1 THEN score1
            WHEN 2 THEN score2
            WHEN 3 THEN score3
        END)
    ) INTO result
    FROM scores;
    
    RETURN result;
END //

-- 更改密码存储过程
CREATE PROCEDURE change_user_password(
    IN p_username VARCHAR(50),
    IN p_new_password VARCHAR(100)
BEGIN
    UPDATE accounts 
    SET password = SHA2(p_new_password, 256)
    WHERE username = p_username;
END //

DELIMITER ;

-- 创建事件：定期清理日志
CREATE EVENT IF NOT EXISTS clean_old_logs
ON SCHEDULE EVERY 1 WEEK
DO
    PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 7 DAY);

-- 创建触发器：记录账户最后登录时间
CREATE TRIGGER before_account_login
BEFORE UPDATE ON accounts
FOR EACH ROW
    SET NEW.last_login = CURRENT_TIMESTAMP;