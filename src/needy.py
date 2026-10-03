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
            ft.FilledButton("DODAJ POTRZEBĘ", on_click=lambda e: add_need(page, user_id), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("MOJE POTRZEBY", on_click=lambda e: view_need_list(user_id),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("MOJE KONTO", on_click=lambda e: view_profile(user_id), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50)
        ]
    )

    page.add(
        content
    )

def add_need(page: ft.Page, user_id):
    page.clean()
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nazwa_potrzeba FROM potrzeba")
    categories = cur.fetchall()
    
    category_list = [category['nazwa_potrzeba'] for category in categories]

    content = ft.Column(
        controls=[
            ft.Text("WYBIERZ KATEGORIĘ", size=20, color=ft.Colors.BLACK),
            *[
                ft.FilledButton(
                    category_name,
                    on_click=lambda e, cat=category_name: select_category(cat),
                    style=ft.ButtonStyle(bgcolor="#132434"),
                    width=200,
                    height=50,
                )
                for category_name in category_list
            ],
            
            ft.Text("KRÓTKI OPIS", size=20, color=ft.Colors.BLACK),
            ft.TextField(label="Wpisz krótki opis potrzeby", multiline=True, width=400, height=100),
            ft.FilledButton("DODAJ", on_click=lambda e: submit_need(), style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
        ]
    )
    page.add(content)

def view_need_list(page: ft.Page, user):
    page.clean()
    active_needs = []
    pending_needs = []
    for need in user.needs:
        if need.completed:
            pending_needs.append(need)
        else:
            active_needs.append(need)
    content = [
        ft.Column(
            controls = [
                ft.Text("MOJE POTRZEBY", size=20, color=ft.Colors.BLACK),
                ft.Column(
                    controls = [
                        [ft.Container(
                            content = [
                                ft.Row(
                                    controls = [
                                        ft.Column(
                                            controls = [
                                                ft.Text(need.category, size=20, color=ft.Colors.WHITE),
                                                ft.Divider(),
                                                ft.Column(
                                                    controls = [
                                                        ft.Text("WOLONTARIUSZ", size=20, color=ft.Colors.WHITE),
                                                        ft.Text(need.volunteer, size=15, color=ft.Colors.WHITE),
                                                    ]
                                                ),
                                                ft.Divider(),
                                                ft.Column(
                                                    controls = [
                                                        ft.Text("NUMER TELEFONU", size=20, color=ft.Colors.WHITE),
                                                        ft.Text(need.volunteer.number, size=15, color=ft.Colors.WHITE),
                                                    ]
                                                )
                                            ]
                                        ),
                                        ft.Image(src="src/assets/check.png", width=50, height=50, fit=ft.BoxFit.CONTAIN)
                                    ],
                                )                                      
                            ],
                            bgcolor="#8b0333") for need in active_needs]
                    ]
                ),
                ft.Column(
                    controls = [
                        [ft.Container(
                            content = [
                                ft.Row(
                                    controls = [
                                        ft.Text(need.category, size=20, color=ft.Colors.WHITE),
                                        ft.Image(src="src/assets/bin.png", width=50, height=50, fit=ft.BoxFit.CONTAIN)
                                    ],
                                )                                      
                            ],
                            bgcolor="#132434") for need in pending_needs]
                    ]   
                )
            ]
        )
    ]
    page.add(content)