"""Vista de carrito de Pixel Vault."""

import flet as ft


class CartView:
    def __init__(self, cart_items, change_quantity, continue_shopping):
        self.cart_items = cart_items
        self.change_quantity = change_quantity
        self.continue_shopping = continue_shopping

    def build(self):
        if not self.cart_items:
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
                        on_click=self.continue_shopping,
                    ),
                ],
            )

        rows = []
        total = 0.0
        for title, item in self.cart_items.items():
            game = item["game"]
            quantity = item["quantity"]
            unit_price = game["price"] or 0.0
            line_total = unit_price * quantity
            total += line_total
            rows.append(self._cart_row(title, game, quantity, line_total))

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
                            on_click=self.continue_shopping,
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

    def _cart_row(self, title, game, quantity, line_total):
        image = (
            ft.Image(
                src=game["image"],
                width=110,
                height=52,
                fit=ft.BoxFit.COVER,
                border_radius=8,
            )
            if game.get("image")
            else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=38, color=ft.Colors.CYAN_300)
        )
        return ft.Container(
            padding=12,
            border_radius=14,
            bgcolor=ft.Colors.BLUE_GREY_900,
            content=ft.Row(
                spacing=14,
                controls=[
                    image,
                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            ft.Text(game["title"], size=17, weight=ft.FontWeight.BOLD),
                            ft.Text(game["price_label"], color=ft.Colors.CYAN_300),
                        ],
                    ),
                    ft.Row(
                        tight=True,
                        spacing=6,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.REMOVE,
                                tooltip="Quitar una unidad",
                                on_click=lambda e, name=title: self.change_quantity(name, -1),
                            ),
                            ft.Text(str(quantity), size=16),
                            ft.IconButton(
                                icon=ft.Icons.ADD,
                                tooltip="Agregar una unidad",
                                on_click=lambda e, name=title: self.change_quantity(name, 1),
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
                                on_click=lambda e, name=title: self.change_quantity(name, -999),
                            ),
                        ],
                    ),
                ],
            ),
        )
