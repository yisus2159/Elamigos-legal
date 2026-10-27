"""Vista del catálogo de juegos cargado desde la API de Elamigos legal."""

import asyncio
import logging

import flet as ft

from elamigos_api import ElamigosAPI, ElamigosAPIError
import httpx2 as httpx

log = logging.getLogger(f"app.{__name__}")

# Paleta visual coherente con el resto de la app
_BG_CARD   = ft.Colors.BLUE_GREY_900
_BG_BADGE  = ft.Colors.CYAN_900
_ACCENT    = ft.Colors.CYAN_300
_MUTED     = ft.Colors.GREY_400
_GREEN     = ft.Colors.GREEN_400
_ORANGE    = ft.Colors.ORANGE_400
_RED       = ft.Colors.RED_400


def _status_color(status: int) -> str:
    """Devuelve un color según si el código es exitoso, advertencia o error."""
    if 200 <= status < 300:
        return _GREEN
    if 300 <= status < 500:
        return _ORANGE
    return _RED


class ElamigosView:
    """Pestaña que muestra el catálogo obtenido desde la API de evaluación.

    Flujo:
        1. `build()` construye la UI y lanza `_fetch()` como tarea asíncrona.
        2. `_fetch()` llama a la API, guarda los datos en RAM y llama a `_render()`.
        3. `_render()` dibuja las tarjetas de juego en el grid.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.api  = ElamigosAPI()

        # ── Indicador de estado HTTP (solo código numérico) ─────────────────
        self._http_badge = ft.Container(
            visible=False,
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=8,
            bgcolor=_BG_BADGE,
            content=ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=_ACCENT),
        )

        # ── Texto de estado general ──────────────────────────────────────────
        self._status_text = ft.Text(
            "Conectando con la API de Elamigos legal…",
            color=_MUTED,
        )

        # ── Grid de tarjetas ─────────────────────────────────────────────────
        self._grid = ft.GridView(
            expand=True,
            max_extent=260,
            child_aspect_ratio=0.80,
            spacing=18,
            run_spacing=18,
        )
        self._results_area = ft.Column(expand=True, controls=[self._grid])

        # ── Búsqueda ─────────────────────────────────────────────────────────
        self._search = ft.TextField(
            hint_text="Buscar en Elamigos legal…",
            prefix_icon=ft.Icons.SEARCH,
            width=260,
            on_change=self._on_search,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Construcción de UI
    # ─────────────────────────────────────────────────────────────────────────

    def build(self) -> ft.Control:
        asyncio.create_task(self._fetch())

        header_banner = ft.Container(
            padding=24,
            border_radius=18,
            bgcolor=_BG_CARD,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        tight=True,
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Catálogo · Elamigos Legal",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                "Datos cargados en tiempo real desde la API de evaluación.",
                                color=_MUTED,
                            ),
                        ],
                    ),
                    ft.Icon(ft.Icons.CLOUD_DOWNLOAD, size=52, color=_ACCENT),
                ],
            ),
        )

        toolbar = ft.Row(
            wrap=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Juegos de la API", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    tight=True,
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self._http_badge,
                        self._status_text,
                        ft.TextButton(
                            content="Actualizar",
                            icon=ft.Icons.REFRESH,
                            on_click=self._on_refresh,
                        ),
                    ],
                ),
            ],
        )

        return ft.Column(
            expand=True,
            spacing=20,
            controls=[
                header_banner,
                ft.Row(
                    wrap=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[toolbar, self._search],
                ),
                self._results_area,
            ],
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Lógica de carga
    # ─────────────────────────────────────────────────────────────────────────

    async def _fetch(self, *, force: bool = False) -> None:
        """Realiza la solicitud a la API y actualiza la UI."""
        self._set_status("Consultando la API…", _MUTED)
        self._set_badge(None)
        self.page.update()

        try:
            games = await self.api.fetch_games(force=force)
            self._set_badge(200)
            self._set_status(
                f"200 – {len(games)} juego(s) cargado(s) y guardado(s) en RAM.",
                _GREEN,
            )
            self._render(games)

        except ElamigosAPIError as err:
            self._set_badge(err.status_code)
            self._set_status(err.user_message, _status_color(err.status_code))
            self._show_error(err.user_message)
            log.error("ElamigosAPIError: %s", err)

        except httpx.TimeoutException:
            self._set_badge(504)
            msg = "504 – Tiempo de espera agotado. Intenta de nuevo."
            self._set_status(msg, _RED)
            self._show_error(msg)
            log.error("Timeout al consultar la API de Elamigos.")

        except httpx.RequestError as exc:
            self._set_badge(503)
            msg = f"503 – Error de red: {exc}"
            self._set_status(msg, _RED)
            self._show_error(msg)
            log.error("RequestError: %s", exc)

        except RuntimeError as exc:
            # API Key no encontrada
            self._set_badge(401)
            msg = f"401 – {exc}"
            self._set_status(msg, _RED)
            self._show_error(str(exc))
            log.error("RuntimeError (API Key): %s", exc)

        except Exception as exc:
            self._set_badge(500)
            msg = "500 – Error inesperado."
            self._set_status(msg, _RED)
            self._show_error(str(exc))
            log.exception("Error inesperado en ElamigosView: %s", exc)

        finally:
            self.page.update()

    # ─────────────────────────────────────────────────────────────────────────
    # Render de tarjetas
    # ─────────────────────────────────────────────────────────────────────────

    def _render(self, games: list[dict]) -> None:
        """Dibuja las tarjetas de juego en el grid."""
        query = (self._search.value or "").strip().lower()
        filtered = [
            g for g in games
            if not query
            or query in g.get("title", "").lower()
            or query in g.get("genre", "").lower()
            or query in g.get("description", "").lower()
        ]

        if filtered:
            self._grid.controls = [self._game_card(g) for g in filtered]
            self._results_area.controls = [self._grid]
        elif query:
            self._results_area.controls = [self._no_results_view(query)]
        else:
            self._results_area.controls = [
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[ft.Text("La API no devolvió juegos.", color=_MUTED)],
                )
            ]

    def _game_card(self, game: dict) -> ft.Control:
        art = game.get("art", "")
        price = game.get("price", 0)
        price_label = "Gratis" if price == 0 else f"${price:.2f}"
        rating = game.get("rating", "N/A")

        cover = (
            ft.Image(
                src=art,
                width=260,
                height=155,
                fit=ft.BoxFit.COVER,
                border_radius=ft.BorderRadius.only(top_left=16, top_right=16),
                error_content=ft.Container(
                    width=260,
                    height=155,
                    bgcolor=ft.Colors.BLUE_GREY_800,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=48, color=_ACCENT),
                ),
            )
            if art
            else ft.Container(
                width=260,
                height=155,
                bgcolor=ft.Colors.BLUE_GREY_800,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=48, color=_ACCENT),
            )
        )

        return ft.Container(
            bgcolor=_BG_CARD,
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
            on_click=lambda e, g=game: self._show_detail(g),
            content=ft.Column(
                spacing=0,
                controls=[
                    cover,
                    ft.Container(
                        padding=14,
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Text(
                                    game.get("title", "Sin título"),
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Text(price_label, size=15, weight=ft.FontWeight.BOLD, color=_ACCENT),
                                        ft.Text("·", color=_MUTED),
                                        ft.Icon(ft.Icons.STAR, size=13, color=_ORANGE),
                                        ft.Text(str(rating), size=13, color=_MUTED),
                                    ],
                                ),
                                ft.Text(
                                    game.get("genre", ""),
                                    color=_MUTED,
                                    size=12,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def _show_detail(self, game: dict) -> None:
        price = game.get("price", 0)
        price_label = "Gratis" if price == 0 else f"${price:.2f}"
        art = game.get("art", "")

        cover = (
            ft.Image(src=art, width=380, height=180, fit=ft.BoxFit.COVER, border_radius=12)
            if art
            else ft.Icon(ft.Icons.VIDEOGAME_ASSET, size=56, color=_ACCENT)
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(game.get("title", "Sin título"), weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        cover,
                        ft.Text(game.get("description", ""), color=_MUTED),
                        ft.Divider(color=ft.Colors.BLUE_GREY_800),
                        ft.Row(spacing=16, wrap=True, controls=[
                            ft.Text(f"Género: {game.get('genre', 'N/A')}"),
                            ft.Text(f"Plataforma: {game.get('platform', 'N/A')}"),
                            ft.Text(f"Lanzamiento: {game.get('release', 'N/A')}"),
                            ft.Row(spacing=4, controls=[
                                ft.Icon(ft.Icons.STAR, size=14, color=_ORANGE),
                                ft.Text(str(game.get("rating", "N/A"))),
                            ]),
                        ]),
                        ft.Text(
                            price_label,
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=_ACCENT,
                        ),
                    ],
                ),
            ),
            scrollable=True,
            actions=[ft.TextButton(content="Cerrar", on_click=self.page.pop_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dialog)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers de UI
    # ─────────────────────────────────────────────────────────────────────────

    def _no_results_view(self, query: str) -> ft.Control:
        return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.SEARCH_OFF, size=52, color=_ACCENT),
                ft.Text("Sin resultados", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(f'No hay juegos para "{query}".', color=_MUTED, text_align=ft.TextAlign.CENTER),
                ft.Button(
                    content="Limpiar búsqueda",
                    icon=ft.Icons.CLEAR,
                    on_click=self._clear_search,
                ),
            ],
        )

    def _show_error(self, message: str) -> None:
        self._results_area.controls = [
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=52, color=_RED),
                    ft.Text("Error al cargar la API", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(message, color=_MUTED, text_align=ft.TextAlign.CENTER),
                    ft.Button(
                        content="Reintentar",
                        icon=ft.Icons.REFRESH,
                        on_click=self._on_refresh,
                    ),
                ],
            )
        ]

    def _set_status(self, text: str, color: str) -> None:
        self._status_text.value = text
        self._status_text.color = color

    def _set_badge(self, code: int | None) -> None:
        """Muestra/actualiza la pastilla con el código HTTP."""
        if code is None:
            self._http_badge.visible = False
            return
        badge_text: ft.Text = self._http_badge.content
        badge_text.value = str(code)
        badge_text.color = _status_color(code)
        self._http_badge.bgcolor = ft.Colors.BLUE_GREY_800
        self._http_badge.visible = True

    # ─────────────────────────────────────────────────────────────────────────
    # Handlers
    # ─────────────────────────────────────────────────────────────────────────

    def _on_refresh(self, _event=None) -> None:
        self.api.clear_cache()
        asyncio.create_task(self._fetch(force=True))

    def _on_search(self, event) -> None:
        self._search.value = event.control.value
        games = self.api.cached_games
        if games is not None:
            self._render(games)
        self.page.update()

    def _clear_search(self, _event=None) -> None:
        self._search.value = ""
        games = self.api.cached_games
        if games is not None:
            self._render(games)
        self.page.update()
