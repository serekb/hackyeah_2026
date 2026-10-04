import flet as ft
import database as db
import login as lg

def view_accepted_needs(page: ft.Page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_potrzeba FROM PRZYPISANIE WHERE id_wolontariusza = %s;", (str(user_id),))
    needs = cur.fetchall()
    
    need_categories = []
    need_ids = [n['id_potrzeba'] for n in needs]
    needy_ids = []
    needy_numbers = []
    needy_names = []
    needy_surnames = []

    for need_id in need_ids:
        cur.execute("SELECT * FROM POTRZEBA WHERE id_potrzeba = %s;", (str(need_id),))
        n = cur.fetchone()
        need_categories.append(n['nazwa_potrzeba'])
        needy_ids.append(n['id_potrzebujacego'])

    for n_id in needy_ids:
        cur.execute("SELECT numer_telefonu, imie, nazwisko FROM POTRZEBUJACY WHERE id_potrzebujacego = %s;", (str(n_id),))
        needy = cur.fetchone()
        needy_numbers.append(needy['numer_telefonu'])
        needy_names.append(needy['imie'])
        needy_surnames.append(needy['nazwisko'])

    cur.execute("SELECT numer_telefonu FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    vol = cur.fetchone()
    volunteer_number = vol['numer_telefonu'] if vol else ""

    needs_data = list(zip(need_categories, needy_numbers, needy_names, needy_surnames))

    page.clean()

    # Generujemy listę kafelków dla każdej potrzeby
    cards = []
    for item in needs_data:
        cat_name, needy_phone, first_name, last_name = item
        cards.append(
            ft.Container(
                bgcolor="#8b0333",
                border_radius=10,
                padding=15,
                content=ft.Row(  # Tutaj pojedyncza kontrolka, bez kwadratowych nawiasów!
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(cat_name, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ft.Divider(color=ft.Colors.WHITE),
                                ft.Column(
                                    controls=[
                                        ft.Text("KOMU POMAGAM?", size=14, color=ft.Colors.WHITE),
                                        ft.Text(f"{first_name} {last_name}", size=16, color=ft.Colors.WHITE),
                                    ],
                                    spacing=2,
                                ),
                                ft.Divider(color=ft.Colors.WHITE),
                                ft.Column(
                                    controls=[
                                        ft.Text("NUMER TELEFONU POTRZEBUJĄCEGO", size=14, color=ft.Colors.WHITE),
                                        ft.Text(needy_phone, size=16, color=ft.Colors.WHITE),
                                    ],
                                    spacing=2,
                                ),
                                ft.Divider(color=ft.Colors.WHITE),
                                ft.Column(
                                    controls=[
                                        ft.Text("UWAGI", size=14, color=ft.Colors.WHITE),
                                        ft.TextField("W TRAKCIE REALIZACJI", color=ft.Colors.WHITE),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            expand=True,
                        ),
                        ft.Image(
                            src="src/assets/check.png",
                            width=40,
                            height=40,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                    ],
                ),
            )
        )

    view = ft.Column(
        scroll=ft.ScrollMode.AUTO, 
        expand=True,
        controls=[
            ft.Text("PRZYJĘTE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            *cards, 
        ],
    )

    page.add(view)
    cur.close()
    conn.close()

def new_needs(page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM POTRZEBA WHERE id_potrzebujacego NOT IN (SELECT id_potrzebujacego FROM PRZYPISANIE WHERE id_wolontariusza = %s);", (str(user_id),))
    needs = cur.fetchall()

    cur.execute("SELECT imie, nazwisko, id_potrzebujacego from potrzebujacy where id_potrzebujacego IN (SELECT id_potrzebujacego FROM POTRZEBA WHERE id_potrzebujacego NOT IN (SELECT id_potrzebujacego FROM PRZYPISANIE WHERE id_wolontariusza = %s));", (str(user_id),))
    needy_infos = cur.fetchall()
    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand = True,
        controls=[
            ft.Container(
                content = ft.Column(
                    controls = [
                        ft.Text("Lokalizacja", size=20, color=ft.Colors.BLACK),
                        ft.Row(
                            controls = [
                                ft.TextField(label="Adres", width=100),
                                ft.TextField(label="10km", width=100)
                            ]
                        ),
                        ft.FilledButton("SZUKAJ", on_click=lambda e: filter_needs(), style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
                    ]
                ),
                border=ft.Border.all(3, ft.Colors.BLACK),
                border_radius=10,
            ),
            *[
                ft.Container(
                    bgcolor="#132434",
                    border_radius=10,
                    padding=15,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(needy_info['imie'] + " " + needy_info['nazwisko'], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Divider(color=ft.Colors.WHITE),
                                    ft.Text(need['nazwa_potrzeba'], size=16, color=ft.Colors.WHITE),
                                    ft.Divider(color=ft.Colors.WHITE),
                                    ft.Text(need['opis'], size=14, color=ft.Colors.WHITE),
                                ],
                                expand=True,
                            ),
                            ft.Image(
                                src="src/assets/right_arrow.png",
                                width=40,
                                height=40,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                        ],
                    ),
                ) for need in needs for needy_info in needy_infos if need['id_potrzebujacego'] == needy_info['id_potrzebujacego']
            ]
        ]
    )
    page.add(content)
    cur.close()
    conn.close()

def select_volunteer(page: ft.Page, menu_return, user_id):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )

    btn_width = 410
    btn_height = 120

    content = ft.Column(
        controls=[
            ft.FilledButton(
                content=ft.Text("PRZYJĘTE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_accepted_needs(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("NOWE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: new_needs(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#8b0333",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("POSTĘPY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: accomplishments(page, user_id), 
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("MOJE KONTO", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_profile(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#8b0333",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Column(
            controls=[content, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def accomplishments(page: ft.Page, user_id):
    page.clean()
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT PKT FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    points = cur.fetchall()
    print(points)
    points = points[0]['pkt']
    print(points)
    if points < 15:
        medal_path = "src/assets/bronze_medal.png"   
    elif points < 50:
        medal_path = "src/assets/silver_medal.png"
    else:
        medal_path = "src/assets/gold_medal.png"

    content = ft.Column(
            controls = [
                ft.Image(src = medal_path),
                ft.Text("Udzielonych pomocy", size = 20, color = ft.Colors.BLACK),
                ft.Text(f"{points}", size = 20, color = ft.Colors.BLACK),
                ft.FilledButton("Pobierz certyfikat", style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
                ft.FilledButton("Przysługujące zniżki", style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ]
        )

    page.add(content)
    cur.close()
    conn.close()

def view_profile(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
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

    address_field = create_textfield(value=user['adres_wolontariusza'])
    number_field = create_textfield(value=user['numer_telefonu'], read_only=True)
    org_field = create_textfield(value=user['organizacja'])
    
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
                create_input_col("ORGANIZACJA", org_field),
                
                ft.Container(height=15),
                
                ft.FilledButton(
                    content=ft.Text("ZAPISZ ZMIANY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: save_data_changes(page, user_id, address_field.value, number_field.value, org_field.value),
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
                    on_click=lambda e: delete_account(page, user_id, "wolontariusz", menu_return),
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

def save_data_changes(page, user_id, address, number, org_field):
    try:
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE WOLONTARIUSZE SET numer_telefonu = %s, adres_wolontariusza = %s, organizacja = %s WHERE id_wolontariusza = %s;", (str(number), str(address), str(org_field), str(user_id),))
        
        # Aktualizacja hasla_wolontariuszy (baza logowania) - trzeba znalezc stary numer
        cur.execute("SELECT nr_tel FROM wolontariusze WHERE id_wolontariusza = %s;", (str(user_id),))
        old_nr = cur.fetchone()['nr_tel'] if 'nr_tel' in [d[0] for d in cur.description] else None
        if old_nr:
            cur.execute("UPDATE hasla_wolontariuszy SET nr_tel = %s WHERE nr_tel = %s;", (str(number), str(old_nr)))
            
        conn.commit()
        cur.close()
        conn.close()
        snack = ft.SnackBar(ft.Text("Zapisano zmiany!", size=16), bgcolor=ft.Colors.GREEN)
        page.overlay.append(snack)
        snack.open = True
        page.update()
    except Exception as e:
        snack = ft.SnackBar(ft.Text(f"Błąd zapisu: {e}", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()

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
    conn = db.get_db_connection()
    cur = conn.cursor()
    # Zabezpieczenie takie samo jak dla potrzebujacego: uzywamy numeru tel do zlokalizowania w hasla_wolontariuszy
    cur.execute("SELECT numer_telefonu FROM wolontariusze WHERE id_wolontariusza = %s;", (str(user_id),))
    user_rec = cur.fetchone()
    if not user_rec:
        return
    phone = user_rec['numer_telefonu']
    
    cur.execute("SELECT haslo FROM hasla_wolontariuszy WHERE nr_tel = %s;", (phone,))
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
        
    cur.execute("UPDATE hasla_wolontariuszy SET haslo = %s WHERE nr_tel = %s;", (new_password, phone))
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