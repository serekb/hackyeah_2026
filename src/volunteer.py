import flet as ft
import database as db

def view_accepted_needs(page: ft.Page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
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

def new_needs(page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
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

def select_volunteer(page: ft.Page, menu_return, user_id):
    page.clean()

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )

    content = ft.Column(
        controls = [
            ft.FilledButton("PRZYJĘTE POTRZEBY", on_click=lambda e: view_accepted_needs(page, user_id, menu_return),
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("NOWE POTRZEBY", on_click=lambda e: new_needs(page, user_id, menu_return),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("POSTĘPY", on_click=lambda e: accomplishments(page, user_id), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("MOJE KONTO", on_click=lambda e: view_profile(page, user_id),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
        ]
    )

    page.add(
        content
    )

def view_profile(page: ft.Page, user_id):
    page.clean()
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    user = cur.fetchone()
    content = ft.Column(
        controls = [
            ft.Text("MOJE KONTO", size=20, color=ft.Colors.BLACK),
            ft.Container(
                content = ft.Column(
                    controls = [
                        ft.Text(f"Imię", size=15, color=ft.Colors.BLACK),
                        ft.TextField(value=user['imie'], read_only=True),
                        ft.Text(f"Nazwisko", size=15, color=ft.Colors.BLACK),
                        ft.TextField(value=user['nazwisko'], read_only=True),
                        ft.Text(f"Adres", size=15, color=ft.Colors.BLACK),
                        ft.Row(
                            controls = [
                                ft.TextField(value=user['adres_wolontariusza']),
                                ft.Image(src = "src/assets/edit.png")
                            ]
                        ),
                        ft.Text(f"Numer telefonu", size=15, color=ft.Colors.BLACK),
                        ft.Row(
                            controls = [
                                ft.TextField(value=user['nr_tel']),
                                ft.Image(src = "src/assets/edit.png")
                            ]
                        ),
                        ft.Text(f"Organizacja", size=15, color=ft.Colors.BLACK),
                        ft.Row(
                            controls = [
                                ft.TextField(value=user['organizacja']),
                                ft.Image(src = "src/assets/edit.png")
                            ]
                        ),
                    ]
                )
            ),
            ft.FilledButton("ZMIEŃ HASŁO", on_click=lambda e: change_password(page, user['id_wolontariusza']),
                             style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("USUŃ KONTO", on_click=lambda e: delete_account(page, user['id_wolontariusza']),
                                         style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),         
        ]
    )
    page.add(content)

def change_password(page: ft.Page, user_id):
    page.clean()
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    user = cur.fetchone()
    passwordbox_old = ft.TextField(label="Stare hasło", password=True, can_reveal_password=True)
    passwordbox_new = ft.TextField(label="Nowe hasło", password=True, can_reveal_password=True)
    passwordbox_confirm = ft.TextField(label="Powtórz nowe hasło", password=True, can_reveal_password=True)
    content = ft.Column(
        controls = [
            ft.Text("Wpisz stare hasło", size=15, color=ft.Colors.BLACK),
            passwordbox_old,
            ft.Text("Wpisz nowe hasło", size=15, color=ft.Colors.BLACK),
            passwordbox_new,
            ft.Text("Powtórz nowe hasło", size=15, color=ft.Colors.BLACK),
            passwordbox_confirm,
            ft.FilledButton("ZAPISZ ZMIANY", on_click=lambda e: save_changes(page, user_id, passwordbox_old.value, passwordbox_new.value, passwordbox_confirm.value),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
        ]
    )
    page.add(content)

def save_changes(page: ft.Page, user_id: int, old_password: str, new_password: str, confirm_password: str):
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT haslo FROM hasla WHERE id_wolontariusza = %s;", (str(user_id),))
    user = cur.fetchone()
    if user['haslo'] != old_password:
        page.add(ft.Text("Nieprawidłowe stare hasło", size=15, color=ft.Colors.RED))
        return
    if new_password != confirm_password:
        page.add(ft.Text("Nowe hasła nie są zgodne", size=15, color=ft.Colors.RED))
        return
    cur.execute("UPDATE hasla SET haslo = %s WHERE id_wolontariusza = %s;", (new_password, str(user_id)))
    conn.commit()
    conn.close()
    page.add(ft.Text("Hasło zostało zmienione", size=15, color=ft.Colors.GREEN))

def delete_account(page, user_id):
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT haslo FROM hasla WHERE id_wolontariusza = %s;", (str(user_id),)) #usuwanie uzytkownika o id = user_id
    user = cur.fetchone()