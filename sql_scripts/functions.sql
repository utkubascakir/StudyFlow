

-- Login Fonksiyonu
CREATE OR REPLACE FUNCTION func_login(p_email VARCHAR, p_password VARCHAR) 
RETURNS TABLE(user_id INT, first_name VARCHAR, role VARCHAR, message TEXT) AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email AND user_password = p_password) THEN
        RETURN QUERY SELECT u.user_id, u.first_name, u.user_role, 'SUCCESS'::TEXT 
                     FROM users u WHERE u.email = p_email;
    ELSE
        RETURN QUERY SELECT -1, 'Yok'::VARCHAR, 'none'::VARCHAR, 'FAIL'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;



-- 1. KAYIT OLMA FONKSİYONU
CREATE OR REPLACE FUNCTION func_register_user(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_email VARCHAR,
    p_password VARCHAR
) RETURNS TEXT AS $$
BEGIN
    -- E-posta kontrolü: Zaten var mı?
    IF EXISTS (SELECT 1 FROM users WHERE email = p_email) THEN
        RETURN 'HATA: Bu e-posta adresi zaten kayıtlı!';
    END IF;

    -- Yeni kayıt ekle (Varsayılan rol: student)
    INSERT INTO users (first_name, last_name, email, user_password, user_role)
    VALUES (p_first_name, p_last_name, p_email, p_password, 'student');

    RETURN 'SUCCESS';
END;
$$ LANGUAGE plpgsql;



-- 2. TRIGGER: ŞİFRE UZUNLUK KONTROLÜ (Proje Madde 12 - İkinci Trigger)
-- Kullanıcı 4 karakterden kısa şifre belirleyemesin.
CREATE OR REPLACE FUNCTION trg_check_password_func() RETURNS TRIGGER AS $$
BEGIN
    IF LENGTH(NEW.user_password) < 4 THEN
        RAISE EXCEPTION 'Şifre en az 4 karakter olmalıdır!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_password
BEFORE INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION trg_check_password_func();



CREATE OR REPLACE FUNCTION func_user_stats(p_user_id INT, p_period_text VARCHAR) 
RETURNS TABLE(total_duration INTERVAL, total_sessions INT) AS $$
DECLARE
    v_cutoff_date TIMESTAMP; -- Başlangıç sınırını tutacak tarih
    v_count INT;
    v_total_time INTERVAL;
BEGIN
    -- 1. Önce kullanıcının ne kadarlık bir geçmiş istediğini hesapla
    -- Eğer 'all' gönderirse veya boş gönderirse sınır koyma 
    IF p_period_text IS NULL OR p_period_text = 'all' THEN
        v_cutoff_date := '2000-01-01 00:00:00'; -- Çok eski bir tarih
    ELSE
        -- Şimdiki zamandan (NOW) istenilen süreyi çıkar
        -- Örn: NOW() - '1 week'::INTERVAL
        v_cutoff_date := NOW() - p_period_text::INTERVAL;
    END IF;

    -- 2. Belirlenen tarihten (v_cutoff_date) SONRAKİ kayıtları say
    SELECT COUNT(*) INTO v_count 
    FROM reservations 
    WHERE user_id = p_user_id 
      AND status = 'completed'
      AND start_time >= v_cutoff_date; -- Sadece bu tarihten sonrakiler

    -- 3. Hiç kayıt yoksa 0 döndür
    IF v_count = 0 THEN
        v_total_time := '0 hours';
    
    -- 4. Kayıt varsa süreleri topla
    ELSE
        SELECT SUM(end_time - start_time) 
        INTO v_total_time
        FROM reservations 
        WHERE user_id = p_user_id 
          AND status = 'completed'
          AND start_time >= v_cutoff_date;
    END IF;

    -- 5. Sonucu döndür
    RETURN QUERY SELECT v_total_time, v_count;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION func_get_room_status(p_room_id INT, p_check_time TIMESTAMP)
