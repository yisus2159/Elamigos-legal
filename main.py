import flet as ft

from data import GAMES
from views.cart import build_cart_view


def main(page: ft.Page):
    page.title = "Elamigos legal"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 24

    cart_items = {}
    cart_label = ft.Text("Carrito (0)", color=ft.Colors.WHITE)

    def update_cart_label():
        count = sum(item["quantity"] for item in cart_items.values())
        cart_label.value = f"Carrito ({count})"

    def game_card(game):
        return ft.Container(
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
            on_click=lambda e, selected=game: show_game(selected),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Image(
                        src=game["art"],
                        width=250,
                        height=205,
                        fit=ft.BoxFit.COVER,
                        border_radius=ft.BorderRadius.only(
                            top_left=16, top_right=16
                        ),
                    ),
                    ft.Container(
                        padding=16,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Text(
                                    game["title"],
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(game["genre"], color=ft.Colors.GREY_400),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            f"${game['price']:.2f}",
                                            size=17,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.CYAN_300,
                                        ),
                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.STAR,
                                                    color=ft.Colors.AMBER_400,
                                                    size=16,
                                                ),
                                                ft.Text(game["rating"]),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def show_game(game):
        def add_to_cart(e):
            item = cart_items.setdefault(
                game["title"], {"game": game, "quantity": 0}
            )
            item["quantity"] += 1
            update_cart_label()
            page.pop_dialog()
            go_cart()

        added_button = ft.Button(
            content="Añadir al carrito",
            icon=ft.Icons.ADD_SHOPPING_CART,
            bgcolor=ft.Colors.CYAN_700,
            color=ft.Colors.WHITE,
            on_click=add_to_cart,
        )
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(game["title"], weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=440,
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=14,
                    controls=[
                        ft.Image(
                            src=game["art"],
                            width=110,
                            height=145,
                            fit=ft.BoxFit.COVER,
                            border_radius=12,
                        ),
                        ft.Text(
                            game["description"],
                            color=ft.Colors.GREY_300,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=4,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(f"Género: {game['genre']}"),
                        ft.Text(f"Plataformas: {game['platform']}"),
                        ft.Text(f"Lanzamiento: {game['release']}  ·  ★ {game['rating']}"),
                        ft.Text(
                            f"${game['price']:.2f}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_300,
                        ),
                    ],
                ),
            ),
            scrollable=True,
            actions=[
                added_button,
                ft.TextButton(
                    content="Cerrar",
                    on_click=lambda: page.pop_dialog(),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.show_dialog(dialog)

    grid = ft.GridView(
        expand=True,
        max_extent=250,
        child_aspect_ratio=0.70,
        spacing=18,
        run_spacing=18,
    )
    grid.controls = [game_card(game) for game in GAMES]

    def filter_games(e):
        query = e.control.value.strip().lower()
        matching = [
            game
            for game in GAMES
            if query in game["title"].lower()
            or query in game["genre"].lower()
        ]
        grid.controls = [game_card(game) for game in matching]
        page.update()

    def change_quantity(title, amount):
        item = cart_items.get(title)
        if item is None:
            return
        item["quantity"] += amount
        if item["quantity"] <= 0:
            del cart_items[title]
        update_cart_label()
        body.content = build_cart_view(cart_items, change_quantity, go_store)
        page.update()

    def go_store():
        body.content = catalog_view
        store_tab.bgcolor = ft.Colors.CYAN_700
        cart_tab.bgcolor = ft.Colors.BLUE_GREY_800
        page.update()

    def go_cart():
        body.content = build_cart_view(cart_items, change_quantity, go_store)
        store_tab.bgcolor = ft.Colors.BLUE_GREY_800
        cart_tab.bgcolor = ft.Colors.CYAN_700
        page.update()

    search = ft.TextField(
        hint_text="Buscar juegos...",
        prefix_icon=ft.Icons.SEARCH,
        width=250,
        on_change=filter_games,
    )
    store_tab = ft.Button(
        content="Tienda",
        icon=ft.Icons.STOREFRONT,
        bgcolor=ft.Colors.CYAN_700,
        on_click=go_store,
    )
    cart_tab = ft.Button(
        content=ft.Row(
            tight=True,
            spacing=6,
            controls=[ft.Icon(ft.Icons.SHOPPING_CART), cart_label],
        ),
        bgcolor=ft.Colors.BLUE_GREY_800,
        on_click=go_cart,
    )
    catalog_view = ft.Column(
        expand=True,
        spacing=20,
        controls=[
            ft.Container(
                padding=24,
                border_radius=18,
                bgcolor=ft.Colors.BLUE_GREY_900,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            tight=True,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "Tu próxima aventura empieza aquí",
                                    size=27,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    "Descubre mundos nuevos. Elige tu siguiente juego favorito.",
                                    color=ft.Colors.GREY_300,
                                ),
                            ],
                        ),
                        ft.Icon(
                            ft.Icons.VIDEOGAME_ASSET,
                            size=54,
                            color=ft.Colors.CYAN_300,
                        ),
                    ],
                ),
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Juegos destacados", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Selecciona un juego para ver sus detalles",
                        color=ft.Colors.GREY_400,
                    ),
                ],
            ),
            grid,
        ],
    )
    body = ft.Container(expand=True, content=catalog_view)
    header = ft.Row(
        wrap=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, size=34, color=ft.Colors.CYAN_300),
                    ft.Text(
                        "Elamigos legal",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ],
            ),
            ft.Row(
                wrap=True,
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[search, store_tab, cart_tab],
            ),
        ],
    )
    page.add(ft.Column(expand=True, spacing=20, controls=[header, body]))


ft.run(main)
