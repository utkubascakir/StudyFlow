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
            self.conn.autocommit = True  # ÖNEMLİ: Transaction hatalarını önler
            print("Veritabanı bağlantısı başarılı!")
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")

    def _reconnect_if_needed(self):
        """Bağlantı kopmuşsa yeniden bağlan"""
        try:
            if self.conn.closed:
                self.connect()
        except:
            self.connect()

    # --- 1. LOGIN İŞLEMLERİ ---
    def login(self, email, password):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM func_login(%s, %s)", (email, password))
            user = cur.fetchone()
            cur.close()
            return user
        except Exception as e:
            print(f"Login Hatası: {e}")
            return None
        
    # --- KAYIT FONKSİYONU ---
    def register_user(self, first_name, last_name, email, password):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT func_register_user(%s, %s, %s, %s)", (first_name, last_name, email, password))
            result = cur.fetchone()[0]
            cur.close()
            return result
        except Exception as e:
            error_msg = str(e)
            print(f"Kayıt Hatası: {error_msg}")
            
            if "Şifre en az 4 karakter" in error_msg:
                return "HATA: Şifre çok kısa! (Min 4 karakter)"
            elif "already exists" in error_msg or "duplicate key" in error_msg or "zaten kayıtlı" in error_msg:
                return "HATA: Bu e-posta adresi zaten kayıtlı!"
            return f"Kayıt Hatası: {error_msg}"

    # --- 2. ODA VE MASA DURUMLARI ---
    def get_rooms(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, room_name, capacity FROM study_rooms ORDER BY room_id")
            rooms = cur.fetchall()
            cur.close()
            print(f"✓ Bulunan odalar: {len(rooms)} adet")
            return rooms
        except Exception as e:
            print(f"✗ Oda Getirme Hatası: {e}")
            return []

    def get_room_status(self, room_id, check_time):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            # Debug için yazdırıyoruz
            print(f"DEBUG SQL: Oda {room_id} için durum sorgulanıyor...") 
            
            cur.execute("SELECT * FROM func_get_room_status(%s, %s)", (room_id, check_time))
            results = cur.fetchall()
            cur.close()
            print(f"DEBUG SQL: Oda {room_id} -> {len(results)} masa döndü.")
            return results
        except Exception as e:
            print(f"✗ Durum Sorgu Hatası: {e}")
            return []

    # --- 3. REZERVASYON İŞLEMLERİ ---
    def create_reservation(self, user_id, table_id, start_time, end_time):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            # Artık direkt INSERT değil, SQL fonksiyonunu çağırıyoruz
            cur.execute("SELECT func_create_reservation(%s, %s, %s, %s)", (user_id, table_id, start_time, end_time))
            result = cur.fetchone()[0] # 'SUCCESS' veya Hata mesajı döner
            cur.close()
            return result
        except Exception as e:
            print(f"✗ Rezervasyon Hatası: {e}")
            return f"Sistem Hatası: {str(e)}"

    def cancel_reservation(self, reservation_id):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("UPDATE reservations SET status = 'cancelled' WHERE reservation_id = %s", (reservation_id,))
            cur.close()
            return True
        except Exception as e:
            print(f"✗ İptal Hatası: {e}")
            return False

    # --- 4. ÖNERİ SİSTEMİ ---
    def get_suggestion(self, room_id, start_time, duration):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            print(f"→ Öneri sorgusu: Oda={room_id}, Başlangıç={start_time}, Süre={duration}h")
            cur.execute("SELECT func_suggest_table(%s, %s, %s)", (room_id, start_time, duration))
            result = cur.fetchone()
            cur.close()
            
            if result:
                print(f"✓ Öneri sonucu: {result[0]}")
                return result[0]
            else:
                return "Öneri bulunamadı."
        except Exception as e:
            print(f"✗ Öneri Hatası: {e}")
            import traceback
            traceback.print_exc()
            return f"Öneri alınamadı: {str(e)}"

    # --- 5. İSTATİSTİKLER ---
    def get_user_stats(self, user_id, period):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM func_user_stats(%s, %s)", (user_id, period))
            result = cur.fetchone()
            cur.close()
            print(f"✓ İstatistik sonucu: {result}")
            return result
        except Exception as e:
            print(f"✗ İstatistik Hatası: {e}")
            import traceback
            traceback.print_exc()
            return None

    # --- 6. EXCEPT SORGUSU ---
    def get_available_tables_list(self, room_id):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            query = """
                SELECT table_number FROM study_tables WHERE room_id = %s
                EXCEPT
                SELECT st.table_number 
                FROM reservations r
                JOIN study_tables st ON r.table_id = st.table_id
                WHERE r.status = 'active' 
                AND st.room_id = %s
                AND (NOW() BETWEEN r.start_time AND r.end_time)
                ORDER BY table_number;
            """
            cur.execute(query, (room_id, room_id))
            results = cur.fetchall()
            cur.close()
            available = [row[0] for row in results]
            print(f"✓ Boş masalar (Oda {room_id}): {available}")
            return available
        except Exception as e:
            print(f"✗ Except Sorgu Hatası: {e}")
            return []

    # --- 7. LİSTELEME FONKSİYONLARI ---
    def get_my_reservations(self, user_id):
        try:
            self._reconnect_if_needed()
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
            print(f"✓ Kullanıcı {user_id} rezervasyonları: {len(results)} adet")
            return results
        except Exception as e:
            print(f"✗ Liste Hatası: {e}")
            return []

    def get_all_reservations_admin(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM view_all_reservations ORDER BY start_time DESC")
            results = cur.fetchall()
            cur.close()
            print(f"✓ Admin view: {len(results)} rezervasyon")
            return results
        except Exception as e:
            print(f"✗ View Hatası: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def __del__(self):
        """Bağlantıyı düzgün kapatmak için"""
        try:
            if self.conn and not self.conn.closed:
                self.conn.close()
                print("✓ Veritabanı bağlantısı kapatıldı")
        except:
            pass