"""Pantalla de tienda y detalles de los juegos de Steam."""

import asyncio
import logging

import flet as ft

from steam_api import SteamStoreAPI
from views.cart import CartView

log = logging.getLogger(f"app.{__name__}")


class StoreView:
    def __init__(self, page):
        self.page = page
        self.api = SteamStoreAPI()
        self.games = []
        self.cart_items = {}
        self.loading = False
        self.received_count = 0
        self.cart_label = ft.Text("Carrito (0)", color=ft.Colors.WHITE)
        self.status = ft.Text("Conectando con Steam Store…", color=ft.Colors.GREY_400)
        self.grid = ft.GridView(
            expand=True,
            max_extent=250,
            child_aspect_ratio=0.82,
            spacing=18,
            run_spacing=18,
        )
        self.results_area = ft.Column(expand=True, controls=[self.grid])
        self.search = ft.TextField(
            hint_text="Buscar juegos…",
            prefix_icon=ft.Icons.SEARCH,
            width=250,
            on_change=self.filter_games,
        )
        self.store_tab = ft.Button(
            content="Tienda",
            icon=ft.Icons.STOREFRONT,
            bgcolor=ft.Colors.CYAN_700,
            on_click=self.show_store,
        )
        self.cart_tab = ft.Button(
            content=ft.Row(
                tight=True,
                spacing=6,
                controls=[ft.Icon(ft.Icons.SHOPPING_CART), self.cart_label],
            ),
            bgcolor=ft.Colors.BLUE_GREY_800,
            on_click=self.show_cart,
        )
        self.catalog_view = self._build_catalog()
        self.body = ft.Container(expand=True, content=self.catalog_view)

    def build(self):
        return ft.Column(
            expand=True,
            spacing=20,
            controls=[self._build_header(), self.body],
        )

    async def load_catalog(self):
        if self.loading:
            return
        self.loading = True
        self.received_count = 0
        self.games = self.api.get_placeholders()
        self._refresh_grid()
        self.status.value = f"Cargando datos de Steam (0/{len(self.games)})…"
        self.page.update()
        try:
            self.games = await self.api.get_catalog(self._on_game_loaded)
            priced = sum(game["price"] is not None for game in self.games)
            if priced:
                self.status.value = f"{priced}/{len(self.games)} precios disponibles · Steam Store · USD."
            else:
                self.status.value = "Fichas listas; Steam no devolvió precios actuales. Pulsa Actualizar para reintentar."
            failed = sum(game["load_error"] for game in self.games)
            log.info(
                "Se cargaron %d juegos; %d precios disponibles y %d fichas incompletas",
                len(self.games), priced, failed,
            )
        except Exception:
            log.exception("Error al cargar el catálogo de Steam")
            self.status.value = "No se pudo cargar Steam. Pulsa Actualizar para reintentar."
        finally:
            self.loading = False
            self.page.update()

    def _on_game_loaded(self, loaded_game):
        for index, game in enumerate(self.games):
            if game["appid"] == loaded_game["appid"]:
                self.games[index] = loaded_game
                break
        self.received_count += 1
        self.status.value = f"Cargando datos de Steam ({self.received_count}/{len(self.games)})…"
        self._refresh_grid()
        self.page.update()

    def refresh_catalog(self):
        if not self.loading:
            asyncio.create_task(self.load_catalog())

    def _build_header(self):
        return ft.Row(
            wrap=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.SPORTS_ESPORTS, size=34, color=ft.Colors.CYAN_300),
                        ft.Text(
                            "PIXEL VAULT",
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
                    controls=[self.search, self.store_tab, self.cart_tab],
                ),
            ],
        )

    def _build_catalog(self):
        return ft.Column(
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
                                        "Descubre juegos, consulta sus precios y revisa sus detalles.",
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
                    wrap=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Juegos de Steam", size=22, weight=ft.FontWeight.BOLD),
                        ft.Row(
                            tight=True,
                            spacing=10,
                            controls=[
                                self.status,
                                ft.TextButton(
                                    content="Actualizar",
                                    icon=ft.Icons.REFRESH,
                                    on_click=self.refresh_catalog,
                                ),
                            ],
                        ),
                    ],
                ),
                self.results_area,
            ],
        )

    def _refresh_grid(self):
        query = self.search.value.strip().lower() if self.search.value else ""
        matching_games = [
            game
            for game in self.games
            if query in game["title"].lower()
            or query in " ".join(game["genres"]).lower()
            or query in game["description"].lower()
        ]
        if matching_games:
            self.grid.controls = [self._game_card(game) for game in matching_games]
            self.results_area.controls = [self.grid]
        elif query:
            self.results_area.controls = [
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.SEARCH_OFF, size=52, color=ft.Colors.CYAN_300),
                        ft.Text(
                            "Juego no encontrado",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f'No hay resultados para “{query}”. Prueba con otro título o género.',
                            color=ft.Colors.GREY_400,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Button(
                            content="Limpiar búsqueda",
                            icon=ft.Icons.CLEAR,
                            on_click=self.clear_search,
                        ),
                    ],
                )
            ]
        else:
            self.results_area.controls = [
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[ft.Text("No hay juegos disponibles.")],
                )
            ]

    def filter_games(self, event):
        self.search.value = event.control.value
        self._refresh_grid()
        self.page.update()

    def clear_search(self):
        self.search.value = ""
        self._refresh_grid()
        self.page.update()

    def _game_card(self, game):
        image = (
            ft.Image(
                src=game["image"],
                width=250,
                height=160,
                fit=ft.BoxFit.COVER,
                error_content=ft.Container(
                    width=250,
                    height=205,
                    alignment=ft.Alignment.CENTER,
                    bgcolor=ft.Colors.BLUE_GREY_800,
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=54, color=ft.Colors.CYAN_300),
                ),
                border_radius=ft.BorderRadius.only(top_left=16, top_right=16),
            )
            if game.get("image")
            else ft.Container(
                width=250,
                height=160,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.BLUE_GREY_800,
                content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=54, color=ft.Colors.CYAN_300),
            )
        )
        genre_label = " · ".join(game["genres"]) or "Juego de Steam"
        return ft.Container(
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
            on_click=lambda e, selected=game: self.show_game(selected),
            content=ft.Column(
                spacing=0,
                controls=[
                    image,
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
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    game["price_label"],
                                    size=17,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.CYAN_300,
                                ),
                                ft.Text(
                                    genre_label,
                                    color=ft.Colors.GREY_400,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def show_game(self, game):
        details = [
            ft.Text(game["description"], color=ft.Colors.GREY_300),
            ft.Text(f"Géneros: {', '.join(game['genres']) or 'No disponibles'}"),
            ft.Text(f"Plataformas: {', '.join(game['platforms']) or 'No disponibles'}"),
            ft.Text(f"Lanzamiento: {game['release']}"),
        ]
        if game["developers"]:
            details.append(ft.Text(f"Desarrollador: {', '.join(game['developers'])}"))
        if game["publishers"]:
            details.append(ft.Text(f"Distribuidor: {', '.join(game['publishers'])}"))

        image = (
            ft.Image(
                src=game["image"],
                width=320,
                height=150,
                fit=ft.BoxFit.COVER,
                border_radius=12,
            )
            if game.get("image")
            else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=56, color=ft.Colors.CYAN_300)
        )
        can_add = game["price"] is not None
        actions = [
            ft.Button(
                content="Añadir al carrito",
                icon=ft.Icons.ADD_SHOPPING_CART,
                bgcolor=ft.Colors.CYAN_700,
                color=ft.Colors.WHITE,
                disabled=not can_add,
                on_click=lambda e, selected=game: self.add_to_cart(selected),
            ),
            ft.TextButton(
                content="Abrir ficha en Steam",
                url=f"https://store.steampowered.com/app/{game['appid']}/",
            ),
            ft.TextButton(content="Cerrar", on_click=self.page.pop_dialog),
        ]
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
                        image,
                        *details,
                        ft.Text(
                            game["price_label"],
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_300,
                        ),
                    ],
                ),
            ),
            scrollable=True,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.page.show_dialog(dialog)

    def add_to_cart(self, game):
        item = self.cart_items.setdefault(
            game["title"], {"game": game, "quantity": 0}
        )
        item["quantity"] += 1
        self._update_cart_label()
        self.page.pop_dialog()
        self.show_cart()

    def change_quantity(self, title, amount):
        item = self.cart_items.get(title)
        if item is None:
            return
        item["quantity"] += amount
        if item["quantity"] <= 0:
            del self.cart_items[title]
        self._update_cart_label()
        self.body.content = self._build_cart()
        self.page.update()

    def _update_cart_label(self):
        count = sum(item["quantity"] for item in self.cart_items.values())
        self.cart_label.value = f"Carrito ({count})"

    def _build_cart(self):
        return CartView(self.cart_items, self.change_quantity, self.show_store).build()

    def show_store(self):
        self.body.content = self.catalog_view
        self.store_tab.bgcolor = ft.Colors.CYAN_700
        self.cart_tab.bgcolor = ft.Colors.BLUE_GREY_800
        self.page.update()

    def show_cart(self):
        self.body.content = self._build_cart()
        self.store_tab.bgcolor = ft.Colors.BLUE_GREY_800
        self.cart_tab.bgcolor = ft.Colors.CYAN_700
        self.page.update()
