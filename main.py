import flet as ft
from database import Database
from datetime import datetime, timedelta

# Veritabanı Bağlantısı
db_init = Database()

def main(page: ft.Page):
    page.title = "StudyFlow - Kampüs Rezervasyon"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0
    
    primary_color = ft.Colors.TEAL_400
    bg_color = ft.Colors.BLUE_GREY_900
    card_bg = ft.Colors.BLUE_GREY_800
    text_white = ft.Colors.WHITE
    text_grey = ft.Colors.GREY_400

    current_user = None 
    current_db = [db_init]      #Şu anda kimin işlem yaptığını ve ona göre hangi user ile database'e bağlanılacak bilgisi
    selected_room_id = [1]
    error_overlay = ft.Container(visible=False)
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def show_message(text, color=ft.Colors.GREEN):
        
        def close_overlay(e):
            error_overlay.visible = False
            page.update()
        
        if color == ft.Colors.GREEN:
            icon = ft.Icons.CHECK_CIRCLE
            icon_color = ft.Colors.GREEN_400
        else:
            icon = ft.Icons.ERROR
            icon_color = ft.Colors.RED_400
        
        error_overlay.content = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(icon, size=50, color=icon_color),
                        ft.Text("Bildirim", size=20, weight="bold"),
                        ft.Divider(),
                        ft.Text(text, size=14, text_align="center"),
                        ft.FilledButton(
                            "Tamam",
                            on_click=close_overlay,
                            style=ft.ButtonStyle(bgcolor=primary_color)
                        ),
                    ], spacing=15, tight=True, horizontal_alignment="center"),
                    padding=30,
                    width=400
                )
            ),
            bgcolor="#CC000000",
            alignment=ft.Alignment(0, 0),
            expand=True
        )
        error_overlay.visible = True
        page.update()



    #Register ekranı
    def load_register_page():
        page.clean()

        reg_error_overlay = ft.Container(visible=False)
        
        reg_name = ft.TextField(label="Ad", width=300, border_radius=15, prefix_icon=ft.Icons.PERSON)
        reg_surname = ft.TextField(label="Soyad", width=300, border_radius=15, prefix_icon=ft.Icons.PERSON_OUTLINE)
        reg_email = ft.TextField(label="E-posta", width=300, border_radius=15, prefix_icon=ft.Icons.EMAIL)
        reg_pass = ft.TextField(label="Şifre", password=True, width=300, border_radius=15, prefix_icon=ft.Icons.LOCK, can_reveal_password=True)

        def show_reg_message(text, color=ft.Colors.GREEN):
            def close_overlay(e):
                reg_error_overlay.visible = False
                page.update()
            
            icon = ft.Icons.CHECK_CIRCLE if color == ft.Colors.GREEN else ft.Icons.ERROR
            icon_color = ft.Colors.GREEN_400 if color == ft.Colors.GREEN else ft.Colors.RED_400
            
            reg_error_overlay.content = ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(icon, size=50, color=icon_color),
                            ft.Text("Bildirim", size=20, weight="bold"),
                            ft.Divider(),
                            ft.Text(text, size=14, text_align="center"),
                            ft.FilledButton("Tamam", on_click=close_overlay, style=ft.ButtonStyle(bgcolor=primary_color)),
                        ], spacing=15, tight=True, horizontal_alignment="center"),
                        padding=30,
                        width=400
                    )
                ),
                bgcolor="#CC000000",
                alignment=ft.Alignment(0, 0),
                expand=True
            )
            reg_error_overlay.visible = True
            page.update()

        def handle_register(e):
            if not reg_name.value or not reg_surname.value or not reg_email.value or not reg_pass.value:
                show_reg_message("Lütfen tüm alanları doldurun!", ft.Colors.RED)
                return

            #Kullanıcıyı kaydet
            res = db_init.register_user(reg_name.value, reg_surname.value, reg_email.value, reg_pass.value)
            
            if res == 'SUCCESS':
                show_reg_message("Kayıt Başarılı! Giriş yapabilirsiniz.", ft.Colors.GREEN)
            else:
                show_reg_message(res, ft.Colors.RED)

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

        page.add(
            ft.Stack([
                ft.Container(content=register_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color),
                reg_error_overlay
            ], expand=True)
        )
        page.update()


    # LOGIN EKRANI
    def load_login_page():
        page.clean()
        
        login_error_overlay = ft.Container(visible=False)
        
        email_input = ft.TextField(label="E-posta", width=300, border_radius=15, prefix_icon=ft.Icons.EMAIL)
        pass_input = ft.TextField(label="Şifre", password=True, width=300, border_radius=15, prefix_icon=ft.Icons.LOCK, can_reveal_password=True)

        def show_login_message(text, color=ft.Colors.GREEN):
            def close_overlay(e):
                login_error_overlay.visible = False
                page.update()
            
            icon = ft.Icons.CHECK_CIRCLE if color == ft.Colors.GREEN else ft.Icons.ERROR
            icon_color = ft.Colors.GREEN_400 if color == ft.Colors.GREEN else ft.Colors.RED_400
            
            login_error_overlay.content = ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(icon, size=50, color=icon_color),
                            ft.Text("Bildirim", size=20, weight="bold"),
                            ft.Divider(),
                            ft.Text(text, size=14, text_align="center"),
                            ft.FilledButton("Tamam", on_click=close_overlay, style=ft.ButtonStyle(bgcolor=primary_color)),
                        ], spacing=15, tight=True, horizontal_alignment="center"),
                        padding=30,
                        width=400
                    )
                ),
                bgcolor="#CC000000",
                alignment=ft.Alignment(0, 0),
                expand=True
            )
            login_error_overlay.visible = True
            page.update()

        def handle_login(e):
            nonlocal current_user
            user = db_init.login(email_input.value, pass_input.value)  #Kullanıcı login
            
            if user and user[3] == 'SUCCESS':
                current_user = user
                user_role = user[2] #Loginişlemi başarılı olursa artık kullanıcı bilinir database e kimin eriştiğini belirler
                
                # Kullanıcıya göre database bağlantısını güncelle
                if user_role == 'admin':
                    current_db[0] = Database('admin')
                else:
                    current_db[0] = Database('student')
                
                # Tamamlanan reservationları completed olarak update
                current_db[0].complete_past_reservations()
                
                show_login_message(f"Hoşgeldin {user[1]}!", ft.Colors.GREEN)
                page.update()
                import time
                time.sleep(0.5)
                
                if user_role == 'admin':
                    load_admin_dashboard()
                else:
                    load_student_dashboard()
            else:
                show_login_message("Hatalı E-posta veya Şifre!", ft.Colors.RED)

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
            ], alignment="center", horizontal_alignment="center"),
            width=400, height=550, bgcolor=card_bg, border_radius=20, padding=40,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK)
        )

        page.add(
            ft.Stack([
                ft.Container(content=login_card, alignment=ft.Alignment(0, 0), expand=True, bgcolor=bg_color),
                login_error_overlay
            ], expand=True)
        )
        page.update()


    # Student paneli
    def load_student_dashboard():
        page.clean()
        
        # Tamamlanan reservationları completed olarak update
        current_db[0].complete_past_reservations()
        
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

        page.add(
            ft.Stack([
                ft.Row([sidebar, ft.VerticalDivider(width=1, color="white10"), content_area], expand=True),
                error_overlay
            ], expand=True)
        )
        show_reservation_tab()
        page.update()


    #Reservations
    def show_reservation_tab():
            content_area.controls.clear()

            def is_time_in_past(date_str, hour):
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    check_time = date_obj.replace(hour=hour, minute=0, second=0, microsecond=0)
                    return check_time < datetime.now()
                except:
                    return False

            selected_table = {'id': None, 'num': None, 'card': None}
            table_cards = {}

            #Odaları getir
            rooms = current_db[0].get_rooms() or []

            if not rooms:
                content_area.controls.append(ft.Text("Veritabanında oda bulunamadı!", color=ft.Colors.RED))
                page.update()
                return

            room_options = [ft.dropdown.Option(key=str(r[0]), text=r[1]) for r in rooms]

            if not selected_room_id or selected_room_id[0] not in [r[0] for r in rooms]:
                selected_room_id[0] = rooms[0][0]

            room_dropdown = ft.Dropdown(
                label="Çalışma Odası Seç",
                width=250,
                options=room_options,
                value=str(selected_room_id[0])
            )

            #Tarih ve saat
            date_picker = ft.TextField(
                label="Tarih",
                value=datetime.now().strftime("%Y-%m-%d"),
                width=150,
                hint_text="YYYY-MM-DD",
                prefix_icon=ft.Icons.CALENDAR_TODAY
            )

            def get_default_times():
                now = datetime.now()
                today = now.strftime("%Y-%m-%d")
                
                # Eğer bugün seçiliyse şu anki saatten 1 saat sonra başlat
                if date_picker.value == today:
                    start_default = min(now.hour + 1, 21)
                    end_default = min(start_default + 2, 22)
                else:
                    # Gelecek günler için varsayılan 9-11
                    start_default = 9
                    end_default = 11
                
                return str(start_default), str(end_default)

            def on_date_change(e):
                default_start, default_end = get_default_times()
                start_hour.value = default_start
                end_hour.value = default_end
                page.update()

            date_picker.on_change = on_date_change
            default_start, default_end = get_default_times()

            start_hour = ft.Dropdown(
                label="Başlangıç Saati",
                options=[ft.dropdown.Option(str(i)) for i in range(9, 22)],
                value=default_start,
                width=140
            )

            end_hour = ft.Dropdown(
                label="Bitiş Saati",
                options=[ft.dropdown.Option(str(i)) for i in range(10, 23)],
                value=default_end,
                width=140
            )

            tables_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

            sel_text = ft.Text("", size=14, weight="bold")

            def cancel_selection(e=None):
                if selected_table['card']:
                    selected_table['card'].bgcolor = ft.Colors.GREEN_700
                    try:
                        selected_table['card'].content.controls[2].value = 'BOŞ'
                    except Exception:
                        pass
                    selected_table['card'] = None
                selected_table['id'] = None
                selected_table['num'] = None
                confirm_bar.visible = False
                page.update()

            #Reservation oluşturmayı onaylama
            def confirm_selection(e):
                if not selected_table['id'] or not current_user:
                    show_message('Lütfen önce masa seçin ve giriş yapın!', ft.Colors.RED)
                    return
                try:
                    date_str = date_picker.value
                    start_h = int(start_hour.value)
                    end_h = int(end_hour.value)

                    if end_h <= start_h:
                        show_message('Bitiş saati başlangıç saatinden sonra olmalı!', ft.Colors.RED)
                        return

                    # Geçmiş zaman kontrolü
                    if is_time_in_past(date_str, start_h):
                        show_message('Geçmiş bir zaman için rezervasyon yapamazsınız!', ft.Colors.RED)
                        return

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    start_time = date_obj.replace(hour=start_h, minute=0, second=0, microsecond=0)
                    end_time = date_obj.replace(hour=end_h, minute=0, second=0, microsecond=0)

                    #Reservation OLuştur
                    res = current_db[0].create_reservation(current_user[0], selected_table['id'], start_time, end_time)

                    if res == 'SUCCESS':
                        show_message('Rezervasyon Başarılı!', ft.Colors.GREEN)
                        c = selected_table['card']
                        if c:
                            c.bgcolor = ft.Colors.RED_800
                            try:
                                c.content.controls[2].value = 'DOLU'
                                c.content.controls[3].value = f"{end_time.strftime('%H:%M')}'e kadar"
                            except Exception:
                                pass
                        cancel_selection()
                        refresh_grid()
                    
                    #Günde 1den fazla reservation yapılmaya çalışırsa trigger tetiklenir kullanıcıyı bilgilendir
                    else:
                        show_message(res, ft.Colors.RED)
                except ValueError:
                    show_message('Geçersiz tarih formatı! YYYY-MM-DD formatında girin.', ft.Colors.RED)
                except Exception as ex:
                    show_message(f"Rezervasyon hatası: {str(ex)}", ft.Colors.RED)

            confirm_bar = ft.Container(
                content=ft.Row([
                    sel_text,
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

            def refresh_grid(e=None):

                # Tamamlanan reservationları completed olarak update
                current_db[0].complete_past_reservations()
                
                try:
                    room_id = int(room_dropdown.value)
                    selected_room_id[0] = room_id

                    date_str = date_picker.value
                    start_h = int(start_hour.value)
                    end_h = int(end_hour.value)

                    if end_h <= start_h:
                        show_message('Bitiş saati başlangıç saatinden sonra olmalı!', ft.Colors.RED)
                        return

                    # Geçmiş zaman kontrolü
                    if is_time_in_past(date_str, start_h):
                        show_message('Geçmiş bir zaman için rezervasyon yapamazsınız!', ft.Colors.RED)
                        return

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    check_start = date_obj.replace(hour=start_h, minute=0, second=0, microsecond=0)
                    check_end = date_obj.replace(hour=end_h, minute=0, second=0, microsecond=0)


                except ValueError:
                    show_message('Geçersiz tarih formatı! YYYY-MM-DD formatında girin.', ft.Colors.RED)
                    return
                except Exception as ex:
                    show_message(f"Hata: {str(ex)}", ft.Colors.RED)
                    return

                cancel_selection()
                table_cards.clear()
                tables_container.controls.clear()
                
                #Oda ve gerekli tarih saat seçildikten sonra belirlenen zaman göre masaları ve durumları getir
                try:

                    #Tüm masaları durumları ile ve reservationu olan masaları getir
                    statuses = current_db[0].get_room_status(room_id, check_start)
                    avail_tables = current_db[0].get_available_tables_for_timerange(room_id, check_start, check_end)

                    if not statuses:
                        tables_container.controls.append(
                            ft.Container(
                                content=ft.Text("Bu odada tanımlı masa yok.", size=16, color=ft.Colors.ORANGE),
                                padding=20
                            )
                        )
                    else:
                        rows = []
                        current_row = []

                        for idx, table in enumerate(statuses):
                            t_id, t_num, status_at_start, until_time = table

                            is_empty = t_num in avail_tables
                            
                            bg_c = ft.Colors.GREEN_700 if is_empty else ft.Colors.RED_800
                            icon = ft.Icons.CHAIR if is_empty else ft.Icons.PERSON_OFF
                            status_text = 'BOŞ' if is_empty else 'DOLU'
                            
                            if is_empty:
                                time_info = "Seçilen zaman aralığında müsait"
                            else:
                                time_info = "Zaman aralığında dolu"

                            card = ft.Container(
                                content=ft.Column([
                                    ft.Icon(icon, size=30, color="white"),
                                    ft.Text(f"Masa {t_num}", size=14, weight="bold"),
                                    ft.Text(status_text, size=11, color="white70"),
                                    ft.Text(
                                        time_info,
                                        size=9, 
                                        color="white60",
                                        text_align="center"
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3),
                                bgcolor=bg_c,
                                border_radius=12,
                                padding=8,
                                width=110,
                                height=110,
                                ink=True
                            )

                            table_cards[t_num] = (t_id, card, is_empty)

                            def make_on_click(tid, tnum, free, c):
                                def _on_click(e):
                                    toggle_select(tid, tnum, c, free)
                                return _on_click

                            card.on_click = make_on_click(t_id, t_num, is_empty, card)
                            current_row.append(card)

                            if len(current_row) == 6 or idx == len(statuses) - 1:
                                rows.append(ft.Row(controls=current_row, spacing=10, wrap=False))
                                current_row = []

                        tables_container.controls.extend(rows)

                except Exception as e:
                    print(f"HATA: Grid yenileme: {e}")
                    import traceback
                    traceback.print_exc()
                    tables_container.controls.append(ft.Text(f"Hata oluştu: {e}", color=ft.Colors.RED))

                page.update()

            def on_room_change(e):
                refresh_grid()

            room_dropdown.on_change = on_room_change

            def toggle_select(tid, tnum, card, free):
                if not free:
                    show_message('Bu masa seçilen zaman aralığında dolu!', ft.Colors.RED)
                    return

                if selected_table['id'] == tid:
                    cancel_selection()
                    return

                if selected_table['card']:
                    try:
                        selected_table['card'].bgcolor = ft.Colors.GREEN_700
                        selected_table['card'].content.controls[2].value = 'BOŞ'
                    except Exception:
                        pass

                selected_table['id'] = tid
                selected_table['num'] = tnum
                selected_table['card'] = card

                card.bgcolor = ft.Colors.GREY_600
                try:
                    card.content.controls[2].value = 'SEÇİLDİ'
                except Exception:
                    pass

                sel_text.value = f"Seçilen Masa: {tnum}"
                confirm_bar.visible = True
                page.update()

            #Öneri al
            def get_suggestion(e):
                try:
                    room_id = int(room_dropdown.value)
                    date_str = date_picker.value
                    start_h = int(start_hour.value)
                    end_h = int(end_hour.value)
                    duration = end_h - start_h
                    
                    
                    if duration <= 0:
                        show_message('Geçerli bir süre belirtin!', ft.Colors.RED)
                        return
                    
                    if duration > 13:
                        show_message('Maksimum süre 13 saat olabilir!', ft.Colors.RED)
                        return
                    
                    #çalışılmak istenen saat miktarı kadar tüm olasılıkları yoğunluğa göre belirle ve yazdır
                    result = current_db[0].find_best_time_window(room_id, date_str, duration)
                    
                    if not result:
                        show_message('Öneri alınamadı!', ft.Colors.RED)
                        return
                    
                    best_start = result['best_start_hour']
                    best_end = result['best_end_hour']
                    max_avail = result['max_available']
                    all_windows = result['all_windows']
                    
                    if best_start is None:
                        show_message('Üzgünüz, seçilen tarihte uygun zaman bulunamadı!', ft.Colors.RED)
                        return
                    suggestion_cards = []
                    
                    for window in all_windows:
                        s_hour = window['start_hour']
                        e_hour = window['end_hour']
                        avail_count = window['available_count']
                        status = window['status']
                        
                        if status == 'past':
                            bg_color = ft.Colors.GREY_800
                            icon = ft.Icons.HISTORY
                            icon_color = ft.Colors.GREY_400
                            border_color = ft.Colors.GREY_700
                            is_disabled = True
                        elif status == 'full':
                            bg_color = ft.Colors.RED_900
                            icon = ft.Icons.BLOCK
                            icon_color = ft.Colors.RED_300
                            border_color = ft.Colors.RED_800
                            is_disabled = True
                        elif s_hour == best_start and e_hour == best_end:
                            bg_color = ft.Colors.GREEN_900
                            icon = ft.Icons.STAR
                            icon_color = ft.Colors.YELLOW_400
                            border_color = ft.Colors.GREEN_400
                            is_disabled = False
                        elif avail_count >= max_avail * 0.7:
                            bg_color = ft.Colors.GREEN_800
                            icon = ft.Icons.CHECK_CIRCLE
                            icon_color = ft.Colors.GREEN_300
                            border_color = ft.Colors.GREEN_700
                            is_disabled = False
                        elif avail_count >= max_avail * 0.4:
                            bg_color = ft.Colors.ORANGE_900
                            icon = ft.Icons.WARNING_AMBER
                            icon_color = ft.Colors.ORANGE_300
                            border_color = ft.Colors.ORANGE_700
                            is_disabled = False
                        else:
                            bg_color = ft.Colors.RED_800
                            icon = ft.Icons.PEOPLE
                            icon_color = ft.Colors.RED_300
                            border_color = ft.Colors.RED_700
                            is_disabled = False
                        
                        def make_time_selector(sel_start, sel_end):
                            def select_time(e):
                                start_hour.value = str(sel_start)
                                end_hour.value = str(sel_end)
                                bs.open = False
                                page.update()
                                refresh_grid()
                                show_message(
                                    f'Saat {sel_start}:00 - {sel_end}:00 seçildi!',
                                    ft.Colors.GREEN
                                )
                            return select_time
                        
                        card = ft.Container(
                            content=ft.Row([
                                ft.Icon(icon, color=icon_color, size=30),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text(
                                                f"{s_hour}:00 - {e_hour}:00",
                                                size=16,
                                                weight="bold"
                                            )
                                        ]),
                                        ft.Text(
                                            f"{avail_count} masa müsait" if status == 'available' 
                                                else "Geçmiş zaman" if status == 'past'
                                                else "Dolu",
                                            size=12,
                                            color="white70"
                                        )
                                    ], spacing=2),
                                    expand=True
                                ),
                                ft.FilledButton(
                                    "Seç",
                                    on_click=make_time_selector(s_hour, e_hour),
                                    style=ft.ButtonStyle(bgcolor=primary_color),
                                    disabled=is_disabled
                                ) if not is_disabled else ft.Text(
                                    "Dolu" if status == 'full' else "Geçmiş",
                                    color=ft.Colors.GREY_400
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            bgcolor=bg_color,
                            border_radius=10,
                            padding=15,
                            margin=5,
                            border=ft.Border.all(2, border_color)
                        )
                        
                        suggestion_cards.append(card)
                    def quick_select(e):
                        start_hour.value = str(best_start)
                        end_hour.value = str(best_end)
                        bs.open = False
                        page.update()
                        refresh_grid()
                        show_message(
                            f'En iyi zaman seçildi: {best_start}:00 - {best_end}:00',
                            ft.Colors.GREEN
                        )
                    
                    def close_sheet(e):
                        print("Sheet closed")
                        bs.open = False
                        page.update()
                    
                    bs = ft.BottomSheet(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("En İyi Zaman Önerisi", size=22, weight="bold"),
                                    ft.IconButton(
                                        icon=ft.Icons.CLOSE,
                                        on_click=close_sheet,
                                        tooltip="Kapat"
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                
                                ft.Divider(),
                            
                                ft.Container(
                                    content=ft.Row([
                                        ft.Column([
                                            ft.Text(
                                                f"En İyi: {best_start}:00 - {best_end}:00",
                                                size=18,
                                                weight="bold",
                                                color=ft.Colors.GREEN_300
                                            ),
                                            ft.Text(
                                                f"{max_avail} masa müsait (En sakin zaman)",
                                                size=14,
                                                color="white70"
                                            )
                                        ], spacing=2)
                                    ]),
                                    bgcolor=ft.Colors.GREEN_900,
                                    padding=15,
                                    border_radius=10,
                                    border=ft.Border.all(2, ft.Colors.GREEN_400)
                                ),
                                
                                ft.Divider(),
                                
                                ft.Text(
                                    f"{date_str} | {duration} saat",
                                    size=14,
                                    weight="bold",
                                    color=ft.Colors.CYAN_200
                                ),
                                
                                ft.Text(
                                    "Tüm zaman dilimleri (en iyiden en kötüye):",
                                    size=12,
                                    color="white70"
                                ),
                                
                                ft.Container(
                                    content=ft.Column(
                                        suggestion_cards,
                                        scroll=ft.ScrollMode.AUTO,
                                    ),
                                    height=300,
                                    border_radius=10
                                ),
                                
                                ft.Row([
                                    ft.FilledButton(
                                        "En İyiyi Seç",
                                        icon=ft.Icons.STAR,
                                        on_click=quick_select,
                                        style=ft.ButtonStyle(bgcolor=primary_color),
                                        expand=True
                                    ),
                                    ft.OutlinedButton(
                                        "Kapat",
                                        on_click=close_sheet,
                                        expand=True
                                    )
                                ], spacing=10)
                                
                            ], spacing=15, scroll=ft.ScrollMode.AUTO),
                            padding=20,
                            bgcolor=card_bg,
                            border_radius=ft.BorderRadius(20, 20, 0, 0)
                        ),
                        open=True
                    )
                    
                    page.overlay.append(bs)
                    bs.open = True
                    page.update()
                    
                except ValueError as ve:
                    print(f"ValueError: {ve}")
                    import traceback
                    traceback.print_exc()
                    show_message('Geçersiz tarih formatı!', ft.Colors.RED)
                    
                except Exception as ex:
                    print(f"ERROR: {ex}")
                    import traceback
                    traceback.print_exc()
                    show_message(f"Öneri alınamadı: {str(ex)}", ft.Colors.RED)

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

            filters = ft.Column([
                ft.Row([room_dropdown, date_picker], spacing=20),
                ft.Row([start_hour, end_hour], spacing=20),
                ft.FilledButton(
                    "Masaları Göster",
                    icon=ft.Icons.SEARCH,
                    on_click=refresh_grid,
                    style=ft.ButtonStyle(bgcolor=primary_color)
                )
            ], spacing=10)

            content_area.controls.extend([
                ft.Container(content=header, padding=20),
                ft.Container(content=filters, padding=ft.padding.only(left=20, right=20, bottom=20)),
                ft.Container(content=confirm_bar, padding=ft.padding.only(left=20, right=20, bottom=10)),
                ft.Container(content=tables_container, expand=True, padding=20)
            ])

            refresh_grid()
            page.update()

    #Kullanıcı istatistikleri ve verimlilik
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
                #Kullanıcı istatistiklerini geitr
                stats = current_db[0].get_user_stats(current_user[0], period_drop.value)
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

    #Kullanıcı geçmişi
    def show_history_tab():
        content_area.controls.clear()
        
        def refresh_history():
            content_area.controls.clear()
            
            overlay_container = ft.Container(visible=False)
            
            try:
                # Tamamlanan reservationları completed olarak update
                current_db[0].complete_past_reservations()
                
                #Kullanıcının reservationlarını getir
                rows = current_db[0].get_my_reservations(current_user[0])
                
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
                    #Kullanıcı aktif reservationlarını cancelled olarak güncelleyebilşir
                    def cancel_reservation(res_id, start_time, status):
                        
                        if status == 'cancelled':
                            show_message("Bu rezervasyon zaten iptal edilmiş!", ft.Colors.ORANGE)
                            return
                        
                        if status == 'completed':
                            show_message("Tamamlanmış rezervasyon iptal edilemez!", ft.Colors.ORANGE)
                            return
                        
                        
                        def confirm_cancel(e):
                            overlay_container.visible = False
                            page.update()
                            
                            # Seçilen reservationu cancelled olarak güncelle
                            result = current_db[0].cancel_reservation(res_id)
                            
                            if result == "SUCCESS":
                                show_message("Rezervasyon başarıyla iptal edildi!", ft.Colors.GREEN)
                                refresh_history()
                            else:
                                show_message(result, ft.Colors.RED)
                        
                        def close_overlay(e):
                            overlay_container.visible = False
                            page.update()
                        
                        overlay_container.content = ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("Rezervasyonu İptal Et", size=20, weight="bold"),
                                        ft.Divider(),
                                        ft.Text(
                                            f"Rezervasyon ID: {res_id}\n\n"
                                            "Bu rezervasyonu iptal etmek istediğinizden emin misiniz?",
                                            size=14
                                        ),
                                        ft.Row([
                                            ft.TextButton("Hayır", on_click=close_overlay),
                                            ft.FilledButton(
                                                "Evet, İptal Et",
                                                on_click=confirm_cancel,
                                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700)
                                            ),
                                        ], alignment=ft.MainAxisAlignment.END)
                                    ], spacing=15, tight=True),
                                    padding=20,
                                    width=400
                                )
                            ),
                            bgcolor="#CC000000",
                            alignment=ft.Alignment(0, 0),
                            expand=True
                        )
                        overlay_container.visible = True
                        page.update()
                    
                    data_rows = []
                    
                    def make_cancel_handler(reservation_id, start_dt, res_status):
                        def handler(e):
                            cancel_reservation(reservation_id, start_dt, res_status)
                        return handler
                    
                    for r in rows:
                        res_id = r[0]
                        room_name = r[1]
                        table_num = r[2]
                        start_time = r[3]
                        end_time = r[4]
                        status = r[5]
                        

                        now = datetime.now()
                        
                        if hasattr(start_time, 'tzinfo') and start_time.tzinfo is not None:
                            start_time_naive = start_time.replace(tzinfo=None)
                        else:
                            start_time_naive = start_time
                        
                        
                        can_cancel = (status == 'active')
                        

                        if status == 'active':
                            status_badge = ft.Container(
                                content=ft.Text("Active", size=12, color="white"),
                                bgcolor=ft.Colors.GREEN_700,
                                padding=5,
                                border_radius=5
                            )
                        elif status == 'completed':
                            status_badge = ft.Container(
                                content=ft.Text("Completed", size=12, color="white"),
                                bgcolor=ft.Colors.BLUE_700,
                                padding=5,
                                border_radius=5
                            )
                        else:  # cancelled
                            status_badge = ft.Container(
                                content=ft.Text("Cancelled", size=12, color="white"),
                                bgcolor=ft.Colors.RED_700,
                                padding=5,
                                border_radius=5
                            )
                        
                        
                        if can_cancel:
                            cancel_btn = ft.IconButton(
                                icon=ft.Icons.CANCEL,
                                icon_color=ft.Colors.RED_400,
                                tooltip="İptal Et",
                                on_click=make_cancel_handler(res_id, start_time, status)
                            )
                        else:
                            cancel_btn = ft.Icon(ft.Icons.BLOCK, color=ft.Colors.GREY_600, size=20)
                        
                        data_rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(room_name)),
                                ft.DataCell(ft.Text(str(table_num))),
                                ft.DataCell(ft.Text(start_time.strftime('%d.%m %H:%M'))),
                                ft.DataCell(ft.Text(end_time.strftime('%d.%m %H:%M'))),
                                ft.DataCell(status_badge),
                                ft.DataCell(cancel_btn),
                            ])
                        )
                    
                    data_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Oda", weight="bold")),
                            ft.DataColumn(ft.Text("Masa", weight="bold")),
                            ft.DataColumn(ft.Text("Başlangıç", weight="bold")),
                            ft.DataColumn(ft.Text("Bitiş", weight="bold")),
                            ft.DataColumn(ft.Text("Durum", weight="bold")),
                            ft.DataColumn(ft.Text("İşlem", weight="bold")),
                        ],
                        rows=data_rows,
                        border=ft.border.all(1, "white10"),
                    )
                    
                    content_area.controls.extend([
                        ft.Stack([
                            ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        ft.Text("📜 Rezervasyon Geçmişim", size=30, weight="bold"),
                                        ft.IconButton(
                                            icon=ft.Icons.REFRESH,
                                            tooltip="Yenile",
                                            on_click=lambda e: refresh_history()
                                        )
                                    ], alignment="spaceBetween"),
                                    padding=20
                                ),
                                ft.Divider(),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("💡 İpucu: Aktif durumdaki tüm rezervasyonlarınızı iptal edebilirsiniz.", 
                                               size=12, color=text_grey, italic=True),
                                        data_table
                                    ]),
                                    padding=20
                                )
                            ]),
                            overlay_container
                        ], expand=True)
                    ])
            except Exception as e:
                show_message(f"Geçmiş yükleme hatası: {str(e)}", ft.Colors.RED)
                print(f"History error: {e}")
                import traceback
                traceback.print_exc()
                
            page.update()
        

        refresh_history()

    #Admin Paneli
    def load_admin_dashboard():
        page.clean()
        
        admin_content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        
        
        def show_all_reservations():
            admin_content.controls.clear()
            
            try:
                #Tüm reservationları getir
                rows = current_db[0].get_all_reservations_admin()
                
                if not rows:
                    admin_content.controls.append(
                        ft.Container(
                            content=ft.Text("Henüz rezervasyon bulunmuyor.", size=16),
                            padding=20
                        )
                    )
                else:
                    admin_table = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Öğrenci", weight="bold")),
                            ft.DataColumn(ft.Text("Oda", weight="bold")),
                            ft.DataColumn(ft.Text("Masa", weight="bold")),
                            ft.DataColumn(ft.Text("Başlangıç", weight="bold")),
                            ft.DataColumn(ft.Text("Bitiş", weight="bold")),
                            ft.DataColumn(ft.Text("Durum", weight="bold")),
                        ],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(r[1])),
                                ft.DataCell(ft.Text(r[2])),
                                ft.DataCell(ft.Text(str(r[3]))),
                                ft.DataCell(ft.Text(r[4].strftime('%d.%m %H:%M'))),
                                ft.DataCell(ft.Text(r[5].strftime('%d.%m %H:%M'))),
                                ft.DataCell(ft.Text(r[6])),
                            ]) for r in rows
                        ],
                        border=ft.border.all(1, "white10"),
                        vertical_lines=ft.border.all(1, "white10"),
                    )
                    
                    admin_content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Tüm Rezervasyonlar", size=20, weight="bold"),
                                ft.Text(f"Toplam: {len(rows)} rezervasyon", color=text_grey, size=14),
                                ft.Divider(),
                                admin_table
                            ]),
                            padding=20
                        )
                    )
            except Exception as e:
                show_message(f"Rezervasyon listesi hatası: {str(e)}", ft.Colors.RED)
                print(f"Admin reservations error: {e}")
            
            page.update()
        
        def show_loyalty_users():
            admin_content.controls.clear()
            
            try:
                #En sadık 3 kullanıcıyı getir
                loyalty_users = current_db[0].get_loyalty_users()
                
                if not loyalty_users:
                    admin_content.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.EMOJI_EVENTS, size=60, color=ft.Colors.AMBER_400),
                                ft.Text("Henüz 5+ rezervasyonu olan kullanıcı yok", size=16)
                            ], horizontal_alignment="center"),
                            padding=40
                        )
                    )
                else:
                    
                    user_cards = []
                    medals = [ft.Icons.LOOKS_ONE, ft.Icons.LOOKS_TWO, ft.Icons.LOOKS_3]
                    medal_colors = [ft.Colors.AMBER_400, ft.Colors.GREY_400, ft.Colors.ORANGE_400]
                    
                    for idx, user in enumerate(loyalty_users):
                        user_id, full_name, email, total_res, total_time = user
                        
                        card = ft.Card(
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Icon(medals[idx], size=50, color=medal_colors[idx]),
                                    ft.Column([
                                        ft.Text(full_name, size=18, weight="bold"),
                                        ft.Text(email, size=12, color=text_grey),
                                        ft.Row([
                                            ft.Icon(ft.Icons.BOOKMARK, size=16, color=primary_color),
                                            ft.Text(f"{total_res} rezervasyon", size=14),
                                            ft.Container(width=20),
                                            ft.Icon(ft.Icons.TIMER, size=16, color=primary_color),
                                            ft.Text(f"{total_time}", size=14),
                                        ], spacing=5)
                                    ], spacing=5, expand=True)
                                ], spacing=20),
                                padding=20
                            )
                        )
                        user_cards.append(card)
                    
                    admin_content.controls.extend([
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.EMOJI_EVENTS, size=40, color=ft.Colors.AMBER_400),
                                    ft.Text("Sadık Kullanıcılar", size=24, weight="bold")
                                ], spacing=10),
                                ft.Text("5+ tamamlanmış rezervasyonu olan ilk 3 kullanıcı", 
                                       color=text_grey, size=14),
                                ft.Divider(),
                                *user_cards
                            ]),
                            padding=20
                        )
                    ])
            except Exception as e:
                show_message(f"Loyalty listesi hatası: {str(e)}", ft.Colors.RED)
                print(f"Loyalty users error: {e}")
            
            page.update()
        
        def show_user_management():
            admin_content.controls.clear()
            
            
            overlay_container = ft.Container(visible=False)
            
            def refresh_users():
                try:
                    #Tüm kullanıcıları getir
                    users = current_db[0].get_all_users()
                    
                    if not users:
                        admin_content.controls.append(
                            ft.Container(
                                content=ft.Text("Kullanıcı bulunamadı.", size=16),
                                padding=20
                            )
                        )
                    else:
                        def delete_user(uid, uname, urole):
                            if urole == 'admin':
                                show_message("Admin kullanıcısı silinemez!", ft.Colors.ORANGE)
                                return
                            
                            
                            def confirm_delete(e):
                                overlay_container.visible = False
                                page.update()
                                
                                #Seçilen kullanıcıyı sil
                                result = current_db[0].delete_user(uid)
                                
                                if result == "SUCCESS":
                                    show_message(f"{uname} başarıyla silindi!", ft.Colors.GREEN)
                                    show_user_management() 
                                else:
                                    show_message(result, ft.Colors.RED)
                            
                            def close_overlay(e):
                                overlay_container.visible = False
                                page.update()
                            
                            
                            overlay_container.content = ft.Container(
                                content=ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Icon(ft.Icons.WARNING_AMBER, size=50, color=ft.Colors.ORANGE_400),
                                            ft.Text("Kullanıcıyı Sil", size=20, weight="bold"),
                                            ft.Divider(),
                                            ft.Text(
                                                f"Kullanıcı: {uname}\n\n"
                                                "Bu kullanıcı ve TÜM rezervasyonları silinecek!\n"
                                                "Bu işlem geri alınamaz. Emin misiniz?",
                                                size=14,
                                                text_align="center"
                                            ),
                                            ft.Row([
                                                ft.TextButton("Hayır", on_click=close_overlay),
                                                ft.FilledButton(
                                                    "Evet, Sil",
                                                    on_click=confirm_delete,
                                                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700)
                                                ),
                                            ], alignment=ft.MainAxisAlignment.END)
                                        ], spacing=15, tight=True, horizontal_alignment="center"),
                                        padding=30,
                                        width=450
                                    )
                                ),
                                bgcolor="#CC000000",
                                alignment=ft.Alignment(0, 0),
                                expand=True
                            )
                            overlay_container.visible = True
                            page.update()
                        
                        def make_delete_handler(user_id, user_name, user_role):
                            def handler(e):
                                delete_user(user_id, user_name, user_role)
                            return handler
                        
                        
                        user_rows = []
                        for user in users:
                            uid, full_name, email, role, created_at, total_res = user
                            
                            
                            if role == 'admin':
                                role_badge = ft.Container(
                                    content=ft.Text("Admin", size=11, color="white"),
                                    bgcolor=ft.Colors.PURPLE_700,
                                    padding=5,
                                    border_radius=5
                                )
                            else:
                                role_badge = ft.Container(
                                    content=ft.Text("Student", size=11, color="white"),
                                    bgcolor=ft.Colors.BLUE_700,
                                    padding=5,
                                    border_radius=5
                                )
                            
                            
                            if role == 'admin':
                                delete_btn = ft.Icon(ft.Icons.BLOCK, color=ft.Colors.GREY_600, size=20)
                            else:
                                delete_btn = ft.IconButton(
                                    icon=ft.Icons.DELETE_FOREVER,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Kullanıcıyı Sil",
                                    on_click=make_delete_handler(uid, full_name, role)
                                )
                            
                            user_rows.append(
                                ft.DataRow(cells=[
                                    ft.DataCell(ft.Text(str(uid))),
                                    ft.DataCell(ft.Text(full_name)),
                                    ft.DataCell(ft.Text(email)),
                                    ft.DataCell(role_badge),
                                    ft.DataCell(ft.Text(created_at.strftime('%d.%m.%Y') if created_at else "-")),
                                    ft.DataCell(ft.Text(str(total_res))),
                                    ft.DataCell(delete_btn),
                                ])
                            )
                        
                        users_table = ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("ID", weight="bold")),
                                ft.DataColumn(ft.Text("Ad Soyad", weight="bold")),
                                ft.DataColumn(ft.Text("E-posta", weight="bold")),
                                ft.DataColumn(ft.Text("Rol", weight="bold")),
                                ft.DataColumn(ft.Text("Kayıt Tarihi", weight="bold")),
                                ft.DataColumn(ft.Text("Rezervasyon", weight="bold")),
                                ft.DataColumn(ft.Text("İşlem", weight="bold")),
                            ],
                            rows=user_rows,
                            border=ft.border.all(1, "white10"),
                        )
                        
                        admin_content.controls.clear()
                        admin_content.controls.append(
                            ft.Stack([
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text("Kullanıcı Yönetimi", size=20, weight="bold"),
                                            ft.IconButton(
                                                icon=ft.Icons.REFRESH,
                                                tooltip="Yenile",
                                                on_click=lambda e: refresh_users()
                                            )
                                        ], alignment="spaceBetween"),
                                        ft.Text(f"Toplam: {len(users)} kullanıcı", color=text_grey, size=14),
                                        ft.Divider(),
                                        users_table
                                    ]),
                                    padding=20
                                ),
                                overlay_container
                            ], expand=True)
                        )
                except Exception as e:
                    show_message(f"Kullanıcı listesi hatası: {str(e)}", ft.Colors.RED)
                    print(f"User management error: {e}")
                    import traceback
                    traceback.print_exc()
                
                page.update()
            
            refresh_users()
        
        admin_sidebar = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=30, color=primary_color),
                    ft.Text("Admin Panel", size=20, weight="bold")
                ], alignment="center"),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LIST),
                    title=ft.Text("Tüm Rezervasyonlar"),
                    on_click=lambda e: show_all_reservations()
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EMOJI_EVENTS, color=ft.Colors.AMBER_400),
                    title=ft.Text("Sadık Kullanıcılar"),
                    on_click=lambda e: show_loyalty_users()
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PEOPLE),
                    title=ft.Text("Kullanıcı Yönetimi"),
                    on_click=lambda e: show_user_management()
                ),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EXIT_TO_APP, color="red"),
                    title=ft.Text("Çıkış", color="red"),
                    on_click=lambda e: load_login_page()
                ),
            ]),
            width=250,
            bgcolor=card_bg,
            padding=20,
            height=800
        )
        
        page.add(ft.Row([admin_sidebar, ft.VerticalDivider(width=1, color="white10"), admin_content], expand=True))
        
        show_all_reservations()
        page.update()

    load_login_page()

ft.run(main)