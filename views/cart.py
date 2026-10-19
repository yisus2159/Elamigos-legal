import flet as ft


def build_cart_view(cart_items, change_quantity, continue_shopping):
    if not cart_items:
        return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            controls=[
                ft.Icon(ft.Icons.SHOPPING_CART, size=56, color=ft.Colors.GREY_500),
                ft.Text("Tu carrito está vacío", size=23, weight=ft.FontWeight.BOLD),
                ft.Text("Explora la tienda y agrega tus juegos favoritos."),
                ft.Button(
                    content="Ir a la tienda",
                    icon=ft.Icons.STOREFRONT,
                    on_click=continue_shopping,
                ),
            ],
        )

    rows = []
    total = 0.0
    for title, item in cart_items.items():
        game = item["game"]
        quantity = item["quantity"]
        line_total = game["price"] * quantity
        total += line_total
        rows.append(
            ft.Container(
                padding=12,
                border_radius=14,
                bgcolor=ft.Colors.BLUE_GREY_900,
                content=ft.Row(
                    spacing=14,
                    controls=[
                        ft.Image(
                            src=game["art"],
                            width=74,
                            height=92,
                            fit=ft.BoxFit.COVER,
                            border_radius=8,
                        ),
                        ft.Column(
                            expand=True,
                            spacing=5,
                            controls=[
                                ft.Text(game["title"], size=17, weight=ft.FontWeight.BOLD),
                                ft.Text(game["genre"], color=ft.Colors.GREY_400),
                                ft.Text(
                                    f"${game['price']:.2f} c/u",
                                    color=ft.Colors.CYAN_300,
                                ),
                            ],
                        ),
                        ft.Row(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    tooltip="Quitar una unidad",
                                    on_click=lambda e, name=title: change_quantity(name, -1),
                                ),
                                ft.Text(str(quantity), size=16),
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    tooltip="Agregar una unidad",
                                    on_click=lambda e, name=title: change_quantity(name, 1),
                                ),
                            ],
                        ),
                        ft.Column(
                            tight=True,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text(
                                    f"${line_total:.2f}",
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.TextButton(
                                    content="Quitar",
                                    on_click=lambda e, name=title: change_quantity(name, -999),
                                ),
                            ],
                        ),
                    ],
                ),
            )
        )

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Tu carrito", size=24, weight=ft.FontWeight.BOLD),
                    ft.Button(
                        content="Seguir comprando",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=continue_shopping,
                    ),
                ],
            ),
            ft.ListView(expand=True, spacing=10, controls=rows),
            ft.Container(
                padding=18,
                border_radius=14,
                bgcolor=ft.Colors.BLUE_GREY_900,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Total", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"${total:.2f}",
                            size=23,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_300,
                        ),
                    ],
                ),
            ),
        ],
    )
