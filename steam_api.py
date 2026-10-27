"""Cliente concurrente para el catálogo público de Steam Store."""

import asyncio
import json
import logging
from pathlib import Path
from urllib.parse import urlencode

import httpx2 as httpx

log = logging.getLogger(f"app.{__name__}")


class SteamStoreAPI:
    """Carga fichas de Steam y consulta un respaldo de precios de Steam."""

    DETAILS_URL = "https://store.steampowered.com/api/appdetails"
    CHEAPSHARK_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals"
    STEAM_STORE_ID = "1"
    BATCH_SIZE = 6
    MAX_CONCURRENT_BATCHES = 3
    MAX_CONCURRENT_PRICE_LOOKUPS = 6
    REQUEST_TIMEOUT = 5
    PRICE_REQUEST_TIMEOUT = 10
    IMAGE_URL_TEMPLATE = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{}/header.jpg"

    def __init__(self, catalog_path=None):
        self.catalog_path = catalog_path or Path(__file__).with_name("games.json")

    def _read_catalog(self):
        with open(self.catalog_path, encoding="utf-8") as catalog_file:
            return json.load(catalog_file)

    def get_placeholders(self):
        """Crea tarjetas inmediatas mientras llegan las respuestas."""
        return [self._placeholder(entry) for entry in self._read_catalog()]

    async def get_catalog(self, on_game_loaded=None):
        """Consulta varios app IDs por solicitud y publica cada lote al llegar."""
        catalog = self._read_catalog()
        batches = [
            catalog[index : index + self.BATCH_SIZE]
            for index in range(0, len(catalog), self.BATCH_SIZE)
        ]
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_BATCHES)
        price_semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_PRICE_LOOKUPS)
        results = {}

        headers = {"User-Agent": "PixelVault/1.0 (videogame-catalog-app)"}
        async with httpx.AsyncClient(timeout=self.REQUEST_TIMEOUT, headers=headers) as client:
            tasks = [
                asyncio.create_task(
                    self._get_batch(client, semaphore, price_semaphore, batch)
                )
                for batch in batches
            ]
            for task in asyncio.as_completed(tasks):
                for game in await task:
                    results[game["appid"]] = game
                    if on_game_loaded:
                        on_game_loaded(game)

        return [results[entry["appid"]] for entry in catalog]

    async def _get_batch(self, client, semaphore, price_semaphore, entries):
        app_ids = ",".join(str(entry["appid"]) for entry in entries)
        query = urlencode({"appids": app_ids, "cc": "us", "l": "spanish"})
        steam_url = f"{self.DETAILS_URL}?{query}"
        try:
            async with semaphore:
                payload = await self._fetch_from_proxy(client, steam_url)
            games = []
            for entry in entries:
                app_id = entry["appid"]
                result = payload.get(str(app_id), {})
                if result.get("success") and "data" in result:
                    games.append(self._parse_game(app_id, result["data"], entry))
                else:
                    log.warning("Steam no devolvió datos para %s", app_id)
                    games.append(self._unavailable_game(entry))
        except (httpx.HTTPError, ValueError, KeyError) as error:
            log.warning("No se pudo cargar el lote de Steam (%s): %s", app_ids, error)
            games = [self._unavailable_game(entry) for entry in entries]

        # Steam Store bloquea CORS en el navegador. CheapShark ofrece una API
        # CORS pública; storeID=1 restringe los resultados a ofertas de Steam.
        to_price = [
            (index, entry)
            for index, (entry, game) in enumerate(zip(entries, games))
            if game["price"] is None
        ]
        if to_price:
            lookups = [
                self._lookup_steam_price(client, price_semaphore, entry)
                for _, entry in to_price
            ]
            prices = await asyncio.gather(*lookups)
            for (index, _), price_data in zip(to_price, prices):
                if price_data is not None:
                    games[index].update(price_data)
        return games

    async def _lookup_steam_price(self, client, semaphore, entry):
        try:
            async with semaphore:
                response = await client.get(
                    self.CHEAPSHARK_DEALS_URL,
                    params={
                        "storeID": self.STEAM_STORE_ID,
                        "steamAppID": str(entry["appid"]),
                        "pageSize": 1,
                    },
                    headers={"User-Agent": "PixelVault/1.0 (videogame-catalog-app)"},
                    timeout=self.PRICE_REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                offers = response.json()
            if not isinstance(offers, list) or not offers:
                return None
            price = float(offers[0]["salePrice"])
            log.info("Precio Steam recibido para %s: %.2f USD", entry["appid"], price)
            return {
                "price": price,
                "price_label": "Gratis" if price == 0 else f"${price:.2f} USD",
                "is_free": price == 0,
                "price_source": "Steam Store",
            }
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as error:
            log.debug("Sin precio de respaldo para %s: %s", entry["appid"], error)
            return None

    async def _fetch_from_proxy(self, client, steam_url):
        requests = [
            asyncio.create_task(client.get(steam_url)),
            asyncio.create_task(
                client.get(
                    "https://api.allorigins.win/raw",
                    params={"url": steam_url},
                )
            ),
            asyncio.create_task(client.get(f"https://cors.eu.org/{steam_url}")),
        ]
        last_error = None
        try:
            for request in asyncio.as_completed(requests):
                try:
                    response = await request
                    response.raise_for_status()
                    data = response.json()
                    if isinstance(data, dict):
                        return data
                    raise ValueError("El proxy devolvió una respuesta no válida")
                except (httpx.HTTPError, ValueError) as error:
                    last_error = error
            raise last_error or ValueError("No hay un proxy CORS disponible")
        finally:
            for request in requests:
                if not request.done():
                    request.cancel()
            await asyncio.gather(*requests, return_exceptions=True)

    @staticmethod
    def _placeholder(entry):
        return {
            "appid": entry["appid"],
            "title": entry["title"],
            "description": entry.get("description", "Cargando información desde Steam…"),
            "image": SteamStoreAPI.IMAGE_URL_TEMPLATE.format(entry["appid"]),
            "price": None,
            "price_label": "Consultando Steam…",
            "genres": entry.get("genres", []),
            "platforms": entry.get("platforms", []),
            "release": entry.get("release", "No disponible"),
            "developers": entry.get("developers", []),
            "publishers": entry.get("publishers", []),
            "is_free": False,
            "load_error": False,
        }

    @staticmethod
    def _parse_game(app_id, data, entry):
        price_info = data.get("price_overview") or {}
        price = price_info.get("final", 0) / 100 if price_info else None
        if data.get("is_free"):
            price = 0.0
            price_label = "Gratis"
        elif price is None:
            price_label = "Precio no disponible"
        else:
            price_label = f"${price:.2f} USD"

        return {
            "appid": app_id,
            "title": data.get("name") or entry["title"],
            "description": data.get("short_description") or entry.get("description", "Sin descripción disponible."),
            "image": data.get("header_image") or SteamStoreAPI.IMAGE_URL_TEMPLATE.format(app_id),
            "price": price,
            "price_label": price_label,
            "genres": [item["description"] for item in data.get("genres", [])] or entry.get("genres", []),
            "platforms": [
                platform.title()
                for platform, available in data.get("platforms", {}).items()
                if available
            ] or entry.get("platforms", []),
            "release": data.get("release_date", {}).get("date") or entry.get("release", "No disponible"),
            "developers": data.get("developers") or entry.get("developers", []),
            "publishers": data.get("publishers") or entry.get("publishers", []),
            "is_free": data.get("is_free", False),
            "load_error": False,
            "price_source": "Steam Store",
        }

    @staticmethod
    def _unavailable_game(entry):
        return {
            "appid": entry["appid"],
            "title": entry["title"],
            "description": entry.get("description", "Steam no devolvió la información."),
            "image": SteamStoreAPI.IMAGE_URL_TEMPLATE.format(entry["appid"]),
            "price": None,
            "price_label": "Precio no disponible",
            "genres": entry.get("genres", []),
            "platforms": entry.get("platforms", []),
            "release": entry.get("release", "No disponible"),
            "developers": entry.get("developers", []),
            "publishers": entry.get("publishers", []),
            "is_free": False,
            "load_error": True,
        }
