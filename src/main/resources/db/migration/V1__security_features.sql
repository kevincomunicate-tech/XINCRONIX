ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(64) NULL;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id BIGINT NOT NULL AUTO_INCREMENT,
    token_hash VARCHAR(64) NOT NULL,
    id_usuario INT NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_password_reset_token_hash (token_hash),
    KEY idx_password_reset_usuario (id_usuario)
);
