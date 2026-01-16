import psycopg2
from datetime import datetime


class Database:
    def __init__(self, user_role=None):

        self.user_role = user_role
        self.conn = None
        self._set_db_config(user_role)
        self.connect()

    def _set_db_config(self, user_role):
        base_config = {
            "dbname": "StudyFlow",
            "host": "localhost",
            "port": "5432"
        }
        
        #Student işlemleri için databasedeki app_student userı ile bağlan
        if user_role == 'student':
            self.db_config = {
                **base_config,
                "user": "app_student",
                "password": "student_pass_2025"
            }
        
        #Admin işlemleri için databasedeki app_admin userı ile bağlan
        elif user_role == 'admin':
            self.db_config = {
                **base_config,
                "user": "app_admin",
                "password": "admin_pass_2025"
            }
        else:
            self.db_config = {
                **base_config,
                "user": "postgres",
                "password": "1234"
            }

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = True
            print(f"Veritabanı bağlantısı başarılı (Kullanıcı: {self.db_config['user']})")
        except Exception as e:
            print(f"Bağlantı Hatası: {e}")
            raise

    def _reconnect_if_needed(self):
        try:
            if self.conn.closed:
                self.connect()
        except:
            self.connect()

    def __del__(self):
        try:
            if self.conn and not self.conn.closed:
                self.conn.close()
                print("Veritabanı bağlantısı kapatıldı")
        except:
            pass


    # Login işlemleri
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


    # User register işlemleri
    def register_user(self, first_name, last_name, email, password):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute(
                "SELECT func_register_user(%s, %s, %s, %s)",
                (first_name, last_name, email, password)
            )
            result = cur.fetchone()[0]
            cur.close()
            return result
        except psycopg2.Error as e:
            error_msg = str(e)
            print(f"Kayıt Hatası: {error_msg}")
            
            if "Şifre en az 4 karakter" in error_msg:   # Trigger tetiklendiğinde dönüş
                return "HATA: Şifre en az 4 karakter olmalıdır!"
            
            elif any(x in error_msg for x in ["already exists", "duplicate key", "zaten kayıtlı"]):
                return "HATA: Bu e-posta adresi zaten kayıtlı!"
            else:
                return f"HATA: {error_msg}"
        except Exception as e:
            print(f"✗ Beklenmeyen hata: {e}")
            return f"HATA: {str(e)}"


    # Tüm odaları getir
    def get_rooms(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT room_id, room_name, capacity FROM study_rooms ORDER BY room_id")
            rooms = cur.fetchall()
            cur.close()
            return rooms
        except Exception as e:
            print(f"Oda Getirme Hatası: {e}")
            return []

    # Bir odadaki tüm masaları bir zamanda uygun olup olmadığına göre işaretleyip geitr
    def get_room_status(self, room_id, check_time):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            cur.execute("SELECT * FROM func_get_room_status(%s, %s)", (room_id, check_time))
            results = cur.fetchall()
            cur.close()
            
            return results
        except Exception as e:
            print(f"Durum Sorgu Hatası: {e}")
            import traceback
            traceback.print_exc()
            return []

    # Bir odadaki sadece b,r zaman aralığındaki uygun masaları getir
    def get_available_tables_for_timerange(self, room_id, start_time, end_time):
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
                  AND (r.start_time < %s AND r.end_time > %s)
                ORDER BY table_number;
            """
            
            cur.execute(query, (room_id, room_id, end_time, start_time))
            results = cur.fetchall()
            cur.close()
            
            available = [row[0] for row in results]
            return available
        except Exception as e:
            print(f"Except Sorgu Hatası: {e}")
            import traceback
            traceback.print_exc()
            return []


    # Tamamlanan reservationları completed olarak update
    def complete_past_reservations(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            cur.execute("SELECT complete_past_reservations()")
            count = cur.fetchone()[0]
            cur.close()
            
            return count
        except Exception as e:
            print(f"Auto-complete error: {e}")
            return 0


    # Reservation oluşturr
    def create_reservation(self, user_id, table_id, start_time, end_time):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            cur.execute(
                "SELECT func_create_reservation(%s, %s, %s, %s)",
                (user_id, table_id, start_time, end_time)
            )
            result = cur.fetchone()[0]
            cur.close()
            
            return result
        except psycopg2.Error as e:
            error_msg = str(e)
            print(f"Rezervasyon Hatası: {error_msg}")
            
            if any(x in error_msg for x in ["GÜNLÜK LİMİT", "sadece 1 kez", "Günde sadece"]): # Günlük Limit Triggerı tetiklenirse
                return "HATA: Günde sadece 1 kez rezervasyon yapabilirsiniz!"
            
            elif any(x in error_msg for x in ["ÇAKIŞMA VAR", "zaten dolu"]):
                return "HATA: Bu saat aralığında masa zaten dolu!"
            else:
                return f"HATA: {error_msg}"
        except Exception as e:
            print(f"✗ Beklenmeyen hata: {e}")
            return f"HATA: {str(e)}"

    #Bir reservationı cancelled olarak güncelle
    def cancel_reservation(self, reservation_id):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            cur.execute(
                "SELECT status FROM reservations WHERE reservation_id = %s",
                (reservation_id,)
            )
            result = cur.fetchone()
            
            if not result:
                cur.close()
                return "HATA: Rezervasyon bulunamadı!"
            
            status = result[0]
            
            if status == 'cancelled':
                cur.close()
                return "HATA: Bu rezervasyon zaten iptal edilmiş!"
            
            if status == 'completed':
                cur.close()
                return "HATA: Tamamlanmış rezervasyon iptal edilemez!"
            
            cur.execute(
                "UPDATE reservations SET status = 'cancelled' WHERE reservation_id = %s",
                (reservation_id,)
            )
            cur.close()
            
            return "SUCCESS"
            
        except Exception as e:
            print(f"İptal Hatası: {e}")
            import traceback
            traceback.print_exc()
            return f"HATA: {str(e)}"

    #Bir kişinin reservationlarını getir
    def get_my_reservations(self, user_id):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            # Önce varsa tamamlanmış reservationları güncelle
            cur.execute("SELECT complete_past_reservations()")
            
            query = """
                SELECT 
                    r.reservation_id, 
                    sr.room_name, 
                    st.table_number, 
                    r.start_time, 
                    r.end_time, 
                    r.status
                FROM reservations_with_status r
                JOIN study_tables st ON r.table_id = st.table_id
                JOIN study_rooms sr ON st.room_id = sr.room_id
                WHERE r.user_id = %s
                ORDER BY r.status ASC, r.start_time DESC
            """
            
            cur.execute(query, (user_id,))
            results = cur.fetchall()
            cur.close()
            
            return results
        except Exception as e:
            print(f"Liste Hatası: {e}")
            return []


    # Bir kişinin istatistiklerini, verimlilik, sonucunu getir
    def get_user_stats(self, user_id, period):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            # Önce varsa tamamlanmış reservationları güncelle
            cur.execute("SELECT complete_past_reservations()")
            
            cur.execute("SELECT * FROM func_user_stats(%s, %s)", (user_id, period))
            result = cur.fetchone()
            cur.close()
            
            return result
        except Exception as e:
            print(f"İstatistik Hatası: {e}")
            import traceback
            traceback.print_exc()
            return None

    #ADMIN: Tüm reservatinoları geit
    def get_all_reservations_admin(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            # Önce varsa tamamlanmış reservationları güncelle
            cur.execute("SELECT complete_past_reservations()")
            
            cur.execute("SELECT * FROM view_all_reservations ORDER BY start_time DESC")
            results = cur.fetchall()
            cur.close()
            
            return results
        except Exception as e:
            print(f"View Hatası: {e}")
            import traceback
            traceback.print_exc()
            return []

    #ADMIN: En sadık 3 kullanıcıyı getir
    def get_loyalty_users(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            # Önce varsa tamamlanmış reservationları güncelle
            cur.execute("SELECT complete_past_reservations()")
            

            # Tamamlanmış en az 5 reservationu olan kullanıcılardan
            # En fazla tamamlanmış reservationu olan ilk 3 kullanıcıyı getir 
            query = """
                SELECT 
                    u.user_id,
                    u.first_name || ' ' || u.last_name AS full_name,
                    u.email,
                    COUNT(r.reservation_id) AS total_reservations,
                    SUM(r.end_time - r.start_time) AS total_time
                FROM users u
                JOIN reservations r ON u.user_id = r.user_id
                WHERE r.status = 'completed'
                  AND u.user_role = 'student'
                GROUP BY u.user_id, u.first_name, u.last_name, u.email
                HAVING COUNT(r.reservation_id) > 5
                ORDER BY COUNT(r.reservation_id) DESC
                LIMIT 3
            """
            
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            
            return results
        except Exception as e:
            print(f"Loyalty query hatası: {e}")
            import traceback
            traceback.print_exc()
            return []


    #ADMIN: tüm kullanıcıları getir
    def get_all_users(self):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            query = """
                SELECT 
                    u.user_id,
                    u.first_name || ' ' || u.last_name AS full_name,
                    u.email,
                    u.user_role,
                    u.created_at,
                    COUNT(r.reservation_id) AS total_reservations
                FROM users u
                LEFT JOIN reservations r ON u.user_id = r.user_id
                GROUP BY u.user_id, u.first_name, u.last_name, u.email, u.user_role, u.created_at
                ORDER BY u.user_role DESC, u.created_at DESC
            """
            
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            
            return results
        except Exception as e:
            print(f"Kullanıcı listesi hatası: {e}")
            return []

    #ADMIN: Bir kullanıcıyı sil
    def delete_user(self, user_id):
        try:
            self._reconnect_if_needed()
            cur = self.conn.cursor()
            
            cur.execute("SELECT user_role FROM users WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            
            if not result:
                cur.close()
                return "HATA: Kullanıcı bulunamadı!"
            
            if result[0] == 'admin':
                cur.close()
                return "HATA: Admin kullanıcısı silinemez!"
            
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            cur.close()
            
            return "SUCCESS"
            
        except Exception as e:
            print(f"Kullanıcı silme hatası: {e}")
            import traceback
            traceback.print_exc()
            return f"HATA: {str(e)}"
    
    #Öneri fonksiyonu
    def find_best_time_window(self, room_id, date_str, duration_hours):
        try:
            self._reconnect_if_needed()
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.now()
            
            results = []
            best_start_hour = None
            best_end_hour = None
            max_available = -1

            #Çalışılmak istenen saat miktarını 9-22 arasında maske gibi gezdir.
            #Her bir gezinmede odanın o saatteki durumunu al
            #Bu değerlere göre önerilerde bulun
            for start_hour in range(9, 23 - duration_hours):
                end_hour = start_hour + duration_hours
                
                start_time = date_obj.replace(hour=start_hour, minute=0, second=0, microsecond=0)
                end_time = date_obj.replace(hour=end_hour, minute=0, second=0, microsecond=0)
                
                if start_time < now:
                    results.append({
                        'start_hour': start_hour,
                        'end_hour': end_hour,
                        'available_count': 0,
                        'status': 'past',
                        'message': f"{start_hour}:00 - {end_hour}:00 (Geçmiş zaman)"
                    })
                    continue
                
                #Maskenin mevcut konumu için odaların durumunu al
                available_tables = self.get_available_tables_for_timerange(
                    room_id, start_time, end_time
                )
                
                available_count = len(available_tables)
                
                if available_count == 0:
                    status = 'full'
                    message = f"{start_hour}:00 - {end_hour}:00 (Uygun masa yok)"
                else:
                    status = 'available'
                    message = f"{start_hour}:00 - {end_hour}:00 ({available_count} masa müsait)"
                
                results.append({
                    'start_hour': start_hour,
                    'end_hour': end_hour,
                    'available_count': available_count,
                    'available_tables': available_tables,
                    'status': status,
                    'message': message
                })
                
                if available_count > max_available:
                    max_available = available_count
                    best_start_hour = start_hour
                    best_end_hour = end_hour
            
            return {
                'best_start_hour': best_start_hour,
                'best_end_hour': best_end_hour,
                'max_available': max_available,
                'all_windows': results
            }
            
        except Exception as e:
            print(f"En iyi zaman bulma hatası: {e}")
            import traceback
            traceback.print_exc()
            return None