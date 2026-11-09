-- FinSync: Step 2 - create all the tables
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

-- Financial accounts belonging to each user (e.g. Cheque, Savings, Credit Card, Cash)
CREATE TABLE IF NOT EXISTS accounts (
    account_id       INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    user_id          INT UNSIGNED   NOT NULL,
    account_name     VARCHAR(100)   NOT NULL,
    account_type     VARCHAR(30)    NOT NULL,
    opening_balance  DECIMAL(12,2)  NOT NULL DEFAULT 0.00,  -- the balance when the account was added
    currency         CHAR(3)        NOT NULL DEFAULT 'ZAR', -- e.g. ZAR, USD
    created_at       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (account_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE                    -- deleting a user also deletes their accounts
) ENGINE=InnoDB;

-- How transactions are classified (shared by all users)
CREATE TABLE IF NOT EXISTS categories (
    category_id    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    category_name  VARCHAR(50)   NOT NULL,
    category_type  ENUM('income', 'expense') NOT NULL,
    PRIMARY KEY (category_id),
    UNIQUE (category_name)                   -- no duplicate category names
) ENGINE=InnoDB;

-- The user's income and expenses
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    account_id        INT UNSIGNED   NOT NULL,
    category_id       INT UNSIGNED   NOT NULL,
    description       VARCHAR(255)   NULL,
    amount            DECIMAL(12,2)  NOT NULL,              -- always positive; the type says if it's money in or out
    transaction_type  ENUM('income', 'expense') NOT NULL,
    transaction_date  DATE           NOT NULL,
    created_at        DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    CHECK (amount > 0),
    FOREIGN KEY (account_id) REFERENCES accounts (account_id)
        ON DELETE CASCADE,                   -- deleting an account also deletes its transactions
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON DELETE RESTRICT                   -- a category can't be deleted while transactions use it
) ENGINE=InnoDB;

-- Monthly budget for a category
CREATE TABLE IF NOT EXISTS budgets (
    budget_id      INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    user_id        INT UNSIGNED   NOT NULL,
    category_id    INT UNSIGNED   NOT NULL,
    budget_amount  DECIMAL(12,2)  NOT NULL,
    start_date     DATE           NOT NULL,
    end_date       DATE           NOT NULL,
    created_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (budget_id),
    CHECK (budget_amount > 0),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Record budget-exceeded notifications to prevent duplicates
CREATE TABLE IF NOT EXISTS budget_notification_history (
    notification_id  INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id          INT UNSIGNED  NOT NULL,
    budget_id        INT UNSIGNED  NOT NULL,
    budget_month     CHAR(7)       NOT NULL,   -- e.g. 2026-11
    created_at       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    UNIQUE KEY unique_budget_month (budget_id, budget_month),   -- one notification per budget per month
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (budget_id) REFERENCES budgets (budget_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Savings goals, e.g. "Holiday" or "New laptop"
CREATE TABLE IF NOT EXISTS savings_goals (
    goal_id         INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    user_id         INT UNSIGNED   NOT NULL,
    goal_name       VARCHAR(100)   NOT NULL,
    category        VARCHAR(50)    NULL,
    target_amount   DECIMAL(12,2)  NOT NULL,
    current_amount  DECIMAL(12,2)  NOT NULL DEFAULT 0.00,
    target_date     DATE           NOT NULL,
    status          VARCHAR(20)    NOT NULL DEFAULT 'active',   -- active or completed
    created_at      DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (goal_id),
    CHECK (target_amount > 0),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Each user's settings (one row per user)
CREATE TABLE IF NOT EXISTS user_settings (
    user_id                INT UNSIGNED  NOT NULL,
    theme                  VARCHAR(10)   NOT NULL DEFAULT 'light',  -- light or dark
    budget_notifications   BOOLEAN       NOT NULL DEFAULT TRUE,
    savings_notifications  BOOLEAN       NOT NULL DEFAULT TRUE,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Starting categories. INSERT IGNORE skips any that already exist,
-- so this script can be run again safely.
INSERT IGNORE INTO categories (category_name, category_type) VALUES
    ('Salary', 'income'),
    ('Groceries', 'expense'),
    ('Transport', 'expense'),
    ('Entertainment', 'expense'),
    ('Utilities', 'expense');
