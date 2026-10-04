import flet as ft
import database as db
from geopy.geocoders import Nominatim

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
    address_field = create_textfield(hint="np. Leśna 56 m.5")
    org_field=create_textfield(hint="np. Koło Wolontariuszy")

    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, style=label_style),
                field_obj
            ],
            spacing=0 
        )

    def handle_registration(e):
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            geolocator = Nominatim(user_agent="my_app")
            full_address=f"Kraków,{address_field.value}"
            location = geolocator.geocode(full_address)

            if location:
                lat = location.latitude
                lon = location.longitude
                print(f"Znaleziono współrzędne: {lat}, {lon}")
            else:
                print("Nie znaleziono adresu. Sprawdź, czy nazwa ulicy jest poprawna.")
                # Jeśli adresu nie ma, można potraktować to jako błąd
                snack = ft.SnackBar(ft.Text("Nie znaleziono adresu!"), bgcolor=ft.Colors.RED)
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return
                
            if user_type == "Wolontariusz":
                    cur.execute("INSERT INTO wolontariusze (imie, nazwisko,pkt,numer_telefonu,adres_wolontariusza,organizacja,dlugosc_geograficzna, szerokosc_geograficzna) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)", (str(name_field.value),str(surname_field.value), 0,str(phone_field.value),str(address_field.value), str(org_field.value), str(lon), str(lat)))
                    cur.execute("INSERT INTO hasla_wolontariuszy (nr_tel,haslo) VALUES (%s, %s)", (str(phone_field.value),str(password_field.value)))

            elif user_type == "Potrzebujący":
                    cur.execute("INSERT INTO potrzebujacy (imie, nazwisko,numer_telefonu,adres_potrzebujacego,dlugosc_geograficzna, szerokosc_geograficzna) VALUES (%s, %s, %s, %s,%s, %s)", (str(name_field.value),str(surname_field.value),str(phone_field.value),str(address_field.value), str(lon), str(lat)))
                    cur.execute("INSERT INTO hasla_potrzebujacych (nr_tel,haslo) VALUES (%s, %s)", (str(phone_field.value),str(password_field.value)))
            else:
                    pass
            
            cur.connection.commit()
            
            snack = ft.SnackBar(ft.Text("Zarejestrowano pomyślnie! Możesz się teraz zalogować."), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            
            # Przejście do logowania po sukcesie
            run_login(page, menu_return, user_type)

        except Exception as e:
            print("ERROR OCCURED:", str(e) )
            snack = ft.SnackBar(ft.Text(f"Błąd rejestracji: Podany numer może już istnieć, lub wystąpił inny błąd."), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            cur.close()
            conn.close()
            
    
        

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
                on_click= handle_registration,
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
    
    if user_type == "Potrzebujący":
        cur.execute("SELECT * FROM hasla_potrzebujacych WHERE nr_tel = %s;", (str(number),))
    elif user_type == "Wolontariusz":
        cur.execute("SELECT * FROM hasla_wolontariuszy WHERE nr_tel = %s;", (str(number),))
    else:
        pass #jakis wyjatek idk

    user = cur.fetchone()


    if not user:
        login_failed(page, menu_return, user_type, "login_error")
    elif user['haslo'] != password:
        login_failed(page, menu_return, user_type, "password_error")
    else:
        login_successful(page, menu_return, user_type, user['id'])


    cur.close()
    conn.close()
    
def run_login(page: ft.Page, menu_return, user_type, login_fail = "ok"):
    page.clean()
    page.bgcolor = "#e8f0f6"

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )

    if user_type not in ["Potrzebujący", "Wolontariusz"]:
        page.add(ft.Text("Nieprawidłowy typ użytkownika", size=20, color=ft.Colors.RED))
        return

    if user_type == "Potrzebujący":
        img_src = "src/assets/needy.png"
    else:
        img_src = "src/assets/volunteer.png"

    if login_fail == "login_error":
        message = "Nieprawidłowy numer telefonu"
    elif login_fail == "password_error":
        message = "Nieprawidłowe hasło"
    else:
        message = ""

    icon_size = 100
    form_width = 350
    
    label_style = ft.TextStyle(weight=ft.FontWeight.BOLD, size=20, color="#132434")
    
    number_field = ft.TextField(
        bgcolor=ft.Colors.WHITE,
        border_color="#132434",
        border_radius=10,
        height=60,
        text_style=ft.TextStyle(size=18, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        content_padding=15
    )
    
    password_field = ft.TextField(
        password=True,
        can_reveal_password=True,
        bgcolor=ft.Colors.WHITE,
        border_color="#132434",
        border_radius=10,
        height=60,
        text_style=ft.TextStyle(size=18, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
        content_padding=15
    )
    
    form_card = ft.Container(
        width=form_width,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=ft.Padding.only(left=20, right=20, top=70, bottom=20),
        margin=ft.Margin.only(top=icon_size // 2),
        content=ft.Column(
            controls=[
                ft.Text("NUMER TELEFONU", style=label_style),
                number_field,
                ft.Container(height=10),
                ft.Text("HASŁO", style=label_style),
                password_field,
                ft.Text(message, size=16, color=ft.Colors.RED, weight=ft.FontWeight.BOLD) if message else ft.Container(),
                ft.Container(height=15),
                ft.FilledButton(
                    content=ft.Text("ZALOGUJ SIĘ", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: verify_login(page, menu_return, user_type, number_field.value, password_field.value),
                    style=ft.ButtonStyle(
                        bgcolor="#8b0333",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=form_width,
                    height=65,
                )
            ]
        )
    )
    
    avatar = ft.Container(
        width=icon_size,
        height=icon_size,
        bgcolor="#78b6db",
        border_radius=20,
        alignment=ft.alignment.center if hasattr(ft, 'alignment') and hasattr(ft.alignment, 'center') else ft.Alignment.CENTER,
        content=ft.Image(src=img_src, width=icon_size*0.7, height=icon_size*0.7, fit=ft.BoxFit.CONTAIN)
    )
    
    stack = ft.Stack(
        controls=[
            form_card,
            ft.Container(top=0, left=(form_width - icon_size) / 2, content=avatar)
        ],
        width=form_width
    )
    
    reg_section = ft.Container(
        width=form_width,
        bgcolor="#132434",
        border_radius=20,
        padding=20,
        on_click=lambda e: register_user(page, menu_return, user_type),
        content=ft.Column(
            controls=[
                ft.Text("Nie masz konta?", color=ft.Colors.WHITE, size=16),
                ft.Text("ZAREJESTRUJ SIĘ", color=ft.Colors.WHITE, size=22, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    
    page.add(
        ft.Column(
            controls=[stack, ft.Container(height=20), reg_section],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )