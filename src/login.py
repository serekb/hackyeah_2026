import flet as ft

def run_login(page: ft.Page, menu_return, user_type):
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
        img_src = "src/assets/needy_icon.jpg"
    else:
        img_src = "src/assets/volunteer_icon.png"

    content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src=img_src, width=50, height=50, fit=ft.BoxFit.CONTAIN),
                ft.Text(f"Próbujesz zalogować się jako {user_type}", size=20, color=ft.Colors.BLACK),
                ft.TextField(label="Email"),
                ft.TextField(label="Hasło", password=True, can_reveal_password=True),
                ft.FilledButton("Zaloguj się", on_click=lambda e: print("Zalogowano!")),
                ft.Row(
                    controls=[
                        ft.Text("Nie masz konta?", color=ft.Colors.RED),
                        ft.FilledButton("Zarejestruj się", on_click=lambda e: print("Zarejestrowano!"))
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