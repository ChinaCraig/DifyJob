-- 创建数据库
CREATE DATABASE IF NOT EXISTS wechat_job CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE wechat_job;

-- 任务配置表
CREATE TABLE IF NOT EXISTS task_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interval_minutes INT DEFAULT 30 COMMENT '间隔时间(分钟)',
    is_active BOOLEAN DEFAULT FALSE COMMENT '是否启用',
    last_end_time DATETIME NULL COMMENT '最后结束时间',
    dify_api_key VARCHAR(255) NULL COMMENT 'Dify API Key',
    dify_url VARCHAR(500) DEFAULT 'http://localhost/v1/workflows/run' COMMENT 'Dify API URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务配置表';

-- 任务执行日志表
CREATE TABLE IF NOT EXISTS task_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interval_minutes INT NOT NULL COMMENT '间隔时间(分钟)',
    execute_time DATETIME NOT NULL COMMENT '执行时间',
    start_time DATETIME NOT NULL COMMENT '起始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    status VARCHAR(20) DEFAULT 'success' COMMENT '执行状态',
    response_data TEXT NULL COMMENT '响应数据',
    error_message TEXT NULL COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_execute_time (execute_time),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务执行日志表';

-- 插入默认配置
INSERT INTO task_configs (interval_minutes, is_active, dify_url) 
VALUES (30, FALSE, 'http://localhost/v1/workflows/run')
ON DUPLICATE KEY UPDATE id=id; 