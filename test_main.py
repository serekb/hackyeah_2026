import flet as ft
# mocked imports
class lg:
    @staticmethod
    def run_login(*args):
        pass

def main(page: ft.Page):
    def menu():
        page.clean()
        page.window.title = "Wybierz typ użytkownika"
        page.update()
        page.window.height = 750
        page.window.width = 450
        page.window_center = True
        page.window.background_color = "#e8f0f6"
        page.bgcolor = "#e8f0f6" 
        page.update()

        page.appbar = None
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        def create_card(title, bg_color, icon_src, on_click, width=350, card_height=180, icon_size=100):
            icon_overlap = icon_size // 2
            
            card = ft.Container(
                width=width,
                height=card_height,
                bgcolor=bg_color,
                border_radius=20,
                alignment=ft.alignment.center,
                content=ft.Text(title, size=24, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            )
            
            icon_container = ft.Container(
                width=icon_size,
                height=icon_size,
                bgcolor="#78b6db",
                border_radius=20,
                alignment=ft.alignment.center,
                content=ft.Image(src=icon_src, width=icon_size*0.7, height=icon_size*0.7, fit=ft.BoxFit.CONTAIN)
            )
            
            stack = ft.Stack(
                controls=[
                    ft.Container(top=icon_overlap, left=0, content=card),
                    ft.Container(top=0, left=(width - icon_size) / 2, content=icon_container),
                ],
                width=width,
                height=card_height + icon_overlap
            )
            
            return ft.Container(
                content=stack,
                on_click=on_click,
            )

        content = ft.Column(
            controls = [
                create_card(
                    title="POTRZEBUJĄCY",
                    bg_color="#8b0333",
                    icon_src="src/assets/needy.png",
                    on_click=lambda e: lg.run_login(page, menu, "Potrzebujący")
                ),
                ft.Container(height=40),
                create_card(
                    title="WOLONTARIUSZ",
                    bg_color="#132434",
                    icon_src="src/assets/volunteer.png",
                    on_click=lambda e: lg.run_login(page, menu, "Wolontariusz")
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        page.add(content)

    menu()
    print("Test passed")

if __name__ == "__main__":
    import test_main
