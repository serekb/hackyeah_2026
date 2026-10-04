import math
import flet as ft
import psycopg2
import database as db
import login as lg

def view_accepted_needs(page: ft.Page, user_id, menu_return):
    page.clean()
    page.scroll = "auto"
    page.bgcolor = "#e8f0f6"
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            p.id_potrzeba, 
            p.nazwa_potrzeba, 
            p.opis,
            po.imie, 
            po.nazwisko, 
            po.numer_telefonu,
            pr.potwierdzenie_wolontariusza
        FROM PRZYPISANIE pr
        JOIN POTRZEBA p ON pr.id_potrzeba = p.id_potrzeba
        JOIN POTRZEBUJACY po ON pr.id_potrzebujacego = po.id_potrzebujacego
        WHERE pr.id_wolontariusza = %s AND pr.status != 'zrealizowane';
    """, (str(user_id),))
    needs_data = cur.fetchall()

    def confirm_need(e, need_id):
        conf_conn = db.get_db_connection()
        conf_cur = conf_conn.cursor()
        try:
            conf_cur.execute("UPDATE PRZYPISANIE SET potwierdzenie_wolontariusza = TRUE WHERE id_potrzeba = %s", (need_id,))
            
            conf_cur.execute("SELECT potwierdzenie_potrzebujacego, potwierdzenie_wolontariusza, id_wolontariusza FROM PRZYPISANIE WHERE id_potrzeba = %s", (need_id,))
            res = conf_cur.fetchone()
            if res['potwierdzenie_potrzebujacego'] and res['potwierdzenie_wolontariusza']:
                conf_cur.execute("UPDATE PRZYPISANIE SET status = 'zrealizowane' WHERE id_potrzeba = %s", (need_id,))
                conf_cur.execute("UPDATE WOLONTARIUSZE SET pkt = COALESCE(pkt, 0) + 1 WHERE id_wolontariusza = %s", (res['id_wolontariusza'],))
                
            conf_conn.commit()
            snack = ft.SnackBar(ft.Text("Zatwierdzono realizację!", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            view_accepted_needs(page, user_id, menu_return)
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            conf_cur.close()
            conf_conn.close()

    cards = []
    for need in needs_data:
        controls_list = [
            ft.Text(need['nazwa_potrzeba'], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        ]
        if need.get('opis'):
            controls_list.append(ft.Text(need['opis'], size=15, color="#b3ffffff", italic=True))
            
        controls_list.extend([
            ft.Divider(color=ft.Colors.WHITE),
            ft.Column(
                controls=[
                    ft.Text("POTRZEBUJĄCY", size=14, color=ft.Colors.WHITE),
                    ft.Text(f"{need['imie']} {need['nazwisko']}", size=15, color=ft.Colors.WHITE),
                ],
                spacing=2,
            ),
            ft.Divider(color=ft.Colors.WHITE),
            ft.Column(
                controls=[
                    ft.Text("NUMER TELEFONU", size=14, color=ft.Colors.WHITE),
                    ft.Text(need['numer_telefonu'], size=15, color=ft.Colors.WHITE),
                ],
                spacing=2,
            ),
        ])
        
        is_confirmed = need.get('potwierdzenie_wolontariusza', False)
        icon_color = ft.Colors.GREEN if is_confirmed else None
        
        icon_widget = ft.Container(
            content=ft.Image(
                src="src/assets/check.png",
                width=40,
                height=40,
                fit=ft.BoxFit.CONTAIN,
                color=icon_color
            ),
            on_click=None if is_confirmed else lambda e, nid=need['id_potrzeba']: confirm_need(e, nid)
        )

        cards.append(
            ft.Container(
                bgcolor="#8b0333",
                border_radius=8,
                padding=15,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(controls=controls_list, expand=True),
                        icon_widget,
                    ],
                ),
            )
        )

    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text("PRZYJĘTE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Text("W TRAKCIE REALIZACJI", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_800),
            *cards
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(
        ft.Container(
            width=410,
            content=content,
            alignment=ft.Alignment.CENTER
        )
    )
    cur.close()
    conn.close()

def filter_needs(user_id, radius_km: str | None):
    """Return unassigned needs within the requested radius of the volunteer."""
    if radius_km is None:
        raise ValueError("Podaj promień w kilometrach, np. 1 albo 2.5.")

    try:
        radius_km = float(radius_km.strip().replace(",", "."))
    except ValueError as exc:
        raise ValueError("Podaj promień w kilometrach, np. 1 albo 2.5.") from exc

    if not math.isfinite(radius_km) or radius_km <= 0:
        raise ValueError("Promień musi być dodatnią, skończoną liczbą kilometrów.")

    conn = db.get_db_connection()
    if conn is None:
        raise ConnectionError("Nie udało się połączyć z bazą danych.")

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT szerokosc_geograficzna, dlugosc_geograficzna
                FROM wolontariusze
                WHERE id_wolontariusza = %s;
                """,
                (str(user_id),),
            )
            volunteer = cur.fetchone()
            if (
                volunteer is None
                or volunteer["szerokosc_geograficzna"] is None
                or volunteer["dlugosc_geograficzna"] is None
            ):
                raise ValueError("Wolontariusz nie ma zapisanej lokalizacji.")

            latitude = volunteer["szerokosc_geograficzna"]
            longitude = volunteer["dlugosc_geograficzna"]
            cur.execute(
                """
                SELECT
                    p.id_potrzeba,
                    p.id_potrzebujacego,
                    p.nazwa_potrzeba,
                    p.opis,
                    n.imie,
                    n.nazwisko
                FROM potrzeba p
                JOIN potrzebujacy n
                  ON n.id_potrzebujacego = p.id_potrzebujacego
                WHERE n.szerokosc_geograficzna IS NOT NULL
                  AND n.dlugosc_geograficzna IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM przypisanie a
                      WHERE a.id_potrzeba = p.id_potrzeba
                  )
                  AND 6371.0088 * 2 * ASIN(SQRT(LEAST(1.0,
                      POWER(SIN(RADIANS(n.szerokosc_geograficzna - %s) / 2), 2)
                      + COS(RADIANS(%s))
                      * COS(RADIANS(n.szerokosc_geograficzna))
                      * POWER(SIN(RADIANS(n.dlugosc_geograficzna - %s) / 2), 2)
                  ))) <= %s;
                """,
                (latitude, latitude, longitude, radius_km),
            )
            return cur.fetchall()
    finally:
        conn.close()


