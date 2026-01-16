-- 1. SEQUENCES
CREATE SEQUENCE seq_user_id START 10000 INCREMENT 1;


-- 2. Record kullanımı içn tanımı
CREATE TYPE table_record AS (
    table_id INT,
    table_number INT,
    status TEXT,
    until_time TIMESTAMP
);


-- 3. TABLES

-- USERS TABLE
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

-- STUDY ROOMS TABLE
CREATE TABLE study_rooms (
    room_id SERIAL PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    CONSTRAINT chk_capacity_positive CHECK (capacity > 0)
);

-- STUDY TABLES
CREATE TABLE study_tables (
    table_id SERIAL PRIMARY KEY,
    room_id INT REFERENCES study_rooms(room_id) ON DELETE CASCADE,
    table_number INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_table_num_pos CHECK (table_number > 0),
    CONSTRAINT uq_room_table_no UNIQUE (room_id, table_number)
);

-- RESERVATIONS TABLE
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    table_id INT REFERENCES study_tables(table_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_res_status CHECK (status IN ('active', 'completed', 'cancelled')),
    CONSTRAINT chk_time_valid CHECK (end_time > start_time)
);

-- INDEXES
CREATE INDEX idx_reservations_user_id ON reservations(user_id);
CREATE INDEX idx_reservations_table_id ON reservations(table_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_time_range ON reservations(start_time, end_time);


-- 4. Trigger Fonksiyonları

-- Password Trigger
CREATE OR REPLACE FUNCTION trg_check_password_func() 
RETURNS TRIGGER AS $$
BEGIN
    IF LENGTH(NEW.user_password) < 4 THEN
        RAISE EXCEPTION 'Şifre en az 4 karakter olmalıdır.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Günlük Limit Trigger
CREATE OR REPLACE FUNCTION check_daily_limit_func() 
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM reservations 
        WHERE user_id = NEW.user_id 
          AND status = 'active'
          AND DATE(start_time) = DATE(NEW.start_time) 
          AND reservation_id != COALESCE(NEW.reservation_id, -1)
    ) THEN
        RAISE EXCEPTION 'GÜNLÜK LİMİT: Günde sadece 1 kez rezervasyon yapabilirsiniz!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Reservation Çakışma Trigger
CREATE OR REPLACE FUNCTION check_overlap_func() 
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM reservations
        WHERE table_id = NEW.table_id
          AND status = 'active'
          AND reservation_id != COALESCE(NEW.reservation_id, -1)  
          AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        RAISE EXCEPTION 'ÇAKIŞMA VAR: Bu saat aralığında masa zaten dolu!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- 5. Trigger fonksiyonlarını tetikleyen Triggerlar

CREATE TRIGGER trg_validate_password
BEFORE INSERT ON users 
FOR EACH ROW 
EXECUTE FUNCTION trg_check_password_func();

CREATE TRIGGER trg_check_daily_limit
BEFORE INSERT OR UPDATE ON reservations 
FOR EACH ROW 
EXECUTE FUNCTION check_daily_limit_func();

CREATE TRIGGER trg_prevent_double_booking
BEFORE INSERT OR UPDATE ON reservations 
FOR EACH ROW 
EXECUTE FUNCTION check_overlap_func();


-- 6. Functions

-- User Login
CREATE OR REPLACE FUNCTION func_login(
    p_email VARCHAR, 
    p_password VARCHAR
) 
RETURNS TABLE(user_id INT, first_name VARCHAR, role VARCHAR, message TEXT) 
AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM users 
        WHERE email = p_email 
          AND user_password = p_password
    ) THEN
        RETURN QUERY 
        SELECT u.user_id, u.first_name, u.user_role, 'SUCCESS'::TEXT 
        FROM users u 
        WHERE u.email = p_email;
    ELSE
        RETURN QUERY 
        SELECT -1, 'Yok'::VARCHAR, 'none'::VARCHAR, 'FAIL'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- User Registration
CREATE OR REPLACE FUNCTION func_register_user(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_email VARCHAR,
    p_password VARCHAR
) 
RETURNS TEXT AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email) THEN
        RETURN 'HATA: Bu e-posta adresi zaten kayıtlı!';
    END IF;

    INSERT INTO users (first_name, last_name, email, user_password, user_role)
    VALUES (p_first_name, p_last_name, p_email, p_password, 'student');

    RETURN 'SUCCESS';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'HATA: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- User istatistikleri
CREATE OR REPLACE FUNCTION func_user_stats(
    p_user_id INT, 
    p_period_text VARCHAR
) 
RETURNS TABLE(total_duration INTERVAL, total_sessions INT) 
AS $$
DECLARE
    v_cutoff_date TIMESTAMP;
    v_count INT;
    v_total_time INTERVAL;
BEGIN

    IF p_period_text IS NULL OR p_period_text = 'all' THEN
        v_cutoff_date := '2000-01-01 00:00:00'; -- Zaman belirtilmemişse çok eski bir zaman
    ELSE
        v_cutoff_date := NOW() - p_period_text::INTERVAL;
    END IF;

    SELECT COUNT(*) INTO v_count 
    FROM reservations 
    WHERE user_id = p_user_id 
      AND status = 'completed'
      AND start_time >= v_cutoff_date;

    IF v_count = 0 THEN
        v_total_time := '0 hours';
    ELSE
        SELECT SUM(end_time - start_time) INTO v_total_time
        FROM reservations 
        WHERE user_id = p_user_id 
          AND status = 'completed'
          AND start_time >= v_cutoff_date;
    END IF;

    RETURN QUERY SELECT v_total_time, v_count;
