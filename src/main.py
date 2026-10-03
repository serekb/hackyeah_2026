import flet as ft
import needy as nd
import volunteer as vl
import login as lg

def main(page: ft.Page):
    def menu():
        page.clean()
        page.window.title = "Wybierz typ użytkownika"
        page.update()
        page.window.height = 750
        page.window.width = 450
        page.window.resizable = False
        page.window_center = True
        page.update()

        page.appbar = None
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        content = ft.Column(
            controls = [
                ft.FilledButton("Potrzebujący", on_click=lambda e: lg.run_login(page, menu, "Potrzebujący"), width=200, height=50),
                ft.FilledButton("Wolontariusz", on_click=lambda e: lg.run_login(page, menu, "Wolontariusz"), width=200, height=50),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.add(content)

    menu()

if __name__ == "__main__":
    ft.run(main)
