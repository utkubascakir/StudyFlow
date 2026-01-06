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