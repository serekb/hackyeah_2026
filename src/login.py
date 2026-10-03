import flet as ft
import database as db

def login_successful(page, menu_return, user_type, user_id):
    if user_type == "Potrzebujący":
        import needy as nd
        nd.select_needy(page, menu_return, user_id)
    elif user_type == "Wolontariusz":
        import volunteer as vl
        vl.select_volunteer(page, menu_return, user_id)
    else:
        pass #jakis wyjatek idk

def login_failed(page, menu_return, user_type, login_fail = "ok"):
    run_login(page, menu_return, user_type, login_fail)

def register_user(user_type):
    pass

def verify_login(page, menu_return, user_type, number, password):
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM HASLA WHERE nr_tel = %s;", (str(number),))
    print(type(number))
    user = cur.fetchone()
    print(user)
    if not user:
        login_failed(page, menu_return, user_type, "login_error")
    elif user['haslo'] != password:
        login_failed(page, menu_return, user_type, "password_error")
    else:
        login_successful(page, menu_return, user_type, user['id'])


def run_login(page: ft.Page, menu_return, user_type, login_fail = "ok"):
    page.clean()

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200
    )

    if user_type not in ["Potrzebujący", "Wolontariusz"]:
        page.add(ft.Text("Nieprawidłowy typ użytkownika", size=20, color=ft.Colors.RED))
        return

    if user_type == "Potrzebujący":
        img_src = "src/assets/needy.png"
    else:
        img_src = "src/assets/volunteer.png"

    if login_fail == "login_error":
        message = "Nieprawidłowy email"
    elif login_fail == "password_error":
        message = "Nieprawidłowe hasło"
    else:
        message = ""

    number_field = ft.TextField(label="Numer telefonu")
    password_field = ft.TextField(label="Hasło", password=True, can_reveal_password=True)
    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src=img_src, width=50, height=50, fit=ft.BoxFit.CONTAIN),
                ft.Text(f"Próbujesz zalogować się jako {user_type}", size=20, color=ft.Colors.BLACK),
                number_field,
                ft.Text(message, size=15, color=ft.Colors.RED) if message else ft.Container(),
                password_field,
                ft.FilledButton("Zaloguj się", on_click=lambda e: verify_login(page, menu_return, user_type, number_field.value, password_field.value),
                                style=ft.ButtonStyle(bgcolor="#8b0333")),
                ft.Row(
                    controls=[
                        ft.Text("Nie masz konta?", color=ft.Colors.BLACK),
                        ft.FilledButton("Zarejestruj się", on_click=lambda e: register_user(user_type),
                                        style=ft.ButtonStyle(bgcolor="#132434"),),
                    ]
                )
            ]
        ),
        padding=10,
        border=ft.Border.all(1, ft.Colors.BLACK),
        bgcolor = ft.Colors.LIGHT_BLUE_100,
        border_radius=10,
    )
    '''
        jakbyśmy nie chccieli dynamicznej
        height=0.5*page.window.height,
        width=page.window.width,
    '''
    page.add(
        content
    )