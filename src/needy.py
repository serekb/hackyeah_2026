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
            ft.FilledButton("MOJE KONTO", on_click=lambda e: view_profile(user_id), 
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
    
    active_needs = []
    pending_needs = []
    
    conn = db.get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.id_potrzeba, p.nazwa_potrzeba, w.imie, w.nazwisko, w.numer_telefonu
                FROM potrzeba p
                LEFT JOIN przypisanie pr ON p.id_potrzeba = pr.id_potrzeba
                LEFT JOIN wolontariusze w ON pr.id_wolontariusza = w.id_wolontariusza
                WHERE p.id_potrzebujacego = %s
            """, (user_id,))
            records = cur.fetchall()
            for record in records:
                if record['imie'] is not None:
                    active_needs.append(record)
                else:
                    pending_needs.append(record)
            cur.close()
        finally:
            conn.close()

    content = [
        ft.Column(
            controls = [
                ft.Text("MOJE POTRZEBY", size=20, color=ft.Colors.BLACK),
                ft.Column(
                    controls = [
                        ft.Container(
                            content = ft.Row(
                                controls = [
                                    ft.Column(
                                        controls = [
                                            ft.Text(need['nazwa_potrzeba'], size=20, color=ft.Colors.WHITE),
                                            ft.Divider(),
                                            ft.Column(
                                                controls = [
                                                    ft.Text("WOLONTARIUSZ", size=20, color=ft.Colors.WHITE),
                                                    ft.Text(f"{need['imie']} {need['nazwisko']}", size=15, color=ft.Colors.WHITE),
                                                ]
                                            ),
                                            ft.Divider(),
                                            ft.Column(
                                                controls = [
                                                    ft.Text("NUMER TELEFONU", size=20, color=ft.Colors.WHITE),
                                                    ft.Text(str(need['numer_telefonu']), size=15, color=ft.Colors.WHITE),
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.Image(src="src/assets/check.png", width=50, height=50, fit=ft.BoxFit.CONTAIN)
                                ],
                            ),
                            bgcolor="#8b0333",
                            padding=10,
                            border_radius=10
                        ) for need in active_needs
                    ]
                ),
                ft.Column(
                    controls = [
                        ft.Container(
                            content = ft.Row(
                                controls = [
                                    ft.Text(need['nazwa_potrzeba'], size=20, color=ft.Colors.WHITE),
                                    ft.Image(src="src/assets/bin.png", width=50, height=50, fit=ft.BoxFit.CONTAIN)
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            bgcolor="#132434",
                            padding=10,
                            border_radius=10
                        ) for need in pending_needs
                    ]   
                )
            ]
        )
    ]
    page.add(*content)