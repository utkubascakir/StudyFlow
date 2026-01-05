-- Temiz başlangıç: Tabloları boşalt ve ID sayaçlarını sıfırla
TRUNCATE TABLE reservations, study_tables, study_rooms, users RESTART IDENTITY CASCADE;

-- 1. KULLANICILAR (İlk 3 Admin, Kalanlar Öğrenci)
INSERT INTO users (first_name, last_name, email, user_password, user_role) VALUES
-- ADMINLER
('Utku', 'Başçakır', 'utku.bascakir@std.yildiz.edu.tr', 'UtkuBaşçakır123', 'admin'),
('Melih', 'Baykal', 'melih.baykal@std.yildiz.edu.tr', 'MelihBaykal123', 'admin'),
('Oğuzhan', 'Şen', 'oguzhan.sen@std.yildiz.edu.tr', 'OğuzhanŞen123', 'admin'),

-- ÖĞRENCİLER (Toplam 10 kayıt olması için)
('Fatma', 'Çelik', 'fatma.celik@std.yildiz.edu.tr', 'FatmaÇelik123', 'student'),
('Ali', 'Can', 'ali.can@std.yildiz.edu.tr', 'AliCan123', 'student'),
('Zeynep', 'Şahin', 'zeynep.sahin@std.yildiz.edu.tr', 'ZeynepŞahin123', 'student'),
('Mustafa', 'Öztürk', 'mustafa.ozturk@std.yildiz.edu.tr', 'MustafaÖztürk123', 'student'),
('Elif', 'Arslan', 'elif.arslan@std.yildiz.edu.tr', 'ElifArslan123', 'student'),
('Burak', 'Polat', 'burak.polat@std.yildiz.edu.tr', 'BurakPolat123', 'student'),
('Selin', 'Koç', 'selin.koc@std.yildiz.edu.tr', 'SelinKoç123', 'student');

-- 2. ODALAR
INSERT INTO study_rooms (room_name, capacity) VALUES
('Kütüphane Ana Salon', 50),
('Sessiz Oda A', 10),
('Sessiz Oda B', 10),
('Grup Çalışma 1', 6),
('Grup Çalışma 2', 6),
('Grup Çalışma 3', 4),
('Bilgisayar Lab', 20),
('7/24 Salonu', 30),
('Teras Çalışma', 15),
('Seminer Odası', 40);

-- 3. MASALAR (OTOMATİK OLUŞTURMA)
-- Her oda için kapasite kadar masa eklenir
INSERT INTO study_tables (room_id, table_number)
SELECT room_id, generate_series(1, capacity)
FROM study_rooms;

-- 4. REZERVASYONLAR
-- ID Sequence 10000'den başladığı varsayılarak:
-- 10000: Utku, 10001: Melih, 10002: Oğuzhan, 10003: Fatma...
INSERT INTO reservations (user_id, table_id, start_time, end_time, status) VALUES
(10001, 1, '2026-01-10 09:00', '2026-01-10 11:00', 'completed'), -- Melih (Kütüphane)
(10002, 55, '2026-01-10 12:00', '2026-01-10 14:00', 'completed'), -- Oğuzhan (Sessiz Oda A)
(10000, 1, '2026-01-11 09:00', '2026-01-11 10:00', 'active'),    -- Utku (Kütüphane)
(10003, 65, '2026-01-11 10:00', '2026-01-11 12:00', 'active'), -- Fatma (Sessiz Oda B)
(10004, 4, '2026-01-11 14:00', '2026-01-11 16:00', 'active'),  -- Ali
(10001, 5, '2026-01-12 09:00', '2026-01-12 12:00', 'active'),  -- Melih
(10005, 1, '2026-01-12 13:00', '2026-01-12 14:00', 'cancelled'), -- Zeynep
(10006, 75, '2026-01-13 10:00', '2026-01-13 11:00', 'active'), -- Mustafa
(10007, 90, '2026-01-13 15:00', '2026-01-13 17:00', 'active'), -- Elif
(10008, 100, '2026-01-14 08:00', '2026-01-14 10:00', 'active'); -- Burak