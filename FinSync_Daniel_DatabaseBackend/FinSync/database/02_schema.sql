-- =====================================================================
-- FinSync - Step 2: tables for the authentication module
-- Owner: Daniel (Database, Flask & Password-Reset Backend)
--
-- Run as root (or any user with CREATE privileges):
--     mysql -u root -p finsync < database/02_schema.sql
--
-- Contains only what the login / password-reset module needs:
--   1. users                  (from the FinSync 4.5 database design)
--   2. password_reset_tokens  (new - supports the password-reset feature)
-- The other finance tables (Accounts, Transactions, Categories, Budgets,
-- Savings_Goals, Notifications) are NOT created here; they belong to later
-- modules and reference users.user_id as their foreign key.
-- =====================================================================

USE finsync;

-- ---------------------------------------------------------------------
-- users
-- Columns follow the 4.5 database design (user_id, first_name, last_name,
-- email, password_hash, phone, created_at) plus updated_at.
-- The Sign Up screen has a single "Full Name" field; the backend splits it
-- into first_name / last_name (see app/users.py -> split_full_name).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id        INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    first_name     VARCHAR(50)     NOT NULL,
    last_name      VARCHAR(50)     NOT NULL DEFAULT '',
    email          VARCHAR(255)    NOT NULL,
    password_hash  VARCHAR(255)    NOT NULL,   -- hash only, NEVER the plain password
    phone          VARCHAR(20)     NULL,
    created_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_email UNIQUE (email)   -- one account per email address
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- password_reset_tokens
-- One row per "Forgot Password" request.
--   token_hash : SHA-256 of the random token. The raw token only exists in
--                the email link, so a leaked database cannot be used to
--                reset anyone's password.
--   expires_at : UTC time after which the link is rejected.
--   used_at    : NULL = unused. Set when the link is used (single-use) or
--                when another reset for the same user succeeds.
-- ON DELETE CASCADE: deleting a user removes their tokens.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_id       INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    user_id        INT UNSIGNED    NOT NULL,
    token_hash     CHAR(64)        NOT NULL,
    created_at     DATETIME        NOT NULL,   -- UTC, set by the app
    expires_at     DATETIME        NOT NULL,   -- UTC, set by the app
    used_at        DATETIME        NULL,       -- UTC, NULL until used
    CONSTRAINT pk_password_reset_tokens PRIMARY KEY (token_id),
    CONSTRAINT uq_prt_token_hash UNIQUE (token_hash),
    -- speeds up "how many reset requests has this user made recently?"
    INDEX idx_prt_user_created (user_id, created_at),
    CONSTRAINT fk_prt_user FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
