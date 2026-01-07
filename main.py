import flet as ft
from database import Database
from datetime import datetime

# Veritabanı Bağlantısı
db = Database()

def main(page: ft.Page):
    # --- SAYFA AYARLARI ---
    page.title = "StudyFlow - Kampüs Rezervasyon"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    # Renk Paleti (BÜYÜK HARF DÜZELTMESİ YAPILDI)
    primary_color = ft.Colors.TEAL_400
    bg_color = ft.Colors.BLUE_GREY_900
    card_bg = ft.Colors.BLUE_GREY_800
    text_white = ft.Colors.WHITE
    text_grey = ft.Colors.GREY_400

    # --- DEĞİŞKENLER (State) ---
    current_user = None 
    selected_room_id = 1 

    # --- YARDIMCI BİLEŞEN: MESAJ KUTUSU ---
    def show_message(text, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # ==========================================
    # 1. KAYIT OL EKRANI (YENİ EKLENDİ)
    # ==========================================
    def load_register_page():
        page.clean()

        reg_name = ft.TextField(label="Ad", width=300, border_radius=15, prefix_icon=ft.Icons.PERSON)
        reg_surname = ft.TextField(label="Soyad", width=300, border_radius=15, prefix_icon=ft.Icons.PERSON_OUTLINE)
        reg_email = ft.TextField(label="E-posta", width=300, border_radius=15, prefix_icon=ft.Icons.EMAIL)
        reg_pass = ft.TextField(label="Şifre", password=True, width=300, border_radius=15, prefix_icon=ft.Icons.LOCK, can_reveal_password=True)

        def handle_register(e):
            if not reg_name.value or not reg_surname.value or not reg_email.value or not reg_pass.value:
                show_message("Lütfen tüm alanları doldurun!", ft.Colors.RED)
                return

            res = db.register_user(reg_name.value, reg_surname.value, reg_email.value, reg_pass.value)
            
            if res == 'SUCCESS':
                show_message("Kayıt Başarılı! Giriş yapabilirsiniz.", ft.Colors.GREEN)
                load_login_page()
            else:
                show_message(res, ft.Colors.RED)

        register_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.APP_REGISTRATION, size=60, color=primary_color),
                ft.Text("Kayıt Ol", size=30, weight="bold", color=text_white),
                ft.Divider(height=20, color="transparent"),
                reg_name,
                reg_surname,
                reg_email,
                reg_pass,
                ft.ElevatedButton("Kayıt Ol", width=300, height=45, on_click=handle_register, style=ft.ButtonStyle(bgcolor=primary_color, color="white")),
                ft.TextButton("Zaten hesabın var mı? Giriş Yap", on_click=lambda e: load_login_page())
            ], alignment="center", horizontal_alignment="center"),
            width=400, height=600, bgcolor=card_bg, border_radius=20, padding=40,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK)
        )

        # DÜZELTME: ft.Alignment(0,0) kullanıldı
        page.add(ft.Container(content=register_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color))


    # ==========================================
    # 2. LOGIN EKRANI
    # ==========================================
    def load_login_page():
        page.clean()
        
        email_input = ft.TextField(label="E-posta", width=300, border_radius=15, prefix_icon=ft.Icons.EMAIL)
        pass_input = ft.TextField(label="Şifre", password=True, width=300, border_radius=15, prefix_icon=ft.Icons.LOCK, can_reveal_password=True)

        def handle_login(e):
            nonlocal current_user
            user = db.login(email_input.value, pass_input.value)
            
            if user and user[3] == 'SUCCESS':
                current_user = user 
                show_message(f"Hoşgeldin {user[1]}!", ft.Colors.GREEN)
                if user[2] == 'admin':
                    load_admin_dashboard()
                else:
                    load_student_dashboard()
            else:
                show_message("Hatalı E-posta veya Şifre!", ft.Colors.RED)

        login_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SCHOOL, size=60, color=primary_color),
                ft.Text("StudyFlow", size=30, weight="bold", color=text_white),
                ft.Text("Giriş Yap", size=16, color=text_grey),
                ft.Divider(height=20, color="transparent"),
                email_input,
                pass_input,
                ft.ElevatedButton("Giriş Yap", width=300, height=45, on_click=handle_login, style=ft.ButtonStyle(bgcolor=primary_color, color="white")),
                ft.TextButton("Hesabın yok mu? Kayıt Ol", on_click=lambda e: load_register_page()),
                ft.Text("Admin: admin@studyflow.com / 1234", size=12, color=ft.Colors.GREY_600)
            ], alignment="center", horizontal_alignment="center"),
            width=400, height=550, bgcolor=card_bg, border_radius=20, padding=40,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK)
        )

        # DÜZELTME: ft.Alignment(0,0) kullanıldı
        page.add(ft.Container(content=login_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color))


    # ==========================================
    # 3. ÖĞRENCİ PANELİ
    # ==========================================
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def load_student_dashboard():
        page.clean()
        
        sidebar = ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.BOOK), ft.Text("StudyFlow", size=20, weight="bold")], alignment="center"),
                ft.Divider(color="white24"),
                ft.ListTile(leading=ft.Icon(ft.Icons.GRID_VIEW), title=ft.Text("Rezervasyon Yap"), on_click=lambda e: show_reservation_tab()),
                ft.ListTile(leading=ft.Icon(ft.Icons.HISTORY), title=ft.Text("Geçmişim"), on_click=lambda e: show_history_tab()),
                ft.ListTile(leading=ft.Icon(ft.Icons.BAR_CHART), title=ft.Text("Verimlilik"), on_click=lambda e: show_stats_tab()),
                ft.Divider(color="white24"),
                ft.ListTile(leading=ft.Icon(ft.Icons.EXIT_TO_APP, color="red"), title=ft.Text("Çıkış", color="red"), on_click=lambda e: load_login_page()),
            ]),
            width=250, bgcolor=card_bg, padding=20, height=800
        )

        page.add(ft.Row([sidebar, ft.VerticalDivider(width=1, color="white10"), content_area], expand=True))
        show_reservation_tab()

    # --- SEKME 1: REZERVASYON ---
    def show_reservation_tab():
        content_area.controls.clear()
        
        # DÜZELTME: Dropdown için get_rooms güvenli çağrısı
        rooms = db.get_rooms() or []
        room_options = [ft.dropdown.Option(key=str(r[0]), text=r[1]) for r in rooms] if rooms else []

        room_dropdown = ft.Dropdown(
            label="Çalışma Odası Seç", width=250,
            options=room_options,
            value=str(selected_room_id),
            on_change=lambda e: refresh_grid(int(e.control.value))
        )

        quick_select = ft.Dropdown(label="Hızlı Boş Masa Seç (Liste)", width=250, options=[])
        tables_grid = ft.GridView(expand=True, runs_count=5, max_extent=150, child_aspect_ratio=1.0, spacing=10, run_spacing=10)

        def refresh_grid(room_id):
            nonlocal selected_room_id
            selected_room_id = room_id
            
            statuses = db.get_room_status(room_id, datetime.now())
            tables_grid.controls.clear()

            avail_tables = db.get_available_tables_list(room_id)
            quick_select.options = [ft.dropdown.Option(str(t)) for t in avail_tables]

            for table in statuses:
                t_id, t_num, status, until = table
                
                bg_c = ft.Colors.GREEN_700 if status == 'BOŞ' else ft.Colors.RED_800
                icon = ft.Icons.CHAIR if status == 'BOŞ' else ft.Icons.PERSON_OFF
                
                card = ft.Container(
                    content=ft.Column([
                        ft.Icon(icon, size=40, color="white"),
                        ft.Text(f"Masa {t_num}", size=20, weight="bold"),
                        ft.Text(status, color="white70"),
                        ft.Text(f"{until.strftime('%H:%M')}'e kadar" if until else "Müsait", size=12)
                    ], alignment="center", horizontal_alignment="center"),
                    bgcolor=bg_c, border_radius=15, padding=10,
                    on_click=lambda e, tid=t_id, tnum=t_num: open_res_dialog(tid, tnum) if status == 'BOŞ' else show_message("Bu masa dolu!", ft.Colors.RED)
                )
                tables_grid.controls.append(card)
            
            page.update()

        def get_suggestion(e):
            msg = db.get_suggestion(selected_room_id, datetime.now(), 2)
            show_message(msg, ft.Colors.CYAN)

        header = ft.Row([
            ft.Text("Masa Durumu", size=25, weight="bold"),
            ft.Container(expand=True), 
            ft.ElevatedButton("Bana Yer Öner", icon=ft.Icons.LIGHTBULB, on_click=get_suggestion)
        ])
        
        filters = ft.Row([room_dropdown, quick_select])
        
        content_area.controls.extend([
            ft.Container(content=header, padding=20),
            ft.Container(content=filters, padding=ft.padding.only(left=20, right=20, bottom=20)),
            ft.Container(content=tables_grid, expand=True, padding=20)
        ])
        
        if room_options: # Eğer oda varsa gridi yükle
            refresh_grid(selected_room_id)
        page.update()

    def open_res_dialog(table_id, table_num):
        start_hour = ft.Dropdown(label="Başlangıç", options=[ft.dropdown.Option(str(i)) for i in range(9, 18)], value="9", width=120)
        duration = ft.Dropdown(label="Süre (Saat)", options=[ft.dropdown.Option(str(i)) for i in range(1, 6)], value="1", width=120)
        
        # Dialog kapatma fonksiyonu
        def close_dlg(e):
            dlg.open = False
            page.update()

        def confirm_res(e):
            now = datetime.now()
            s_h = int(start_hour.value)
            dur = int(duration.value)
            
            start_time = now.replace(hour=s_h, minute=0, second=0, microsecond=0)
            end_time = start_time.replace(hour=s_h + dur)
            
            res = db.create_reservation(current_user[0], table_id, start_time, end_time)
            
            if "SUCCESS" in res:
                show_message("Rezervasyon Başarılı!", ft.Colors.GREEN)
                close_dlg(None)
                show_reservation_tab()
            else:
                show_message(res, ft.Colors.RED)
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Masa {table_num} Rezerve Et"),
            content=ft.Column([
                ft.Text("Bugün için saat seçiniz:"),
                ft.Row([start_hour, duration])
            ], height=100),
            actions=[
                ft.TextButton("İptal", on_click=close_dlg),
                ft.ElevatedButton("Onayla", on_click=confirm_res)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- SEKME 2: İSTATİSTİKLER ---
    def show_stats_tab():
        content_area.controls.clear()
        
        period_drop = ft.Dropdown(
            label="Dönem Seç", 
            options=[
                ft.dropdown.Option("1 week", "Son 1 Hafta"),
                ft.dropdown.Option("1 month", "Son 1 Ay"),
                ft.dropdown.Option("all", "Tüm Zamanlar"),
            ],
            value="all"
        )
        
        result_text = ft.Text("Seçim yapınız...", size=20)
        
        def calculate(e):
            stats = db.get_user_stats(current_user[0], period_drop.value)
            if stats:
                sure, oturum = stats
                result_text.value = f"Toplam Oturum: {oturum}\nToplam Süre: {str(sure)}"
            page.update()

        content_area.controls.extend([
            ft.Text("Verimlilik İstatistikleri", size=30, weight="bold"),
            ft.Divider(),
            period_drop,
            ft.ElevatedButton("Hesapla", on_click=calculate),
            ft.Container(content=result_text, padding=20, bgcolor=card_bg, border_radius=10)
        ])
        page.update()

    # --- SEKME 3: GEÇMİŞİM ---
    def show_history_tab():
        content_area.controls.clear()
        rows = db.get_my_reservations(current_user[0])
        
        data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Oda")),
                ft.DataColumn(ft.Text("Masa")),
                ft.DataColumn(ft.Text("Başlangıç")),
                ft.DataColumn(ft.Text("Bitiş")),
                ft.DataColumn(ft.Text("Durum")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(str(r[2]))),
                    ft.DataCell(ft.Text(r[3].strftime('%d.%m %H:%M'))),
                    ft.DataCell(ft.Text(r[4].strftime('%H:%M'))),
                    ft.DataCell(ft.Text(r[5])),
                ]) for r in rows
            ]
        )
        
        content_area.controls.extend([
            ft.Text("Rezervasyon Geçmişim", size=30, weight="bold"),
            ft.Divider(),
            data_table
        ])
        page.update()

    # --- ADMIN PANELİ ---
    def load_admin_dashboard():
        page.clean()
        
        rows = db.get_all_reservations_admin()
        
        admin_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Öğrenci")),
                ft.DataColumn(ft.Text("Oda")),
                ft.DataColumn(ft.Text("Masa")),
                ft.DataColumn(ft.Text("Tarih")),
                ft.DataColumn(ft.Text("Durum")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(r[2])),
                    ft.DataCell(ft.Text(str(r[3]))),
                    ft.DataCell(ft.Text(r[4].strftime('%d.%m %H:%M'))),
                    ft.DataCell(ft.Text(r[6])),
                ]) for r in rows
            ],
            border=ft.border.all(1, "white10"),
            vertical_lines=ft.border.all(1, "white10"),
        )
        
        page.add(
            ft.Column([
                ft.Row([ft.Text("Yönetici Paneli", size=30, weight="bold"), ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: load_login_page())], alignment="spaceBetween"),
                ft.Text("Tüm Rezervasyonlar (VIEW Kullanımı)", color="grey"),
                ft.Divider(),
                ft.Container(content=admin_table, expand=True, overflow_scroll=True)
            ], expand=True, padding=20)
        )

    # Uygulamayı Başlat
    load_login_page()

ft.app(main)