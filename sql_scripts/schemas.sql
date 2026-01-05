CREATE SEQUENCE seq_user_id START 10000 INCREMENT 1;

-- 1. TABLO: KULLANICILAR (USERS)
CREATE TABLE users (
    user_id INT PRIMARY KEY DEFAULT nextval('seq_user_id'),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_role VARCHAR(20) DEFAULT 'student' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_user_role CHECK (user_role IN ('admin', 'student'))
);

-- 2. TABLO: ÇALIŞMA ODALARI (STUDY_ROOMS)
CREATE TABLE study_rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    
    CONSTRAINT chk_capacity_positive CHECK (capacity > 0)
);

-- 3. TABLO: MASALAR (STUDY_TABLES)
CREATE TABLE study_tables (
    table_id SERIAL PRIMARY KEY, -- Teknik yönetim için (Kodlama kolaylığı)
    room_id INT REFERENCES study_rooms(room_id) ON DELETE CASCADE,
    table_number INT NOT NULL,   -- Kullanıcının gördüğü numara (Örn: 5)
    is_available BOOLEAN DEFAULT TRUE,

    -- Masa numarası pozitif olmalı
    CONSTRAINT chk_table_num_pos CHECK (table_number > 0),

    CONSTRAINT uq_room_table_no UNIQUE (room_id, table_number)
);

-- 4. TABLO: REZERVASYONLAR (RESERVATIONS)
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    table_id INT REFERENCES study_tables(table_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_res_status CHECK (status IN ('active', 'completed', 'cancelled')),
    CONSTRAINT chk_time_valid CHECK (end_time > start_time)
);