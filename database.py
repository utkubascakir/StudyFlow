import psycopg2
from datetime import datetime

class Database:
    def __init__(self):
        self.db_config = {
            "dbname": "StudyFlow",
            "user": "postgres",
            "password": "123",  
            "host": "localhost",
            "port": "5432"
        }
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("Veritabanı bağlantısı başarılı!")
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")

    # --- 1. LOGIN İŞLEMLERİ (Madde 11: SQL Fonksiyonu Kullanımı) ---
    def login(self, email, password):
        try:
            cur = self.conn.cursor()
            # func_login fonksiyonunu çağırıyoruz
            cur.execute("SELECT * FROM func_login(%s, %s)", (email, password))
            user = cur.fetchone()
            cur.close()
            # Dönüş: (user_id, first_name, role, message)
            return user
        except Exception as e:
            print(f"Login Hatası: {e}")
            return None

    # --- 2. ODA VE MASA DURUMLARI (Grid View İçin) ---
    def get_rooms(self):
        """Arayüzdeki Dropdown'ı doldurmak için odaları çeker."""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, room_name, capacity FROM study_rooms")
            rooms = cur.fetchall()
            cur.close()
            return rooms
        except Exception as e:
            print(f"Oda Getirme Hatası: {e}")
            return []

    def get_room_status(self, room_id, check_time):
        """
        Grid View'daki kartların renklerini belirler.
        func_get_room_status SQL fonksiyonunu kullanır.
        """
        try:
            cur = self.conn.cursor()
            # check_time bir datetime objesi olmalı
            cur.execute("SELECT * FROM func_get_room_status(%s, %s)", (room_id, check_time))
            results = cur.fetchall()
            cur.close()
            # Dönüş: [(table_id, table_number, 'DOLU'/'BOŞ', until_time), ...]
            return results
        except Exception as e:
            print(f"Durum Sorgu Hatası: {e}")
            return []

    # --- 3. REZERVASYON İŞLEMLERİ (Madde 4 & 12: Insert ve Trigger) ---
    def create_reservation(self, user_id, table_id, start_time, end_time):
        """
        Yeni rezervasyon ekler.
        Eğer çakışma varsa Trigger devreye girer ve hata fırlatır.
        """
        try:
            cur = self.conn.cursor()
            query = """
                INSERT INTO reservations (user_id, table_id, start_time, end_time, status)
                VALUES (%s, %s, %s, %s, 'active')
            """
            cur.execute(query, (user_id, table_id, start_time, end_time))
            self.conn.commit() # Değişikliği kaydet
            cur.close()
            return "SUCCESS"
        except Exception as e:
            self.conn.rollback() # Hata olursa işlemi geri al
            # Trigger'dan gelen hatayı yakala ve temizle
            error_msg = str(e)
            if "ÇAKIŞMA VAR" in error_msg:
                return "HATA: Seçtiğiniz saat aralığında bu masa dolu!"
            return f"Beklenmedik Hata: {error_msg}"

    def cancel_reservation(self, reservation_id):
        """Madde 4: Update/Delete işlemi (Status'u iptal yapar)"""
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE reservations SET status = 'cancelled' WHERE reservation_id = %s", (reservation_id,))
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"İptal Hatası: {e}")
            return False

    # --- 4. ÖNERİ SİSTEMİ (Madde 11: Cursor/Record Kullanımı) ---
    def get_suggestion(self, room_id, start_time, duration):
        try:
            cur = self.conn.cursor()
            # func_suggest_table fonksiyonunu çağırır
            cur.execute("SELECT func_suggest_table(%s, %s, %s)", (room_id, start_time, duration))
            result = cur.fetchone()[0] # Tek bir metin döner
            cur.close()
            return result
        except Exception as e:
            return f"Öneri Hatası: {e}"

    # --- 5. İSTATİSTİKLER (Madde 10 & 11: Aggregate ve Fonksiyon) ---
    def get_user_stats(self, user_id, period):
        """
        period: '1 week', '1 month', 'all'
        func_user_stats SQL fonksiyonunu kullanır.
        """
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM func_user_stats(%s, %s)", (user_id, period))
            result = cur.fetchone()
            cur.close()
            # Dönüş: (Interval Süre, Toplam Oturum Sayısı)
            return result
        except Exception as e:
            print(f"İstatistik Hatası: {e}")
            return None

    # --- 6. EXCEPT SORGUSU (Madde 9: Küme İşlemleri) ---
    def get_available_tables_list(self, room_id):
        """
        Hızlı seçim menüsü için sadece boş masaları getirir.
        EXCEPT kullanımı buradadır.
        """
        try:
            cur = self.conn.cursor()
            query = """
                SELECT table_number FROM study_tables WHERE room_id = %s
                EXCEPT
                SELECT st.table_number 
                FROM reservations r
                JOIN study_tables st ON r.table_id = st.table_id
                WHERE r.status = 'active' 
                AND (NOW() BETWEEN r.start_time AND r.end_time)
                ORDER BY table_number;
            """
            cur.execute(query, (room_id,))
            results = cur.fetchall()
            cur.close()
            return [row[0] for row in results] # Liste olarak döner: [1, 3, 5]
        except Exception as e:
            print(f"Except Sorgu Hatası: {e}")
            return []

    # --- 7. ADMIN VE KULLANICI LİSTELERİ (Madde 6: View Kullanımı) ---
    def get_my_reservations(self, user_id):
        """Öğrencinin kendi geçmişini listeler"""
        try:
            cur = self.conn.cursor()
            query = """
                SELECT r.reservation_id, sr.room_name, st.table_number, r.start_time, r.end_time, r.status
                FROM reservations r
                JOIN study_tables st ON r.table_id = st.table_id
                JOIN study_rooms sr ON st.room_id = sr.room_id
                WHERE r.user_id = %s
                ORDER BY r.start_time DESC
            """
            cur.execute(query, (user_id,))
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            print(f"Liste Hatası: {e}")
            return []

    def get_all_reservations_admin(self):
        """Admin için VIEW kullanımı"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM view_all_reservations ORDER BY start_time DESC")
            results = cur.fetchall()
            cur.close()
            return results
        except Exception as e:
            print(f"View Hatası: {e}")
            return []