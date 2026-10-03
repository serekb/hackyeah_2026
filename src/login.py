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


def register_user(page: ft.Page, menu_return, user_type):
    page.clean()

    # Zezwalamy na przewijanie całej strony
    page.scroll = "auto"

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: run_login(page, menu_return, user_type), width=150, height=40),
            padding=10  
        ),
        leading_width=200
    )

    label_style = ft.TextStyle(weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900, size=12)
    field_bgcolor = ft.Colors.WHITE
    text_color = "#8b0333"

    # Zaktualizowana funkcja generująca pola tekstowe - teraz przyjmuje argument 'hint'
    def create_textfield(hint="", is_password=False):
        return ft.TextField(
            hint_text=hint,                                                # <--- Tutaj podpinamy wyszarzony tekst
            hint_style=ft.TextStyle(color=ft.Colors.GREY_400, size=13),    # <--- Nadajemy mu jasnoszary kolor
            password=is_password, 
            can_reveal_password=is_password, 
            bgcolor=field_bgcolor, 
            color=text_color, 
            border_color=ft.Colors.TRANSPARENT, 
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=14),
            height=40,              
            content_padding=10      
        )

    # Inicjalizacja pól z przykładowymi danymi bazującymi na Twoim zdjęciu
    phone_field = create_textfield(hint="np. 567865432")
    password_field = create_textfield(hint="min. 8 znaków", is_password=True)
    name_field = create_textfield(hint="np. Kasia")
    surname_field = create_textfield(hint="np. Wesoła")
    address_field = create_textfield(hint="np. ul. Leśna 56")

    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, style=label_style),
                field_obj
            ],
            spacing=0 
        )

    def handle_registration(e):
        print("=== DANE Z FORMULARZA ===")
        print(f"Telefon: {phone_field.value}")
        print(f"Hasło: {password_field.value}")
        print(f"Imię: {name_field.value}")
        print(f"Nazwisko: {surname_field.value}")
        print(f"Adres: {address_field.value}")
        print("Zapis do bazy tymczasowo wyłączony.")
        run_login(page, menu_return, user_type)

    form_content = ft.Container(
        content=ft.Column(
            controls=[
                create_input_col("NUMER TELEFONU", phone_field),
                create_input_col("HASŁO", password_field),
                create_input_col("IMIĘ", name_field),
                create_input_col("NAZWISKO", surname_field),
                create_input_col("ADRES", address_field),
                
                ft.Container(height=5), 
                ft.Text("ZAŚWIADCZENIE Z ORGANIZACJI", style=label_style),
                ft.FilledButton(
                    "DODAJ ZAŚWIADCZENIE",
                    icon="add_circle",
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLUE_GREY_900,
                        bgcolor=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    width=300,
                    height=45, 
                )
            ],
            spacing=5 
        ),
        padding=15, 
        border=ft.Border.all(2, ft.Colors.BLUE_GREY_900),
        bgcolor="#E8EEF2",
        border_radius=15,
    )

    content = ft.Column(
        controls=[
            ft.Container(
                content=ft.Text("REJESTRACJA", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                padding=5
            ),
            form_content,
            ft.Container(height=10), 
            
            ft.FilledButton(
                "ZAREJESTRUJ SIĘ", 
                on_click=handle_registration,
                style=ft.ButtonStyle(
                    bgcolor=text_color,
                    shape=ft.RoundedRectangleBorder(radius=10)
                ),
                width=300, 
                height=50 
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=350,
        scroll="auto" 
    )

    page.add(
        ft.Row(
            controls=[content],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

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
                ft.FilledButton("Zarejestruj się", on_click=lambda e: register_user(page, menu_return, user_type),
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