import flet as ft
import database as db

class Need:
    def __init__(self, category, description, volunteer=None, needy = None, completed=False):
        self.category = category
        self.description = description
        self.volunteer = volunteer
        self.needy = needy
        self.completed = completed

def select_needy(page: ft.Page, menu_return, user_id):
    page.clean()

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200
    )

    content = ft.Column(
        controls = [
            ft.FilledButton("DODAJ POTRZEBĘ", on_click=lambda e: add_need(page, user_id, menu_return), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("MOJE POTRZEBY", on_click=lambda e: view_need_list(page, user_id, menu_return),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("MOJE KONTO", on_click=lambda e: view_profile(page, user_id, menu_return), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50)
        ]
    )

    page.add(
        content
    )

def add_need(page: ft.Page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT nazwa_potrzeba FROM potrzeba")
    categories = cur.fetchall()
    
    category_list = [category['nazwa_potrzeba'] for category in categories]
    
    selected_category = [None]
    error_text = ft.Text("", color=ft.Colors.RED, size=16)
    
    category_buttons = []
    
    def select_category(cat_name):
        selected_category[0] = cat_name
        for btn in category_buttons:
            if btn.content == cat_name:
                btn.style = ft.ButtonStyle(bgcolor="#4CAF50") # Highlighted color
            else:
                btn.style = ft.ButtonStyle(bgcolor="#132434") # Default color
        error_text.value = ""
        page.update()
        
    for category_name in category_list:
        btn = ft.FilledButton(
            category_name,
            on_click=lambda e, cat=category_name: select_category(cat),
            style=ft.ButtonStyle(bgcolor="#132434"),
            width=200,
            height=50,
        )
        category_buttons.append(btn)
        
    description_field = ft.TextField(label="Wpisz krótki opis potrzeby (opcjonalnie)", multiline=True, width=400, height=100)

    def submit_need():
        if not selected_category[0]:
            error_text.value = "Błąd: Musisz wybrać kategorię!"
            page.update()
            return
            
        try:
            ins_conn = db.get_db_connection()
            ins_cur = ins_conn.cursor()
            ins_cur.execute(
                "INSERT INTO potrzeba (nazwa_potrzeba, opis, id_potrzebujacego) VALUES (%s, %s, %s)",
                (selected_category[0], description_field.value, user_id)
            )
            ins_conn.commit()
            ins_cur.close()
            ins_conn.close()
            
            snack = ft.SnackBar(ft.Text("Potrzeba została pomyślnie dodana!"))
            page.overlay.append(snack)
            snack.open = True
            
            # Wróć do menu głównego potrzebującego po pomyślnym dodaniu
            select_needy(page, menu_return, user_id)
        except Exception as e:
            error_text.value = f"Błąd bazy danych: {e}"
            page.update()

    content = ft.Column(
        controls=[
            ft.Text("WYBIERZ KATEGORIĘ", size=20, color=ft.Colors.BLACK),
            *category_buttons,
            error_text,
            ft.Text("KRÓTKI OPIS", size=20, color=ft.Colors.BLACK),
            description_field,
            ft.FilledButton("DODAJ", on_click=lambda e: submit_need(), style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
        ]
    )
    page.add(content)

def view_need_list(page: ft.Page, user_id, menu_return):
    page.clean()
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
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
            w.imie, 
            w.nazwisko, 
            w.numer_telefonu 
        FROM POTRZEBA p
        JOIN PRZYPISANIE pr ON p.id_potrzeba = pr.id_potrzeba
        JOIN WOLONTARIUSZE w ON pr.id_wolontariusza = w.id_wolontariusza
        WHERE p.id_potrzebujacego = %s;
    """, (str(user_id),))
    active_needs = cur.fetchall()

    # 2. Potrzeby oczekujące (bez przypisanego wolontariusza)
    cur.execute("""
        SELECT id_potrzeba, nazwa_potrzeba 
        FROM POTRZEBA 
        WHERE id_potrzebujacego = %s 
          AND id_potrzeba NOT IN (SELECT id_potrzeba FROM PRZYPISANIE);
    """, (str(user_id),))
    pending_needs = cur.fetchall()

    # Budujemy kafelki aktywnych potrzeb
    active_cards = [
        ft.Container(
            bgcolor="#8b0333",
            border_radius=8,
            padding=15,
            content=ft.Row(  # Pojedynczy obiekt, bez []
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(need['nazwa_potrzeba'], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
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
                        ],
                        expand=True,
                    ),
                    ft.Image(src="src/assets/check.png", width=40, height=40, fit=ft.BoxFit.CONTAIN),
                ],
            ),
        )
        for need in active_needs
    ]

    # Budujemy kafelki oczekujących potrzeb
    pending_cards = [
        ft.Container(
            bgcolor="#132434",
            border_radius=8,
            padding=15,
            content=ft.Row(  # Pojedynczy obiekt, bez []
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(need['nazwa_potrzeba'], size=18, color=ft.Colors.WHITE),
                    ft.Image(src="src/assets/bin.png", width=35, height=35, fit=ft.BoxFit.CONTAIN),
                ],
            ),
        )
        for need in pending_needs
    ]

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
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: select_needy(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM potrzebujacy WHERE id_potrzebujacego = %s;", (str(user_id),))
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
                        ft.TextField(value=user['adres_potrzebujacego']),
                        ft.Text(f"Numer telefonu", size=15, color=ft.Colors.BLACK),
                        ft.TextField(value=user['nr_tel'])
                    ]
                )
            ),
            ft.FilledButton("ZMIEŃ HASŁO", on_click=lambda e: change_password(page, user['id_potrzebujacego']),
                             style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("USUŃ KONTO", on_click=lambda e: delete_account(page, user['id_potrzebujacego'], "potrzebujacy"),
                                         style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),         
        ]
    )
    page.add(content)

def change_password(page: ft.Page, user_id):
    page.clean()
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM potrzebujacy WHERE id_potrzebujacego = %s;", (str(user_id),))
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
    cur.execute("SELECT haslo FROM hasla WHERE id_potrzebujacego = %s;", (str(user_id),))
    user = cur.fetchone()
    if user['haslo'] != old_password:
        page.add(ft.Text("Nieprawidłowe stare hasło", size=15, color=ft.Colors.RED))
        return
    if new_password != confirm_password:
        page.add(ft.Text("Nowe hasła nie są zgodne", size=15, color=ft.Colors.RED))
        return
    cur.execute("UPDATE hasla SET haslo = %s WHERE id_potrzebujacego = %s;", (new_password, str(user_id)))
    conn.commit()
    page.add(ft.Text("Hasło zostało zmienione", size=15, color=ft.Colors.GREEN))

def delete_account(page, user_id, role):
    conn = db.get_db_connection()
    cur = conn.cursor()
    tabela = 'wolontariusze' if role == 'wolontariusz' else 'potrzebujacy'
    kolumna = 'id_wolontariusza' if role == 'wolontariusz' else 'id_potrzebujacego'
    cur.execute(f"DELETE FROM {tabela} WHERE {kolumna} = %s;", (str(user_id),))
    conn.commit()
    conn.close()
