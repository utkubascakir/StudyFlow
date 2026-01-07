CREATE OR REPLACE VIEW view_all_reservations AS
SELECT 
    r.reservation_id,
    u.first_name || ' ' || u.last_name AS full_name,
    sr.room_name,
    st.table_number,
    r.start_time,
    r.end_time,
    r.status
FROM reservations r
JOIN users u ON r.user_id = u.user_id
JOIN study_tables st ON r.table_id = st.table_id
JOIN study_rooms sr ON st.room_id = sr.room_id;



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



-- Trigger Fonksiyonu
CREATE OR REPLACE FUNCTION check_overlap_func() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM reservations
        WHERE table_id = NEW.table_id
          AND status = 'active'
          AND (NEW.start_time < end_time AND NEW.end_time > start_time)
    ) THEN
        RAISE EXCEPTION 'ÇAKIŞMA VAR: Bu saat aralığında masa zaten dolu!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger Tanımı
CREATE TRIGGER trg_prevent_double_booking
BEFORE INSERT ON reservations
FOR EACH ROW
EXECUTE FUNCTION check_overlap_func();