RETURNS TABLE(
    table_id INT, 
    table_number INT, 
    status TEXT, 
    until_time TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        st.table_id,
        st.table_number,
        CASE 
            WHEN r.reservation_id IS NOT NULL THEN 'DOLU'
            ELSE 'BOŞ'
        END AS status,
        r.end_time AS until_time
    FROM study_tables st
    LEFT JOIN reservations r ON st.table_id = r.table_id 
        AND r.status = 'active'
        AND (p_check_time >= r.start_time AND p_check_time < r.end_time)
    WHERE st.room_id = p_room_id
    ORDER BY st.table_number;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION func_suggest_table(p_room_id INT, p_start_time TIMESTAMP, p_duration_hours INT) 
RETURNS TEXT AS $$
DECLARE
    -- Madde 11: RECORD ve CURSOR Tanımı
    rec_table RECORD;
    cur_tables CURSOR FOR SELECT table_id, table_number FROM study_tables WHERE room_id = p_room_id ORDER BY table_number;
    
    v_end_time TIMESTAMP;
    v_collision_count INT;
BEGIN
    v_end_time := p_start_time + (p_duration_hours || ' hours')::INTERVAL;

    OPEN cur_tables; -- Cursor'ı aç
    LOOP
        FETCH cur_tables INTO rec_table; -- Satır satır oku
        EXIT WHEN NOT FOUND; -- Kayıt bitince çık

        -- Bu masa için o saat aralığında çakışan rezervasyon var mı?
        SELECT COUNT(*) INTO v_collision_count
        FROM reservations
        WHERE table_id = rec_table.table_id
          AND status = 'active'
          AND (start_time < v_end_time AND end_time > p_start_time);

        -- Çakışma yoksa (0 ise) bu masayı öner ve döngüden çık
        IF v_collision_count = 0 THEN
            CLOSE cur_tables;
            RETURN 'Öneri: Masa ' || rec_table.table_number;
        END IF;

    END LOOP;
    
    CLOSE cur_tables;
    RETURN 'Maalesef, bu saatte uygun masa yok.';
END;
$$ LANGUAGE plpgsql;




-- Mevcut trigger zaten var, bu fonksiyon sadece sarmalayıcı (wrapper) olacak.
CREATE OR REPLACE FUNCTION func_create_reservation(
    p_user_id INT,
    p_table_id INT,
    p_start_time TIMESTAMP,
    p_end_time TIMESTAMP
) RETURNS TEXT AS $$
BEGIN
    -- Basit Insert işlemi
    -- Çakışma kontrolünü zaten 'trg_check_overlap_func' trigger'ı yapacak.
    INSERT INTO reservations (user_id, table_id, start_time, end_time, status)
    VALUES (p_user_id, p_table_id, p_start_time, p_end_time, 'active');

    RETURN 'SUCCESS';
EXCEPTION
    -- Trigger bir hata fırlatırsa (RAISE EXCEPTION) burası yakalar
    WHEN OTHERS THEN
        RETURN 'HATA: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;






--***********************************************************
--***********************************************************



CREATE OR REPLACE FUNCTION check_daily_limit_func() RETURNS TRIGGER AS $$
BEGIN

    IF EXISTS (
        SELECT 1 FROM reservations 
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


CREATE TRIGGER trg_check_daily_limit
BEFORE INSERT OR UPDATE ON reservations
FOR EACH ROW
EXECUTE FUNCTION check_daily_limit_func();




CREATE OR REPLACE FUNCTION check_overlap_func() RETURNS TRIGGER AS $$
BEGIN

    IF EXISTS (
        SELECT 1 FROM reservations
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

CREATE TRIGGER trg_prevent_double_booking
BEFORE INSERT OR UPDATE ON reservations
FOR EACH ROW
EXECUTE FUNCTION check_overlap_func();

--*********************************************************************
-- 1. Function to auto-complete past reservations
CREATE OR REPLACE FUNCTION complete_past_reservations() 
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    -- Update all active reservations where end_time has passed
    UPDATE reservations 
    SET status = 'completed'
    WHERE status = 'active' 
      AND end_time < NOW();
    
    -- Get number of rows updated
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;


-- 2. Smart View with dynamic status calculation
CREATE OR REPLACE VIEW reservations_with_status AS
SELECT 
    reservation_id,
    user_id,
    table_id,
    start_time,
    end_time,
    created_at,
    -- Dynamic status: if end_time passed, show 'completed' even if DB says 'active'
    CASE 
        WHEN status = 'cancelled' THEN 'cancelled'
        WHEN end_time < NOW() THEN 'completed'
        ELSE 'active'
    END AS status,
    status AS original_status  -- Keep original for reference
FROM reservations;



CREATE OR REPLACE VIEW view_all_reservations AS
SELECT 
    r.reservation_id,
    u.first_name || ' ' || u.last_name AS full_name,
    sr.room_name,
    st.table_number,
    r.start_time,
    r.end_time,
    r.status  -- Now uses dynamic status from reservations_with_status
FROM reservations_with_status r  -- Changed from 'reservations' to 'reservations_with_status'
JOIN users u ON r.user_id = u.user_id
JOIN study_tables st ON r.table_id = st.table_id
JOIN study_rooms sr ON st.room_id = sr.room_id
WHERE u.user_role='student';


--**************************
CREATE INDEX idx_reservations_user_id ON reservations(user_id);
CREATE INDEX idx_reservations_table_id ON reservations(table_id);




DROP USER IF EXISTS app_student;
DROP USER IF EXISTS app_admin;

-- Create student user (for regular students)
CREATE USER app_student WITH PASSWORD 'student_pass_2025';

-- Create admin user (for administrators)
CREATE USER app_admin WITH PASSWORD 'admin_pass_2025';


-- =====================================================
-- 2. GRANT PRIVILEGES FOR STUDENT USER (app_student)
-- =====================================================


-- Schema usage
GRANT USAGE ON SCHEMA public TO app_student;

-- TABLES: Students need to read/write specific tables

-- users table: Can INSERT (register), SELECT (login), but NOT UPDATE/DELETE
GRANT SELECT, INSERT ON users TO app_student;

-- study_rooms table: Only SELECT (view available rooms)
GRANT SELECT ON study_rooms TO app_student;

-- study_tables table: Only SELECT (view available tables)
GRANT SELECT ON study_tables TO app_student;

-- reservations table: Can INSERT, SELECT, UPDATE (for their own reservations)
GRANT SELECT, INSERT, UPDATE ON reservations TO app_student;

-- SEQUENCES: Need to use sequences for auto-increment
GRANT USAGE, SELECT ON SEQUENCE seq_user_id TO app_student;
GRANT USAGE, SELECT ON SEQUENCE reservations_reservation_id_seq TO app_student;

-- VIEWS: Students can view these
GRANT SELECT ON view_all_reservations TO app_student;
GRANT SELECT ON reservations_with_status TO app_student;

-- FUNCTIONS: Students need to execute these functions
GRANT EXECUTE ON FUNCTION func_login(VARCHAR, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_register_user(VARCHAR, VARCHAR, VARCHAR, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_user_stats(INT, VARCHAR) TO app_student;
GRANT EXECUTE ON FUNCTION func_get_room_status(INT, TIMESTAMP) TO app_student;
GRANT EXECUTE ON FUNCTION func_suggest_table(INT, TIMESTAMP, INT) TO app_student;
GRANT EXECUTE ON FUNCTION func_create_reservation(INT, INT, TIMESTAMP, TIMESTAMP) TO app_student;
GRANT EXECUTE ON FUNCTION complete_past_reservations() TO app_student;


-- =====================================================
-- 3. GRANT PRIVILEGES FOR ADMIN USER (app_admin)
-- =====================================================

-- Schema usage
GRANT USAGE ON SCHEMA public TO app_admin;

-- TABLES: Admins have full access to all tables
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON study_rooms TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON study_tables TO app_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON reservations TO app_admin;

-- SEQUENCES: Full access
GRANT USAGE, SELECT, UPDATE ON SEQUENCE seq_user_id TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE reservations_reservation_id_seq TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE study_rooms_room_id_seq TO app_admin;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE study_tables_table_id_seq TO app_admin;

-- VIEWS: Full access
GRANT SELECT ON view_all_reservations TO app_admin;
GRANT SELECT ON reservations_with_status TO app_admin;

-- FUNCTIONS: Execute all functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_admin;