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
    
    # Renk Paleti
    primary_color = ft.Colors.TEAL_400
    bg_color = ft.Colors.BLUE_GREY_900
    card_bg = ft.Colors.BLUE_GREY_800
    text_white = ft.Colors.WHITE
    text_grey = ft.Colors.GREY_400

    # --- DEĞİŞKENLER (State) ---
    current_user = None 
    selected_room_id = [1]

    # --- YARDIMCI BİLEŞEN: MESAJ KUTUSU ---
    def show_message(text, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # ==========================================
    # 1. KAYIT OL EKRANI
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
                ft.FilledButton("Kayıt Ol", width=300, height=45, on_click=handle_register, style=ft.ButtonStyle(bgcolor=primary_color, color="white")),
                ft.TextButton("Zaten hesabın var mı? Giriş Yap", on_click=lambda e: load_login_page())
            ], alignment="center", horizontal_alignment="center"),
            width=400, height=600, bgcolor=card_bg, border_radius=20, padding=40,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK)
        )

        page.add(ft.Container(content=register_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color))
        page.update()


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
                ft.FilledButton("Giriş Yap", width=300, height=45, on_click=handle_login, style=ft.ButtonStyle(bgcolor=primary_color, color="white")),
                ft.TextButton("Hesabın yok mu? Kayıt Ol", on_click=lambda e: load_register_page()),
                ft.Text("Admin: admin@studyflow.com / 1234", size=12, color=ft.Colors.GREY_600)
            ], alignment="center", horizontal_alignment="center"),
            width=400, height=550, bgcolor=card_bg, border_radius=20, padding=40,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK)
        )

        page.add(ft.Container(content=login_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color))
        page.update()


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
        page.update()

    # --- SEKME 1: REZERVASYON ---
    def show_reservation_tab():
        content_area.controls.clear()

        # Local state for selection and mapping table numbers to cards
        selected_table = {'id': None, 'num': None, 'card': None}
        table_cards = {}  # key: table_number -> (table_id, card, is_empty)

        # Odaları veritabanından çek
        rooms = db.get_rooms() or []

        if not rooms:
            content_area.controls.append(ft.Text("Veritabanında oda bulunamadı! Lütfen 'study_rooms' tablosuna veri ekleyin.", color=ft.Colors.RED))
            page.update()
            return

        # Dropdown seçeneklerini hazırla
        room_options = [ft.dropdown.Option(key=str(r[0]), text=r[1]) for r in rooms]

        # Eğer seçili oda yoksa ilk odayı seç
        if not selected_room_id or selected_room_id[0] not in [r[0] for r in rooms]:
            selected_room_id[0] = rooms[0][0]

        room_dropdown = ft.Dropdown(
            label="Çalışma Odası Seç",
            width=250,
            options=room_options,
            value=str(selected_room_id[0])  # Seçili olanın ID'si string olarak
        )

        quick_select = ft.Dropdown(label="Hızlı Boş Masa Seç", width=250, options=[])

        # Masaların duracağı kapsayıcı (Column)
        tables_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        # --- CONFIRM BAR (Gizli, seçim yapıldığında gösterilecek) ---
        sel_text = ft.Text("", size=14, weight="bold")
        start_hour_confirm = ft.Dropdown(
            label="Başlangıç Saati",
            options=[ft.dropdown.Option(str(i)) for i in range(9, 18)],
            value="9",
            width=120
        )
        duration_confirm = ft.Dropdown(
            label="Süre (Saat)",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            value="2",
            width=120
        )

        def cancel_selection(e=None):
            # Deselect current
            if selected_table['card']:
                # revert card color to green
                selected_table['card'].bgcolor = ft.Colors.GREEN_700
                # update status text back to "BOŞ"
                try:
                    selected_table['card'].content.controls[2].value = 'BOŞ'
                except Exception:
                    pass
                selected_table['card'] = None
            selected_table['id'] = None
            selected_table['num'] = None
            confirm_bar.visible = False
            page.update()

        def confirm_selection(e):
            if not selected_table['id'] or not current_user:
                show_message('Lütfen önce masa seçin ve giriş yapın!', ft.Colors.RED)
                return
            try:
                now = datetime.now()
                s_h = int(start_hour_confirm.value)
                dur = int(duration_confirm.value)

                start_time = now.replace(hour=s_h, minute=0, second=0, microsecond=0)
                end_time = start_time.replace(hour=s_h + dur)

                print(f"Rezervasyon (seçimden): User={current_user[0]}, Table={selected_table['id']}, Start={start_time}, End={end_time}")
                res = db.create_reservation(current_user[0], selected_table['id'], start_time, end_time)

                if 'SUCCESS' in res:
                    show_message('Rezervasyon Başarılı!', ft.Colors.GREEN)
                    # Update the card visual immediately
                    c = selected_table['card']
                    if c:
                        c.bgcolor = ft.Colors.RED_800
                        try:
                            c.content.controls[2].value = 'DOLU'
                            c.content.controls[3].value = f"{end_time.strftime('%H:%M')}'e kadar"
                        except Exception:
                            pass
                    cancel_selection()
                    # small delay: refresh grid to sync with DB
                    refresh_grid(selected_room_id[0])
                else:
                    show_message(res, ft.Colors.RED)
            except Exception as ex:
                show_message(f"Rezervasyon hatası: {str(ex)}", ft.Colors.RED)
                print(f"Reservation error (selection): {ex}")

        confirm_bar = ft.Container(
            content=ft.Row([
                sel_text,
                ft.Container(width=20),
                start_hour_confirm,
                duration_confirm,
                ft.Container(width=20),
                ft.FilledButton('Rezervasyonu Onayla', on_click=confirm_selection, style=ft.ButtonStyle(bgcolor=primary_color)),
                ft.TextButton('İptal', on_click=cancel_selection)
            ], alignment=ft.MainAxisAlignment.CENTER),
            visible=False,
            padding=10,
            bgcolor=card_bg,
            border_radius=12,
            margin=ft.margin.only(bottom=10)
        )

        # GRID YENİLEME FONKSİYONU
        def refresh_grid(room_id):
            print(f"UI UPDATE: Oda {room_id} yükleniyor...")

            # Global değişkeni güncelle
            selected_room_id[0] = int(room_id)

            # Clear selection when changing room
            cancel_selection()
            table_cards.clear()

            # Konteynerı temizle
            tables_container.controls.clear()

            try:
                # Veritabanından çek
                statuses = db.get_room_status(room_id, datetime.now())

                # Boş masa listesini güncelle (Hızlı seçim için)
                avail_tables = db.get_available_tables_list(room_id)
                quick_select.options = [ft.dropdown.Option(str(t)) for t in avail_tables]
                quick_select.value = None  # Seçimi sıfırla

                if not statuses:
                    tables_container.controls.append(
                        ft.Container(
                            content=ft.Text("Bu odada tanımlı masa yok.", size=16, color=ft.Colors.ORANGE),
                            padding=20
                        )
                    )
                else:
                    # Masaları kartlara dönüştür
                    rows = []
                    current_row = []

                    for idx, table in enumerate(statuses):
                        t_id, t_num, status, until = table

                        is_empty = (status == 'BOŞ')
                        bg_c = ft.Colors.GREEN_700 if is_empty else ft.Colors.RED_800
                        icon = ft.Icons.CHAIR if is_empty else ft.Icons.PERSON_OFF

                        card = ft.Container(
                            content=ft.Column([
                                ft.Icon(icon, size=30, color="white"),
                                ft.Text(f"Masa {t_num}", size=14, weight="bold"),
                                ft.Text(status, size=11, color="white70"),
                                ft.Text(
                                    f"{until.strftime('%H:%M')}'e kadar" if until else "Müsait",
                                    size=10, color="white60"
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                            bgcolor=bg_c,
                            border_radius=12,
                            padding=8,
                            width=100,
                            height=100,
                            ink=True
                        )

                        # Save to map for later access
                        table_cards[t_num] = (t_id, card, is_empty)

                        # Assign click handler AFTER creation so we can reference the card
                        def make_on_click(tid, tnum, free, c):
                            def _on_click(e):
                                toggle_select(tid, tnum, c, free)
                            return _on_click

                        card.on_click = make_on_click(t_id, t_num, is_empty, card)

                        current_row.append(card)

                        # Her 6 masada bir alt satıra geç
                        if len(current_row) == 6 or idx == len(statuses) - 1:
                            rows.append(ft.Row(controls=current_row, spacing=10, wrap=False))
                            current_row = []

                    # Satırları ekrana ekle
                    tables_container.controls.extend(rows)

            except Exception as e:
                print(f"HATA: Grid yenileme patladı: {e}")
                tables_container.controls.append(ft.Text(f"Hata oluştu: {e}", color=ft.Colors.RED))

            # En son sayfayı güncelle
            page.update()

        # Dropdown değiştiğinde çalışacak
        def on_room_change(e):
            new_id = int(e.control.value)
            refresh_grid(new_id)

        room_dropdown.on_change = on_room_change

        def on_quick_select(e):
            val = e.control.value
            if not val:
                return
            try:
                tnum = int(val)
                if tnum in table_cards:
                    tid, card, free = table_cards[tnum]
                    if free:
                        toggle_select(tid, tnum, card, free)
                    else:
                        show_message('Seçilen masa şu an dolu!', ft.Colors.RED)
            except Exception as ex:
                print(f'Quick select error: {ex}')

        quick_select.on_change = on_quick_select

        # Seçim toggle fonksiyonu
        def toggle_select(tid, tnum, card, free):
            if not free:
                show_message('Bu masa dolu!', ft.Colors.RED)
                return

            # Eğer zaten seçiliyse iptal et
            if selected_table['id'] == tid:
                cancel_selection()
                return

            # Deselect previous
            if selected_table['card']:
                try:
                    selected_table['card'].bgcolor = ft.Colors.GREEN_700
                    selected_table['card'].content.controls[2].value = 'BOŞ'
                except Exception:
                    pass

            # Select new
            selected_table['id'] = tid
            selected_table['num'] = tnum
            selected_table['card'] = card

            # Visual: set to grey
            card.bgcolor = ft.Colors.GREY_600
            try:
                card.content.controls[2].value = 'SEÇİLDİ'
            except Exception:
                pass

            sel_text.value = f"Seçilen Masa: {tnum}"
            confirm_bar.visible = True
            page.update()

        # Öneri Butonu Mantığı (aynı zamanda önerilen masayı otomatik seçer)
        def get_suggestion(e):
            current_room = selected_room_id[0]
            print(f"Öneri isteniyor... Oda ID: {current_room}")

            try:
                # 2 saatlik öneri iste
                msg = db.get_suggestion(current_room, datetime.now(), 2)

                # SnackBar ile göster
                page.snack_bar = ft.SnackBar(content=ft.Text(str(msg)), bgcolor=ft.Colors.CYAN)
                page.snack_bar.open = True
                page.update()

                # Eğer öneri formatı 'Öneri: Masa X' ise otomatik seç
                if isinstance(msg, str) and 'Öneri: Masa' in msg:
                    try:
                        parts = msg.split('Masa')
                        num = int(parts[-1].strip())
                        if num in table_cards:
                            tid, c, free = table_cards[num]
                            # if free select
                            if free:
                                toggle_select(tid, num, c, free)
                                return
                    except Exception as ex:
                        print(f"Öneri parse hatası: {ex}")

            except Exception as ex:
                print(f"Öneri hatası: {ex}")

        # Başlık ve Filtreler
        header = ft.Row([
            ft.Text("Masa Durumu", size=25, weight="bold"),
            ft.Container(expand=True),
            ft.FilledButton(
                "Bana Yer Öner",
                icon=ft.Icons.LIGHTBULB,
                on_click=get_suggestion,
                style=ft.ButtonStyle(bgcolor=primary_color)
            )
        ])

        filters = ft.Row([room_dropdown, quick_select], spacing=20)

        # Sayfaya bileşenleri yerleştir
        content_area.controls.extend([
            ft.Container(content=header, padding=20),
            ft.Container(content=filters, padding=ft.padding.only(left=20, right=20, bottom=20)),
            ft.Container(content=confirm_bar, padding=ft.padding.only(left=20, right=20, bottom=10)),
            ft.Container(content=tables_container, expand=True, padding=20)
        ])

        # İlk açılışta gridi yükle
        refresh_grid(selected_room_id[0])
        page.update()
    def open_res_dialog(table_id, table_num):
        start_hour = ft.Dropdown(
            label="Başlangıç Saati", 
            options=[ft.dropdown.Option(str(i)) for i in range(9, 18)], 
            value="9", 
            width=150
        )
        duration = ft.Dropdown(
            label="Süre (Saat)", 
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)], 
            value="2", 
            width=150
        )
        
        def close_dlg(e):
            dlg.open = False
            page.update()

        def confirm_res(e):
            try:
                now = datetime.now()
                s_h = int(start_hour.value)
                dur = int(duration.value)
                
                start_time = now.replace(hour=s_h, minute=0, second=0, microsecond=0)
                end_time = start_time.replace(hour=s_h + dur)
                
                print(f"Rezervasyon oluşturuluyor: User={current_user[0]}, Table={table_id}, Start={start_time}, End={end_time}")
                
                res = db.create_reservation(current_user[0], table_id, start_time, end_time)
                
                if "SUCCESS" in res:
                    show_message("Rezervasyon Başarılı!", ft.Colors.GREEN)
                    close_dlg(None)
                    show_reservation_tab()  # Sayfayı yenile
                else:
                    show_message(res, ft.Colors.RED)
            except Exception as ex:
                show_message(f"Rezervasyon hatası: {str(ex)}", ft.Colors.RED)
                print(f"Reservation error: {ex}")
                import traceback
                traceback.print_exc()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Masa {table_num} Rezervasyonu", weight="bold"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Rezervasyon detaylarını seçiniz:", size=14, color=text_grey),
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([start_hour, duration], spacing=20),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text(
                        "⚠️ Seçtiğiniz saat aralığında masa müsait olmalıdır.", 
                        size=12, 
                        color=ft.Colors.ORANGE_300,
                        italic=True
                    )
                ], tight=True),
                padding=10
            ),
            actions=[
                ft.TextButton("İptal", on_click=close_dlg),
                ft.FilledButton(
                    "Rezerve Et", 
                    on_click=confirm_res,
                    style=ft.ButtonStyle(bgcolor=primary_color)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
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
            value="all",
            width=250
        )
        
        result_text = ft.Text("Hesapla butonuna basarak istatistiklerinizi görüntüleyin.", size=16, color=text_grey)
        
        def calculate(e):
            try:
                stats = db.get_user_stats(current_user[0], period_drop.value)
                if stats:
                    sure, oturum = stats
                    result_text.value = f"📊 Toplam Oturum: {oturum}\n⏱️ Toplam Süre: {str(sure)}"
                    result_text.color = text_white
                else:
                    result_text.value = "Henüz veri bulunmuyor."
                    result_text.color = ft.Colors.ORANGE
                page.update()
            except Exception as ex:
                show_message(f"İstatistik hatası: {str(ex)}", ft.Colors.RED)
                print(f"Stats error: {ex}")

        content_area.controls.extend([
            ft.Container(content=ft.Text("📈 Verimlilik İstatistikleri", size=30, weight="bold"), padding=20),
            ft.Divider(),
            ft.Container(content=period_drop, padding=20),
            ft.Container(
                content=ft.FilledButton(
                    "Hesapla", 
                    on_click=calculate,
                    icon=ft.Icons.CALCULATE,
                    style=ft.ButtonStyle(bgcolor=primary_color)
                ), 
                padding=20
            ),
            ft.Container(
                content=result_text, 
                padding=20, 
                bgcolor=card_bg, 
                border_radius=10, 
                margin=20
            )
        ])
        page.update()

    # --- SEKME 3: GEÇMİŞİM ---
    def show_history_tab():
        content_area.controls.clear()
        
        try:
            rows = db.get_my_reservations(current_user[0])
            
            if not rows:
                content_area.controls.extend([
                    ft.Container(content=ft.Text("📜 Rezervasyon Geçmişim", size=30, weight="bold"), padding=20),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Text("Henüz rezervasyonunuz bulunmuyor.", size=16),
                        padding=20,
                        bgcolor=card_bg,
                        border_radius=10,
                        margin=20
                    )
                ])
            else:
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Oda", weight="bold")),
                        ft.DataColumn(ft.Text("Masa", weight="bold")),
                        ft.DataColumn(ft.Text("Başlangıç", weight="bold")),
                        ft.DataColumn(ft.Text("Bitiş", weight="bold")),
                        ft.DataColumn(ft.Text("Durum", weight="bold")),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(r[1])),
                            ft.DataCell(ft.Text(str(r[2]))),
                            ft.DataCell(ft.Text(r[3].strftime('%d.%m %H:%M'))),
                            ft.DataCell(ft.Text(r[4].strftime('%H:%M'))),
                            ft.DataCell(ft.Text(r[5])),
                        ]) for r in rows
                    ],
                    border=ft.border.all(1, "white10"),
                )
                
                content_area.controls.extend([
                    ft.Container(content=ft.Text("📜 Rezervasyon Geçmişim", size=30, weight="bold"), padding=20),
                    ft.Divider(),
                    ft.Container(content=data_table, padding=20)
                ])
        except Exception as e:
            show_message(f"Geçmiş yükleme hatası: {str(e)}", ft.Colors.RED)
            print(f"History error: {e}")
            
        page.update()

    # --- ADMIN PANELİ ---
    def load_admin_dashboard():
        page.clean()
        
        try:
            # Veritabanından verileri çek
            rows = db.get_all_reservations_admin()
            
            # Tabloyu oluştur
            admin_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Öğrenci", weight="bold")),
                    ft.DataColumn(ft.Text("Oda", weight="bold")),
                    ft.DataColumn(ft.Text("Masa", weight="bold")),
                    ft.DataColumn(ft.Text("Tarih", weight="bold")),
                    ft.DataColumn(ft.Text("Durum", weight="bold")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(r[1])), # Ad Soyad
                        ft.DataCell(ft.Text(r[2])), # Oda Adı
                        ft.DataCell(ft.Text(str(r[3]))), # Masa No
                        ft.DataCell(ft.Text(r[4].strftime('%d.%m %H:%M'))), # Başlangıç
                        ft.DataCell(ft.Text(r[6])), # Durum
                    ]) for r in rows
                ],
                border=ft.border.all(1, "white10"),
                vertical_lines=ft.border.all(1, "white10"),
            )
            
            # DÜZELTME BURADA YAPILDI:
            # ft.Column içindeki 'padding' kaldırıldı.
            # Bunun yerine ft.Container kullanıldı.
            content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🔐 Yönetici Paneli", size=30, weight="bold"), 
                        ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: load_login_page(), tooltip="Çıkış Yap")
                    ], alignment="spaceBetween"),
                    ft.Text("Tüm Rezervasyonlar", color="grey"),
                    ft.Divider(),
                    ft.Container(content=admin_table, expand=True) # Tabloyu saran container
                ], expand=True, scroll=ft.ScrollMode.AUTO),
                
                padding=20, # Padding buraya (Container'a) verildi
                expand=True
            )

            page.add(content)

        except Exception as e:
            show_message(f"Admin panel hatası: {str(e)}", ft.Colors.RED)
            print(f"Admin panel error: {e}")
            import traceback
            traceback.print_exc()
            
        page.update()

    # Uygulamayı Başlat
    load_login_page()

ft.run(main)