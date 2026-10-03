import flet as ft
import needy as nd
import volunteer as vl

def main(page: ft.Page):
    def menu():
        page.clean()
        page.window.height = 750
        page.window.width = 450
        page.appbar = None
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        content = ft.Column(
            controls = [
                ft.FilledButton("Potrzebujący", on_click=lambda e: nd.select_needy(page, menu), width=200, height=50),
                ft.FilledButton("Wolontariusz", on_click=lambda e: vl.select_volunteer(page, menu), width=200, height=50),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        page.add(content)

    menu()

if __name__ == "__main__":
    ft.run(main)
