# Elamigos legal

## Descripción
Elamigos legal es una aplicación de escritorio y web moderna desarrollada en Python utilizando el framework Flet. Funciona como una tienda digital interactiva de videojuegos, permitiendo a los usuarios explorar un catálogo dinámico, filtrar títulos por nombre o género, ver información detallada en modales, gestionar un carrito de compras y cambiar de vista de forma fluida.

## Características Principales
- **Catálogo Responsivo:** Visualización de juegos en una cuadrícula (GridView) moderna y adaptable con diseño oscuro.

- **Búsqueda en Tiempo Real:** Filtra instantáneamente los juegos del catálogo según su título o género.

- **Detalles del Juego:** Al hacer clic en cualquier tarjeta, se despliega una ventana emergente (AlertDialog) con la descripción completa, plataformas, fecha de lanzamiento, calificación y precio.

- **Gestión de Carrito:** Añade juegos al carrito, incrementa o disminuye cantidades y calcula automáticamente el total de artículos con un contador dinámico.

- **Navegación Fluida:** Permite alternar fácilmente entre la vista principal de la tienda y el carrito de compras.

## Estructura del Proyecto
```text
├── .venv/
├── views/
│   ├── cart.py
│   └── store.py
├── .gitignore
├── games.json
├── main.py
├── pyproject.toml
├── README.md
├── steam_api.py
└── uv.lock
```

## Descripción de los archivos
 `main.py` (El núcleo de la aplicación)
Es el archivo principal y el punto de entrada (main) de todo el proyecto. Aquí se centraliza la mayor parte de la lógica de la interfaz de usuario (UI):

Gestión de Estado: Administra el estado global de la aplicación, como los elementos agregados al carrito (cart_items) y la actualización dinámica del contador.

Vistas y Navegación: Controla la barra superior (header), la barra de búsqueda en tiempo real, las pestañas de navegación y el cambio fluido entre la tienda y el carrito.

Componentes Visuales: Define la cuadrícula principal (GridView) del catálogo, el diseño de las tarjetas de cada juego (game_card) y los diálogos modales (show_game) que muestran los detalles extendidos de un título.

`Games.json`Archivo de almacenamiento estructurado en formato JSON utilizado como base de datos local para la información de los juegos.

`steam_api.py`Módulo o servicio dedicado a la integración y comunicación con la API de Steam. 

`views/cart.py` (La vista del carrito)
Este archivo modulariza la interfaz correspondiente al carrito de compras:

Función build_cart_view: Se encarga de construir y retornar el diseño visual de la pantalla del carrito.

`gitignore`:indica cuales archivos o carpetas deben excluirse del control de versiones.

Interactividad: Muestra los productos seleccionados, permite modificar cantidades (incrementar o disminuir), calcular subtotales y totales, y provee un botón de retorno rápido a la tienda para continuar explorando.

`pyproject.toml`Archivo de configuración central del proyecto y definición de metadatos de dependencias.

`uv.lock`Archivo de bloqueo de versiones generado por el gestor de paquetes uv, asegurando la reproducibilidad del entorno.

`README`Documentación descriptiva del proyecto, guías de instalación y uso.

## Requisitos e Instalación
Para ejecutar este proyecto en tu máquina local, asegúrate de tener instalado Python 3.8 o superior.

## Instala las dependencias necesarias (Flet):
```powershell
pip install flet
```
 ## Cómo Ejecutar la Aplicación
Una vez instaladas las dependencias, ejecuta el archivo principal desde tu terminal:

```powershell
python main.py
```

La aplicación se abrirá automáticamente en una ventana nativa de Flet 

## Tecnologías Utilizadas
`Python:` Lógica general de la aplicación.

`Flet:` Framework basado en Flutter para construir interfaces de usuario en Python de forma sencilla y potente.

## Estado del proyecto
El proyecto se encuentra en una etapa de Prototipo Funcional Completo (MVP - Producto Mínimo Viable). Las características esenciales de la interfaz y la experiencia del usuario ya están totalmente implementadas y operativas.

## Autor 
Jesus Alvarez