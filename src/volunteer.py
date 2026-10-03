import flet as ft

def view_accepted_needs(page, user):
    page.clean()
    content = [
        ft.Column(
            controls = [
                ft.Text("PRZYJĘTE POTRZEBY", size=20, color=ft.Colors.BLACK),
                ft.Column(
                    controls = [
                        ft.Container(
                            content = [
                                ft.Row(
                                    controls = [
                                        ft.Column(
                                            controls = [
                                                ft.Text(need.category, size=20, color=ft.Colors.WHITE),
                                                ft.Divider(),
                                                ft.Column(
                                                    controls = [
                                                        ft.Text("KOMU POMAGAM?", size=20, color=ft.Colors.WHITE),
                                                        ft.Text(need.needy, size=15, color=ft.Colors.WHITE),
                                                    ]
                                                ),
                                                ft.Divider(),
                                                ft.Column(
                                                    controls = [
                                                        ft.Text("NUMER TELEFONU", size=20, color=ft.Colors.WHITE),
                                                        ft.Text(need.volunteer.number, size=15, color=ft.Colors.WHITE),
                                                    ]
                                                ),
                                                ft.Divider(),
                                                ft.Column(
                                                    controls = [
                                                        ft.Text("UWAGI", size=20, color=ft.Colors.WHITE),
                                                        ft.TextField("W TRAKCIE REALIZACJI", size=15, color=ft.Colors.WHITE), #nie wiem czy tak
                                                    ]
                                                )
                                            ]
                                        ),
                                        ft.Image(src="src/assets/check.png", width=50, height=50, fit=ft.BoxFit.CONTAIN)
                                    ],
                                )                                      
                            ],
                            bgcolor="#8b0333") for need in user.needs]
                    )
                ]
            )
    ]

    page.add(content)



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

    content = ft.Column(
        controls = [
            ft.FilledButton("PRZYJĘTE POTRZEBY", on_click=lambda e: view_accepted_needs(page, user),
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("NOWE POTRZEBY", on_click=lambda e: new_needs(),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
            ft.FilledButton("POSTĘPY", on_click=lambda e: accomplishments(), 
                            style=ft.ButtonStyle(bgcolor="#132434"), width=200, height=50),
            ft.FilledButton("MOJE KONTO", on_click=lambda e: view_profile(),
                            style=ft.ButtonStyle(bgcolor="#8b0333"), width=200, height=50),
        ]
    )

    page.add(
        content
    )
