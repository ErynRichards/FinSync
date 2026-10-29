-- =====================================================================
-- FinSync - Step 1: create the database and a limited application user
-- Owner: Daniel (Database, Flask & Password-Reset Backend)
--
-- Run this ONCE as the MySQL root user, e.g. in MySQL Workbench or:
--     mysql -u root -p < database/01_create_database.sql
--
-- BEFORE RUNNING: replace  CHANGE_ME_Strong_Pass_123!  below with your own
-- password, and put the same password in DB_PASSWORD in your .env file.
-- Never commit your real password to GitHub.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS finsync
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- A dedicated user so the Flask app does not run as root.
-- 'localhost' means it can only connect from the same computer.
CREATE USER IF NOT EXISTS 'finsync_app'@'localhost'
    IDENTIFIED BY 'CHANGE_ME_Strong_Pass_123!';

-- Only the privileges the app needs: read/write rows.
-- (No DROP, ALTER or GRANT - so a bug in the app cannot delete tables.)
GRANT SELECT, INSERT, UPDATE, DELETE ON finsync.* TO 'finsync_app'@'localhost';

FLUSH PRIVILEGES;
