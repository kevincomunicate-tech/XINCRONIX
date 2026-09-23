CREATE TABLE IF NOT EXISTS login_verification_codes (
    id BIGINT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    code_hash VARCHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_login_verification_user (id_usuario),
    KEY idx_login_verification_usuario (id_usuario)
);
