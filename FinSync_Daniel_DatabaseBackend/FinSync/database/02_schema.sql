-- FinSync: Step 2 - create the tables for the login and password-reset module
-- Run as root after 01_create_database.sql.

USE finsync;

-- Users table (columns from the 4.5 database design)
CREATE TABLE IF NOT EXISTS users (
    user_id        INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    first_name     VARCHAR(50)   NOT NULL,
    last_name      VARCHAR(50)   NOT NULL DEFAULT '',
    email          VARCHAR(255)  NOT NULL,
    password_hash  VARCHAR(255)  NOT NULL,   -- only the hash is stored, never the real password
    phone          VARCHAR(20)   NULL,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE (email)                           -- one account per email address
) ENGINE=InnoDB;

-- One row for every "Forgot Password" request
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_id    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id     INT UNSIGNED  NOT NULL,
    token_hash  CHAR(64)      NOT NULL,      -- SHA-256 hash of the token in the email link
    created_at  DATETIME      NOT NULL,
    expires_at  DATETIME      NOT NULL,      -- the link stops working after this
    used_at     DATETIME      NULL,          -- NULL until the link has been used
    PRIMARY KEY (token_id),
    UNIQUE (token_hash),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE                    -- deleting a user also deletes their tokens
) ENGINE=InnoDB;
