import flet as ft

def select_volunteer(page: ft.Page, menu_return):
    page.clean()

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton("WRÓĆ", on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )

    content = ft.Text("Jestem wolontariuszem", size=20, color=ft.Colors.BLACK)

    page.add(
        content
    )
