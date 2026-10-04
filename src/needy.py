import flet as ft
import database as db
import login as lg

class Need:
    def __init__(self, category, description, volunteer=None, needy = None, completed=False):
        self.category = category
        self.description = description
        self.volunteer = volunteer
        self.needy = needy
        self.completed = completed

def select_needy(page: ft.Page, menu_return, user_id):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )

    btn_width = 410
    btn_height = 150

    content = ft.Column(
        controls=[
            ft.FilledButton(
                content=ft.Text("DODAJ POTRZEBĘ", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: add_need(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("MOJE POTRZEBY", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_need_list(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#8b0333",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("MOJE KONTO", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_profile(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30
    )

    page.add(content)

def add_need(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    category_list = ["Zakupy", "Gotowanie", "Sprzątanie", "Towarzyszenie", "Technologia", "Inne"]
    selected_category = [None]
    error_text = ft.Text("", color=ft.Colors.RED, size=16, weight=ft.FontWeight.BOLD)
    
    category_buttons = []
    
    def select_category(e, cat_name):
        selected_category[0] = cat_name
        for btn in category_buttons:
            if btn.data == cat_name:
                btn.style = ft.ButtonStyle(bgcolor="#8b0333", shape=ft.RoundedRectangleBorder(radius=15)) 
            else:
                btn.style = ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=15))
        error_text.value = ""
        page.update()
        
    for category_name in category_list:
        btn = ft.FilledButton(
            content=ft.Text(category_name.upper(), size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            data=category_name,
            on_click=lambda e, cat=category_name: select_category(e, cat),
            style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=15)),
            width=175,
            height=75,
        )
        category_buttons.append(btn)
        
    grid = ft.Row(
        controls=category_buttons,
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        run_spacing=10,
        width=370
    )

    description_field = ft.TextField(
        hint_text="Krótki opis (opcjonalnie)",
        bgcolor=ft.Colors.WHITE,
        border_color="#132434",
        border_radius=10,
        height=100,
        multiline=True,
        text_style=ft.TextStyle(size=18, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        content_padding=15,
        width=370
    )

    def submit_need(e):
        if not selected_category[0]:
            error_text.value = "BŁĄD: MUSISZ WYBRAĆ KATEGORIĘ!"
            page.update()
            return
            
        try:
            import database as db
            ins_conn = db.get_db_connection()
            ins_cur = ins_conn.cursor()
            ins_cur.execute(
                "INSERT INTO potrzeba (nazwa_potrzeba, opis, id_potrzebujacego) VALUES (%s, %s, %s)",
                (selected_category[0], description_field.value, user_id)
            )
            ins_conn.commit()
            ins_cur.close()
            ins_conn.close()
            
            snack = ft.SnackBar(ft.Text("Potrzeba została pomyślnie dodana!", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            
            select_needy(page, menu_return, user_id)
        except Exception as err:
            error_text.value = f"Błąd bazy danych: {err}"
            page.update()

    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("WYBIERZ KATEGORIĘ", size=20, weight=ft.FontWeight.BOLD, color="#132434"),
                grid,
                ft.Container(height=10),
                ft.Text("DODATKOWY OPIS", size=20, weight=ft.FontWeight.BOLD, color="#132434"),
                description_field,
                error_text,
                ft.Container(height=10),
                ft.FilledButton(
                    content=ft.Text("DODAJ POTRZEBĘ", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=submit_need,
                    style=ft.ButtonStyle(
                        bgcolor="#8b0333",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=370,
                    height=65
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def view_need_list(page: ft.Page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()

    # 1. Potrzeby aktywne wraz z przypisanym wolontariuszem (JOIN)
    cur.execute("""
        SELECT 
            p.id_potrzeba,
            p.nazwa_potrzeba, 
            p.opis,
            w.imie, 
            w.nazwisko, 
            w.numer_telefonu,
            pr.potwierdzenie_potrzebujacego
        FROM POTRZEBA p
        JOIN PRZYPISANIE pr ON p.id_potrzeba = pr.id_potrzeba
        JOIN WOLONTARIUSZE w ON pr.id_wolontariusza = w.id_wolontariusza
        WHERE p.id_potrzebujacego = %s AND pr.status != 'zrealizowane';
    """, (str(user_id),))
    active_needs = cur.fetchall()

    # 2. Potrzeby oczekujące (bez przypisanego wolontariusza)
    cur.execute("""
        SELECT id_potrzeba, nazwa_potrzeba, opis 
        FROM POTRZEBA 
        WHERE id_potrzebujacego = %s 
          AND id_potrzeba NOT IN (SELECT id_potrzeba FROM PRZYPISANIE);
    """, (str(user_id),))
    pending_needs = cur.fetchall()

    # Budujemy kafelki aktywnych potrzeb
    def confirm_need(e, need_id):
        conf_conn = db.get_db_connection()
        conf_cur = conf_conn.cursor()
        try:
            conf_cur.execute("UPDATE PRZYPISANIE SET potwierdzenie_potrzebujacego = TRUE WHERE id_potrzeba = %s", (need_id,))
            
            # Sprawdzenie czy obie strony potwierdzily
            conf_cur.execute("SELECT potwierdzenie_potrzebujacego, potwierdzenie_wolontariusza, id_wolontariusza FROM PRZYPISANIE WHERE id_potrzeba = %s", (need_id,))
            res = conf_cur.fetchone()
            if res['potwierdzenie_potrzebujacego'] and res['potwierdzenie_wolontariusza']:
                conf_cur.execute("UPDATE PRZYPISANIE SET status = 'zrealizowane' WHERE id_potrzeba = %s", (need_id,))
                conf_cur.execute("UPDATE WOLONTARIUSZE SET pkt = COALESCE(pkt, 0) + 1 WHERE id_wolontariusza = %s", (res['id_wolontariusza'],))
                
            conf_conn.commit()
            snack = ft.SnackBar(ft.Text("Zatwierdzono realizację!", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            view_need_list(page, user_id, menu_return)
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            conf_cur.close()
            conf_conn.close()

    active_cards = []
    for need in active_needs:
        controls_list = [
            ft.Text(need['nazwa_potrzeba'], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        ]
        if need.get('opis'):
            controls_list.append(ft.Text(need['opis'], size=15, color="#b3ffffff", italic=True))
            
        controls_list.extend([
            ft.Divider(color=ft.Colors.WHITE),
            ft.Column(
                controls=[
                    ft.Text("WOLONTARIUSZ", size=14, color=ft.Colors.WHITE),
                    ft.Text(f"{need['imie']} {need['nazwisko']}", size=15, color=ft.Colors.WHITE),
                ],
                spacing=2,
            ),
            ft.Divider(color=ft.Colors.WHITE),
            ft.Column(
                controls=[
                    ft.Text("NUMER TELEFONU", size=14, color=ft.Colors.WHITE),
                    ft.Text(need['numer_telefonu'], size=15, color=ft.Colors.WHITE),
                ],
                spacing=2,
            ),
        ])
        
        # Jesli juz kliknal, pokazujemy ze oczekuje na wolontariusza lub po prostu na szaro
        is_confirmed = need.get('potwierdzenie_potrzebujacego', False)
        
        icon_color = ft.Colors.GREEN if is_confirmed else None
        icon_widget = ft.Container(
            content=ft.Image(
                src="src/assets/check.png",
                width=40,
                height=40,
                fit=ft.BoxFit.CONTAIN,
                color=icon_color
            ),
            on_click=None if is_confirmed else lambda e, nid=need['id_potrzeba']: confirm_need(e, nid)
        )
        
        active_cards.append(
            ft.Container(
                bgcolor="#8b0333",
                border_radius=8,
                padding=15,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(controls=controls_list, expand=True),
                        icon_widget,
                    ],
                ),
            )
        )

    def delete_need(e, need_id):
        del_conn = db.get_db_connection()
        del_cur = del_conn.cursor()
        try:
            del_cur.execute("DELETE FROM POTRZEBA WHERE id_potrzeba = %s", (need_id,))
            del_conn.commit()
            snack = ft.SnackBar(ft.Text("Potrzeba usunięta pomyślnie!", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd przy usuwaniu: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
        finally:
            del_cur.close()
            del_conn.close()
        
        # Odświeżenie widoku
        view_need_list(page, user_id, menu_return)

    # Budujemy kafelki oczekujących potrzeb
    pending_cards = []
    for need in pending_needs:
        col_controls = [
            ft.Text(need['nazwa_potrzeba'], size=18, color=ft.Colors.WHITE)
        ]
        if need.get('opis'):
            col_controls.append(ft.Text(need['opis'], size=14, color="#b3ffffff", italic=True))
            
        pending_cards.append(
            ft.Container(
                bgcolor="#132434",
                border_radius=8,
                padding=15,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(controls=col_controls, expand=True),
                        ft.Container(
                            content=ft.Image(src="src/assets/bin.png", width=35, height=35, fit=ft.BoxFit.CONTAIN),
                            on_click=lambda e, nid=need['id_potrzeba']: delete_need(e, nid)
                        )
                    ],
                ),
            )
        )

    # Główny widok – kolumna bez nawiasów kwadratowych w zmiennej content
    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text("MOJE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            
            ft.Text("W TRAKCIE REALIZACJI", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
            *active_cards,  # Rozpakowanie listy kafelków
            
            ft.Text("OCZEKUJĄCE", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
            *pending_cards, # Rozpakowanie listy kafelków
        ],
    )

    page.add(content)

def view_profile(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    import database as db
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM potrzebujacy WHERE id_potrzebujacego = %s;", (str(user_id),))
    user = cur.fetchone()
    cur.close()
    conn.close()

    def create_textfield(value="", read_only=False):
        return ft.TextField(
            value=value,
            read_only=read_only,
            bgcolor=ft.Colors.WHITE if not read_only else ft.Colors.GREY_200,
            border_color="#132434",
            border_radius=10,
            height=50,
            text_style=ft.TextStyle(size=16, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            content_padding=15
        )

    address_field = create_textfield(value=user['adres_potrzebujacego'])
    number_field = create_textfield(value=user['numer_telefonu'], read_only=True)
    
    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, size=16, weight=ft.FontWeight.BOLD, color="#132434"),
                field_obj
            ],
            spacing=5
        )
        
    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("MOJE KONTO", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=10),
                
                create_input_col("IMIĘ", create_textfield(value=user['imie'], read_only=True)),
                create_input_col("NAZWISKO", create_textfield(value=user['nazwisko'], read_only=True)),
                
                create_input_col("ADRES", address_field),
                create_input_col("NUMER TELEFONU", number_field),
                
                ft.Container(height=15),
                
                ft.FilledButton(
                    content=ft.Text("ZAPISZ ZMIANY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: save_data_changes(page, user_id, address_field.value, number_field.value),
                    style=ft.ButtonStyle(bgcolor="#4CAF50", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
                ft.FilledButton(
                    content=ft.Text("ZMIEŃ HASŁO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: change_password(page, user_id, menu_return),
                    style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
                ft.FilledButton(
                    content=ft.Text("USUŃ KONTO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: delete_account(page, user_id, "potrzebujacy", menu_return),
                    style=ft.ButtonStyle(bgcolor="#8b0333", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def save_data_changes(page, user_id, address, number):
    try:
        import database as db
        conn = db.get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE potrzebujacy SET adres_potrzebujacego = %(address)s WHERE id_potrzebujacego = %(user_id)s;", 
            {"address": str(address), "user_id": str(user_id)}
        )
        
        conn.commit()
        snack = ft.SnackBar(ft.Text("Zapisano zmiany!", size=16), bgcolor=ft.Colors.GREEN)
        page.overlay.append(snack)
        snack.open = True
        page.update()
    except Exception as e:
        snack = ft.SnackBar(ft.Text(f"Błąd zapisu: {e}", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def change_password(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: view_profile(page, user_id, menu_return), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    def create_passfield(hint):
        return ft.TextField(
            hint_text=hint,
            password=True,
            can_reveal_password=True,
            bgcolor=ft.Colors.WHITE,
            border_color="#132434",
            border_radius=10,
            height=50,
            text_style=ft.TextStyle(size=16, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            content_padding=15
        )

    passwordbox_old = create_passfield("Stare hasło")
    passwordbox_new = create_passfield("Nowe hasło")
    passwordbox_confirm = create_passfield("Powtórz nowe hasło")
    
    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, size=16, weight=ft.FontWeight.BOLD, color="#132434"),
                field_obj
            ],
            spacing=5
        )
        
    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("ZMIEŃ HASŁO", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=10),
                create_input_col("STARE HASŁO", passwordbox_old),
                create_input_col("NOWE HASŁO", passwordbox_new),
                create_input_col("POWTÓRZ NOWE HASŁO", passwordbox_confirm),
                ft.Container(height=15),
                ft.FilledButton(
                    content=ft.Text("ZAPISZ ZMIANY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: save_password_changes(page, user_id, passwordbox_old.value, passwordbox_new.value, passwordbox_confirm.value, menu_return),
                    style=ft.ButtonStyle(bgcolor="#4CAF50", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def save_password_changes(page: ft.Page, user_id, old_password: str, new_password: str, confirm_password: str, menu_return):
    import database as db
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT numer_telefonu FROM potrzebujacy WHERE id_potrzebujacego = %s;", (str(user_id),))
    user_rec = cur.fetchone()
    if not user_rec:
        return
    phone = user_rec['numer_telefonu']
    
    cur.execute("SELECT haslo FROM hasla_potrzebujacych WHERE nr_tel = %s;", (phone,))
    pwd_rec = cur.fetchone()
    
    if not pwd_rec or pwd_rec['haslo'] != old_password:
        snack = ft.SnackBar(ft.Text("Nieprawidłowe stare hasło", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        return
        
    if new_password != confirm_password:
        snack = ft.SnackBar(ft.Text("Nowe hasła nie są zgodne", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        return
        
    cur.execute("UPDATE hasla_potrzebujacych SET haslo = %s WHERE nr_tel = %s;", (new_password, phone))
    conn.commit()
    cur.close()
    conn.close()
    
    snack = ft.SnackBar(ft.Text("Hasło zostało zmienione", size=16), bgcolor=ft.Colors.GREEN)
    page.overlay.append(snack)
    snack.open = True
    view_profile(page, user_id, menu_return)

def delete_account(page, user_id, role, menu_return):
    def confirm_delete(e):
        dialog.open = False
        page.update()
        import database as db
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            tabela = 'wolontariusze' if role == 'wolontariusz' else 'potrzebujacy'
            kolumna = 'id_wolontariusza' if role == 'wolontariusz' else 'id_potrzebujacego'
            
            cur.execute(f"DELETE FROM {tabela} WHERE {kolumna} = %s;", (str(user_id),))
            conn.commit()
            snack = ft.SnackBar(ft.Text("Konto usunięte. Wylogowywanie...", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            menu_return()
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            cur.close()
            conn.close()

    def cancel_delete(e):
        dialog.open = False
        page.update()

    import flet as ft
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Usuwanie konta", size=22, weight=ft.FontWeight.BOLD),
        content=ft.Text("Czy na pewno chcesz bezpowrotnie usunąć swoje konto? Tej operacji nie można cofnąć.", size=16),
        actions=[
            ft.TextButton("ANULUJ", on_click=cancel_delete),
            ft.TextButton("USUŃ", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
