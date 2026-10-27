"""Cliente para la API de evaluación de Elamigos legal (Jesús Álvarez).

La API Key NUNCA se escribe literalmente en este archivo.
Se lee desde la variable de entorno ELAMIGOS_API_KEY o, como respaldo,
desde el archivo `.env` ubicado junto a este módulo.

Endpoint protegido:
    GET /api/v1/jesusalvares/games
    Header: X-API-Key: <key>

Códigos de respuesta documentados:
    200 – OK, lista de juegos devuelta correctamente.
    401 – Falta la cabecera X-API-Key.
    403 – API Key inválida para este namespace.
    404 – Namespace de usuario no encontrado.
    422 – Error de validación (Unprocessable Entity).
"""

import asyncio
import logging
import os
from pathlib import Path

import httpx2 as httpx

log = logging.getLogger(f"app.{__name__}")

# ── Configuración ────────────────────────────────────────────────────────────
_BASE_URL = "https://progra-2-krw5.onrender.com"
_ENDPOINT = "/api/v1/jesusalvares/games"
_ENV_KEY  = "ELAMIGOS_API_KEY"
_ENV_FILE = Path(__file__).with_name(".env")

# Mensajes de error por código HTTP (todos los documentados en la spec)
_HTTP_ERRORS: dict[int, str] = {
    200: "OK",
    401: "401 – Falta la cabecera X-API-Key.",
    403: "403 – API Key inválida para este namespace.",
    404: "404 – Namespace de usuario no encontrado.",
    405: "405 – Método no permitido.",
    422: "422 – Error de validación en la solicitud.",
    500: "500 – Error interno del servidor.",
    502: "502 – Gateway incorrecto (servidor caído o reiniciándose).",
    503: "503 – Servicio no disponible.",
    504: "504 – Tiempo de espera del gateway agotado.",
}


def _load_api_key() -> str:
    """Carga la API Key desde el entorno o desde .env, nunca del código fuente."""
    # 1. Variable de entorno (más segura, ideal para producción)
    key = os.environ.get(_ENV_KEY, "").strip()
    if key:
        return key

    # 2. Archivo .env junto al módulo (desarrollo local)
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(_ENV_KEY + "="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    log.debug("API Key cargada desde %s", _ENV_FILE)
                    return key

    raise RuntimeError(
        f"API Key no encontrada. Defínela en la variable de entorno "
        f"'{_ENV_KEY}' o en el archivo '{_ENV_FILE}'."
    )


class ElamigosAPIError(Exception):
    """Excepción propia para errores de la API de Elamigos legal."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"[{status_code}] {detail}")

    @property
    def user_message(self) -> str:
        """Mensaje legible para mostrar en pantalla."""
        return _HTTP_ERRORS.get(self.status_code, f"{self.status_code} – Error desconocido.")


class ElamigosAPI:
    """Cliente asíncrono para el catálogo de Elamigos legal.

    Los datos se almacenan en RAM (``_cache``) para no repetir
    solicitudes innecesarias durante la misma sesión.
    """

    REQUEST_TIMEOUT = 15  # segundos

    def __init__(self):
        self._cache: list[dict] | None = None   # RAM: datos de la última consulta
        self._api_key: str = _load_api_key()    # se carga una sola vez

    # ── Propiedad de solo lectura para la caché ──────────────────────────────
    @property
    def cached_games(self) -> list[dict] | None:
        """Devuelve los juegos en RAM (None si aún no se han consultado)."""
        return self._cache

    # ── Método principal ─────────────────────────────────────────────────────
    async def fetch_games(self, *, force: bool = False) -> list[dict]:
        """Consulta el endpoint y devuelve la lista de juegos.

        Los datos se guardan en RAM. Si ``force=False`` y ya hay datos
        en caché se devuelven directamente sin hacer una nueva solicitud.

        Args:
            force: Si es ``True`` fuerza una nueva solicitud aunque haya caché.

        Returns:
            Lista de dicts con las claves: title, genre, platform, price,
            rating, release, art, description.

        Raises:
            ElamigosAPIError: Para cualquier error HTTP documentado.
            httpx.TimeoutException: Si el servidor no responde a tiempo.
            httpx.RequestError: Para errores de red genéricos.
        """
        if self._cache is not None and not force:
            log.info("Datos de Elamigos legal devueltos desde RAM (caché).")
            return self._cache

        url = f"{_BASE_URL}{_ENDPOINT}"
        headers = {"X-API-Key": self._api_key}

        log.info("Consultando API Elamigos legal: GET %s", url)

        try:
            async with httpx.AsyncClient(timeout=self.REQUEST_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
        except httpx.TimeoutException as exc:
            log.error("Tiempo de espera agotado al consultar la API: %s", exc)
            raise ElamigosAPIError(504, "Tiempo de espera agotado. El servidor tardó demasiado.") from exc
        except httpx.ConnectError as exc:
            log.error("Error de conexión con la API: %s", exc)
            raise ElamigosAPIError(503, "No se pudo conectar con el servidor de la API.") from exc
        except httpx.RequestError as exc:
            log.error("Error de red al consultar la API: %s", exc)
            raise ElamigosAPIError(503, f"Error de red: {exc}") from exc

        status = response.status_code
        log.info("Respuesta de la API → HTTP %d", status)

        # Manejo de errores por código de estado
        if status != 200:
            try:
                body = response.json()
                detail = body.get("detail", _HTTP_ERRORS.get(status, "Error desconocido."))
            except Exception:
                detail = _HTTP_ERRORS.get(status, f"Error HTTP {status}.")
            log.warning("API retornó error %d: %s", status, detail)
            raise ElamigosAPIError(status, detail)

        # Parsear respuesta exitosa
        try:
            data = response.json()
            items: list[dict] = data.get("items", [])
        except Exception as exc:
            log.error("No se pudo parsear la respuesta de la API: %s", exc)
            raise ElamigosAPIError(200, "Respuesta de la API no es JSON válido.") from exc

        # Guardar en RAM
        self._cache = items
        log.info("Datos guardados en RAM: %d juegos de Elamigos legal.", len(items))

        return self._cache

    def clear_cache(self) -> None:
        """Limpia los datos de la RAM para forzar una nueva consulta."""
        self._cache = None
        log.debug("Caché de Elamigos legal limpiada.")
