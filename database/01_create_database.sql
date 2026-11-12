-- FinSync: Step 1 - create the database and the app's MySQL user
-- Run once as root in MySQL Workbench (File > Open SQL Script > Execute).
-- Change the password below first, and use the same one for DB_PASSWORD in .env.

-- Create the MySQL database used by FinSync.
CREATE DATABASE IF NOT EXISTS finsync
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- The Flask app logs in as this user instead of root
CREATE USER IF NOT EXISTS 'finsync_app'@'localhost'
    IDENTIFIED BY 'CHANGE_ME_Strong_Pass_123!';

-- The app only needs to read and change rows, not create or delete tables
GRANT SELECT, INSERT, UPDATE, DELETE ON finsync.* TO 'finsync_app'@'localhost';

FLUSH PRIVILEGES;