def new_needs(page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    radius_field = ft.TextField(label="Kilometry", value="10", width=100)
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM POTRZEBA WHERE id_potrzebujacego NOT IN (SELECT id_potrzebujacego FROM PRZYPISANIE WHERE id_wolontariusza = %s);", (str(user_id),))
    needs = cur.fetchall()

    cur.execute("SELECT imie, nazwisko, id_potrzebujacego from potrzebujacy where id_potrzebujacego IN (SELECT id_potrzebujacego FROM POTRZEBA WHERE id_potrzebujacego NOT IN (SELECT id_potrzebujacego FROM PRZYPISANIE WHERE id_wolontariusza = %s));", (str(user_id),))
    needy_infos = cur.fetchall()
    
    def accept_need(e, need_id, needy_id):
        acc_conn = db.get_db_connection()
        acc_cur = acc_conn.cursor()
        try:
            acc_cur.execute(
                "INSERT INTO PRZYPISANIE (id_potrzeba, id_potrzebujacego, id_wolontariusza, status) VALUES (%s, %s, %s, %s)",
                (need_id, needy_id, user_id, 'w trakcie')
            )
            acc_conn.commit()
            snack = ft.SnackBar(ft.Text("Potrzeba została pomyślnie przyjęta!", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            
            new_needs(page, user_id, menu_return)
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            acc_cur.close()
            acc_conn.close()

    def need_card(need, needy_info):
        return ft.Container(
            bgcolor="#132434",
            border_radius=20,
            padding=20,
            width=410,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"{needy_info['imie']} {needy_info['nazwisko']}",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Divider(color=ft.Colors.WHITE),
                            ft.Text(
                                need["nazwa_potrzeba"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                need.get("opis") or "",
                                size=15,
                                color="#b3ffffff",
                                italic=True,
                            ),
                        ],
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Image(
                            src="src/assets/right_arrow.png",
                            width=50,
                            height=50,
                            fit=ft.BoxFit.CONTAIN,
                        ),
                        on_click=lambda e, need_id=need["id_potrzeba"],
                        needy_id=need["id_potrzebujacego"]: accept_need(
                            e, need_id, needy_id
                        ),
                    ),
                ],
            ),
        )

    available_needs_view = ft.Column(
        spacing=10,
        controls=[
            need_card(need, needy_info)
            for need in needs
            for needy_info in needy_infos
            if need["id_potrzebujacego"] == needy_info["id_potrzebujacego"]
        ],
    )

    def search_needs(_):
        available_needs_view.controls.clear()
        try:
            matching_needs = filter_needs(user_id, radius_field.value)
        except (ConnectionError, ValueError) as exc:
            available_needs_view.controls.append(
                ft.Text(str(exc), color=ft.Colors.RED)
            )
        except psycopg2.Error as exc:
            print(f"Błąd bazy danych podczas wyszukiwania potrzeb: {exc}")
            available_needs_view.controls.append(
                ft.Text(
                    "Wystąpił błąd podczas wyszukiwania. Spróbuj ponownie.",
                    color=ft.Colors.RED,
                )
            )
        else:
            if not matching_needs:
                available_needs_view.controls.append(
                    ft.Text("Nie znaleziono potrzeb w podanym promieniu.")
                )
            else:
                available_needs_view.controls.extend(
                    need_card(need, need) for need in matching_needs
                )
        page.update()

    filter_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("FILTRUJ PO LOKALIZACJI", size=20, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=5),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Odległość od Twojej lokalizacji",
                            color="#132434",
                            expand=True,
                        ),
                        radius_field,
                    ],
                    spacing=10,
                ),
                ft.Container(height=5),
                ft.FilledButton(
                    content=ft.Text("SZUKAJ", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    style=ft.ButtonStyle(bgcolor="#8b0333", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370,
                    height=55,
                    on_click=search_needs,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


    content = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            ft.Text("NOWE POTRZEBY", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
            ft.Container(height=5),
            filter_card,
            ft.Container(height=10),
            available_needs_view,
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(
        ft.Container(
            width=450,
            content=content,
            alignment=ft.Alignment.CENTER
        )
    )
    cur.close()
    conn.close()

def select_volunteer(page: ft.Page, menu_return, user_id):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "auto"

    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: menu_return(), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT 
    )

    btn_width = 410
    btn_height = 120

    content = ft.Column(
        controls=[
            ft.FilledButton(
                content=ft.Text("PRZYJĘTE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_accepted_needs(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("NOWE POTRZEBY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: new_needs(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#8b0333",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("POSTĘPY", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: accomplishments(page, user_id, menu_return), 
                style=ft.ButtonStyle(
                    bgcolor="#132434",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
            ft.FilledButton(
                content=ft.Text("MOJE KONTO", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                on_click=lambda e: view_profile(page, user_id, menu_return),
                style=ft.ButtonStyle(
                    bgcolor="#8b0333",
                    shape=ft.RoundedRectangleBorder(radius=20)
                ),
                width=btn_width,
                height=btn_height
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    page.add(
        ft.Column(
            controls=[content, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def accomplishments(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )

    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT PKT FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    points_data = cur.fetchone()
    # It might return a RealDictRow or a tuple. If no pkt, treat as 0
    points = points_data['pkt'] if points_data and points_data.get('pkt') is not None else 0
    
    if points < 15:
        medal_path = "src/assets/bronze_medal.png"   
    elif points < 50:
        medal_path = "src/assets/silver_medal.png"
    else:
        medal_path = "src/assets/gold_medal.png"

    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("TWOJE POSTĘPY", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=10),
                
                ft.Image(src=medal_path, width=220, height=220, fit=ft.BoxFit.CONTAIN),
                
                ft.Container(height=15),
                ft.Text("UDZIELONYCH POMOCY", size=18, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Text(f"{points}", size=50, weight=ft.FontWeight.BOLD, color="#8b0333"),
                
                ft.Container(height=20),
                
                ft.FilledButton(
                    content=ft.Text("POBIERZ CERTYFIKAT", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
                ft.FilledButton(
                    content=ft.Text("PRZYSŁUGUJĄCE ZNIŻKI", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    style=ft.ButtonStyle(bgcolor="#8b0333", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    cur.close()
    conn.close()

def view_profile(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: select_volunteer(page, menu_return, user_id), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM WOLONTARIUSZE WHERE id_wolontariusza = %s;", (str(user_id),))
    user = cur.fetchone()
    cur.close()
    conn.close()

    def create_textfield(value="", read_only=False):
        return ft.TextField(
            value=value,
            read_only=read_only,
            bgcolor=ft.Colors.WHITE if not read_only else ft.Colors.GREY_200,
            border_color="#132434",
            border_radius=10,
            height=50,
            text_style=ft.TextStyle(size=16, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            content_padding=15
        )

    address_field = create_textfield(value=user['adres_wolontariusza'])
    number_field = create_textfield(value=user['numer_telefonu'], read_only=True)
    org_field = create_textfield(value=user['organizacja'])
    
    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, size=16, weight=ft.FontWeight.BOLD, color="#132434"),
                field_obj
            ],
            spacing=5
        )
        
    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("MOJE KONTO", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=10),
                
                create_input_col("IMIĘ", create_textfield(value=user['imie'], read_only=True)),
                create_input_col("NAZWISKO", create_textfield(value=user['nazwisko'], read_only=True)),
                
                create_input_col("ADRES", address_field),
                create_input_col("NUMER TELEFONU", number_field),
                create_input_col("ORGANIZACJA", org_field),
                
                ft.Container(height=15),
                
                ft.FilledButton(
                    content=ft.Text("ZAPISZ ZMIANY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: save_data_changes(page, user_id, address_field.value, number_field.value, org_field.value),
                    style=ft.ButtonStyle(bgcolor="#4CAF50", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
                ft.FilledButton(
                    content=ft.Text("ZMIEŃ HASŁO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: change_password(page, user_id, menu_return),
                    style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
                ft.FilledButton(
                    content=ft.Text("USUŃ KONTO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: delete_account(page, user_id, "wolontariusz", menu_return),
                    style=ft.ButtonStyle(bgcolor="#8b0333", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def save_data_changes(page, user_id, address, number, org_field):
    try:
        conn = db.get_db_connection()
        cur = conn.cursor()
        
        # Only update editable fields using dictionary style parameterization
        cur.execute(
            "UPDATE WOLONTARIUSZE SET adres_wolontariusza = %(address)s, organizacja = %(org)s WHERE id_wolontariusza = %(user_id)s;", 
            {"address": str(address), "org": str(org_field), "user_id": str(user_id)}
        )
        
        conn.commit()
        snack = ft.SnackBar(ft.Text("Zapisano zmiany!", size=16), bgcolor=ft.Colors.GREEN)
        page.overlay.append(snack)
        snack.open = True
        page.update()
    except Exception as e:
        snack = ft.SnackBar(ft.Text(f"Błąd zapisu: {e}", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def change_password(page: ft.Page, user_id, menu_return):
    page.clean()
    page.bgcolor = "#e8f0f6"
    page.scroll = "auto"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.appbar = ft.AppBar(
        leading=ft.Container(
            content=ft.FilledButton(content=ft.Text("WRÓĆ", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), style=ft.ButtonStyle(bgcolor="#132434", shape=ft.RoundedRectangleBorder(radius=10)), on_click=lambda e: view_profile(page, user_id, menu_return), width=150, height=50),
            padding=10  
        ),
        leading_width=200,
        bgcolor=ft.Colors.TRANSPARENT
    )
    
    def create_passfield(hint):
        return ft.TextField(
            hint_text=hint,
            password=True,
            can_reveal_password=True,
            bgcolor=ft.Colors.WHITE,
            border_color="#132434",
            border_radius=10,
            height=50,
            text_style=ft.TextStyle(size=16, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD),
            content_padding=15
        )

    passwordbox_old = create_passfield("Stare hasło")
    passwordbox_new = create_passfield("Nowe hasło")
    passwordbox_confirm = create_passfield("Powtórz nowe hasło")
    
    def create_input_col(label_text, field_obj):
        return ft.Column(
            controls=[
                ft.Text(label_text, size=16, weight=ft.FontWeight.BOLD, color="#132434"),
                field_obj
            ],
            spacing=5
        )
        
    form_card = ft.Container(
        width=410,
        bgcolor=ft.Colors.WHITE,
        border=ft.Border.all(4, "#132434"),
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("ZMIEŃ HASŁO", size=24, weight=ft.FontWeight.BOLD, color="#132434"),
                ft.Container(height=10),
                create_input_col("STARE HASŁO", passwordbox_old),
                create_input_col("NOWE HASŁO", passwordbox_new),
                create_input_col("POWTÓRZ NOWE HASŁO", passwordbox_confirm),
                ft.Container(height=15),
                ft.FilledButton(
                    content=ft.Text("ZAPISZ ZMIANY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    on_click=lambda e: save_password_changes(page, user_id, passwordbox_old.value, passwordbox_new.value, passwordbox_confirm.value, menu_return),
                    style=ft.ButtonStyle(bgcolor="#4CAF50", shape=ft.RoundedRectangleBorder(radius=10)),
                    width=370, height=55
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(
        ft.Column(
            controls=[ft.Container(height=10), form_card, ft.Container(height=30)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

def save_password_changes(page: ft.Page, user_id, old_password: str, new_password: str, confirm_password: str, menu_return):
    conn = db.get_db_connection()
    cur = conn.cursor()
    # Zabezpieczenie takie samo jak dla potrzebujacego: uzywamy numeru tel do zlokalizowania w hasla_wolontariuszy
    cur.execute("SELECT numer_telefonu FROM wolontariusze WHERE id_wolontariusza = %s;", (str(user_id),))
    user_rec = cur.fetchone()
    if not user_rec:
        return
    phone = user_rec['numer_telefonu']
    
    cur.execute("SELECT haslo FROM hasla_wolontariuszy WHERE nr_tel = %s;", (phone,))
    pwd_rec = cur.fetchone()
    
    if not pwd_rec or pwd_rec['haslo'] != old_password:
        snack = ft.SnackBar(ft.Text("Nieprawidłowe stare hasło", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        return
        
    if new_password != confirm_password:
        snack = ft.SnackBar(ft.Text("Nowe hasła nie są zgodne", size=16), bgcolor=ft.Colors.RED)
        page.overlay.append(snack)
        snack.open = True
        page.update()
        return
        
    cur.execute("UPDATE hasla_wolontariuszy SET haslo = %s WHERE nr_tel = %s;", (new_password, phone))
    conn.commit()
    cur.close()
    conn.close()
    
    snack = ft.SnackBar(ft.Text("Hasło zostało zmienione", size=16), bgcolor=ft.Colors.GREEN)
    page.overlay.append(snack)
    snack.open = True
    view_profile(page, user_id, menu_return)

def delete_account(page, user_id, role, menu_return):
    def confirm_delete(e):
        dialog.open = False
        page.update()
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            tabela = 'wolontariusze' if role == 'wolontariusz' else 'potrzebujacy'
            kolumna = 'id_wolontariusza' if role == 'wolontariusz' else 'id_potrzebujacego'
            
            cur.execute(f"DELETE FROM {tabela} WHERE {kolumna} = %s;", (str(user_id),))
            conn.commit()
            snack = ft.SnackBar(ft.Text("Konto usunięte. Wylogowywanie...", size=16), bgcolor=ft.Colors.GREEN)
            page.overlay.append(snack)
            snack.open = True
            menu_return()
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Błąd: {err}", size=16), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        finally:
            cur.close()
            conn.close()

    def cancel_delete(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Usuwanie konta", size=22, weight=ft.FontWeight.BOLD),
        content=ft.Text("Czy na pewno chcesz bezpowrotnie usunąć swoje konto? Tej operacji nie można cofnąć.", size=16),
        actions=[
            ft.TextButton("ANULUJ", on_click=cancel_delete),
            ft.TextButton("USUŃ", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(dialog)
    dialog.open = True
    page.update()