END;
$$ LANGUAGE plpgsql;

-- Get Room Status
CREATE OR REPLACE FUNCTION func_get_room_status(
    p_room_id INT, 
    p_check_time TIMESTAMP
)
RETURNS TABLE(
    table_id INT, 
    table_number INT, 
    status TEXT, 
    until_time TIMESTAMP
) AS $$
DECLARE
    cur_tables CURSOR FOR 
        SELECT 
            st.table_id,
            st.table_number,
            CASE 
                WHEN r.reservation_id IS NOT NULL THEN 'DOLU'
                ELSE 'BOŞ'
            END AS status,
            r.end_time AS until_time
        FROM study_tables st
        LEFT JOIN reservations r 
            ON st.table_id = r.table_id 
            AND r.status = 'active'
            AND (p_check_time >= r.start_time AND p_check_time < r.end_time)
        WHERE st.room_id = p_room_id
        ORDER BY st.table_number;
    v_row table_record;
BEGIN

    FOR v_row IN cur_tables LOOP
        func_get_room_status.table_id     := v_row.table_id;
        func_get_room_status.table_number := v_row.table_number;
        func_get_room_status.status       := v_row.status;
        func_get_room_status.until_time   := v_row.until_time;
        
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- Create Reservation
CREATE OR REPLACE FUNCTION func_create_reservation(
    p_user_id INT,
    p_table_id INT,
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP
) 
RETURNS TEXT AS $$
BEGIN
    INSERT INTO reservations (user_id, table_id, start_time, end_time, status)
    VALUES (p_user_id, p_table_id, p_start_time, p_end_time, 'active');
    RETURN 'SUCCESS';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'HATA: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Complete Reservations
CREATE OR REPLACE FUNCTION complete_past_reservations() 
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE reservations 
    SET status = 'completed'
    WHERE status = 'active' 
      AND end_time < NOW();
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;


-- 7. VIEWS

-- View with Calculated Status
CREATE OR REPLACE VIEW reservations_with_status AS
SELECT 
    reservation_id, 
    user_id, 
    table_id, 
    start_time, 
    end_time, 
    created_at,
    CASE 
        WHEN status = 'cancelled' THEN 'cancelled'
        WHEN end_time < NOW() THEN 'completed'    --Reservation güncellenmemişse bile tamamlanmışsa completed gibi göster
        ELSE 'active'
    END AS status,
    status AS original_status
FROM reservations;

-- Reservation Information
CREATE OR REPLACE VIEW view_all_reservations AS
SELECT 
    r.reservation_id,
    u.first_name || ' ' || u.last_name AS full_name,
    sr.room_name,
    st.table_number,
    r.start_time,
    r.end_time,
    r.status
FROM reservations_with_status r                 --Durumları ayarlanmış reservationlara göre tüm reservationları göster
JOIN users u ON r.user_id = u.user_id
JOIN study_tables st ON r.table_id = st.table_id
JOIN study_rooms sr ON st.room_id = sr.room_id
WHERE u.user_role = 'student';


-- 8. ROLES AND PERMISSIONS

-- Create Roles
CREATE USER app_student WITH PASSWORD 'student_pass_2025';
CREATE USER app_admin WITH PASSWORD 'admin_pass_2025';

-- STUDENT PERMISSIONS
GRANT USAGE ON SCHEMA public TO app_student;

-- Table Permissions
GRANT SELECT, INSERT ON users TO app_student;
GRANT SELECT ON study_rooms TO app_student;
GRANT SELECT ON study_tables TO app_student;
GRANT SELECT, INSERT, UPDATE ON reservations TO app_student;

-- Sequence Permissions
GRANT USAGE, SELECT ON SEQUENCE seq_user_id TO app_student;
GRANT USAGE, SELECT ON SEQUENCE reservations_reservation_id_seq TO app_student;

-- View Permissions
GRANT SELECT ON view_all_reservations TO app_student;
GRANT SELECT ON reservations_with_status TO app_student;

-- Function Permissions
GRANT EXECUTE ON FUNCTION func_login(VARCHAR, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_register_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_user_stats(INT, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_get_room_status(INT, TIMESTAMP) TO app_student;
GRANT EXECUTE ON FUNCTION func_create_reservation(INT, INT, TIMESTAMP, TIMESTAMP) TO app_student;
GRANT EXECUTE ON FUNCTION complete_past_reservations() TO app_student;


-- ADMIN PERMISSIONS
GRANT USAGE ON SCHEMA public TO app_admin;

-- Table Permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON study_rooms TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON study_tables TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON reservations TO app_admin;

-- Sequence Permissions
GRANT USAGE, SELECT, UPDATE ON SEQUENCE seq_user_id TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE reservations_reservation_id_seq TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE study_rooms_room_id_seq TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE study_tables_table_id_seq TO app_admin;

-- View Permissions
GRANT SELECT ON view_all_reservations TO app_admin;
GRANT SELECT ON reservations_with_status TO app_admin;

-- Function Permissions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_admin;
