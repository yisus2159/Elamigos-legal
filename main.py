"""Punto de entrada de Pixel Vault."""

import asyncio
import logging

import flet as ft

from views.store import StoreView
from views.elamigos import ElamigosView

LOG_LEVEL = logging.INFO
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")
logging.getLogger("app").setLevel(LOG_LEVEL)


def main(page: ft.Page):
    page.title = "Elamigos legal"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.GREY_900
    page.padding = 24

    store = StoreView(page)
    elamigos = ElamigosView(page)

    # ── Controles de pestaña ─────────────────────────────────────────────────
    tab_store_btn = ft.Button(
        content=ft.Row(
            tight=True,
            spacing=6,
            controls=[ft.Icon(ft.Icons.STOREFRONT), ft.Text("Steam Store")],
        ),
        bgcolor=ft.Colors.CYAN_700,
    )
    tab_api_btn = ft.Button(
        content=ft.Row(
            tight=True,
            spacing=6,
            controls=[ft.Icon(ft.Icons.CLOUD), ft.Text("Elamigos Legal API")],
        ),
        bgcolor=ft.Colors.BLUE_GREY_800,
    )

    body = ft.Container(expand=True)

    def show_store(_event=None):
        body.content = store.build()
        tab_store_btn.bgcolor = ft.Colors.CYAN_700
        tab_api_btn.bgcolor   = ft.Colors.BLUE_GREY_800
        asyncio.create_task(store.load_catalog())
        page.update()

    def show_api(_event=None):
        body.content = elamigos.build()
        tab_store_btn.bgcolor = ft.Colors.BLUE_GREY_800
        tab_api_btn.bgcolor   = ft.Colors.CYAN_700
        page.update()

    tab_store_btn.on_click = show_store
    tab_api_btn.on_click   = show_api

    nav_bar = ft.Row(
        spacing=12,
        controls=[
            ft.Icon(ft.Icons.SPORTS_ESPORTS, size=34, color=ft.Colors.CYAN_300),
            ft.Text("PIXEL VAULT", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(expand=True),
            tab_store_btn,
            tab_api_btn,
        ],
    )

    # Mostrar Steam Store por defecto
    show_store()

    page.add(
        ft.Column(
            expand=True,
            spacing=20,
            controls=[nav_bar, body],
        )
    )


ft.run(main)
