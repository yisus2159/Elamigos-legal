Elamigos legal

Descripción
Elamigos legal es una aplicación de escritorio y web moderna desarrollada en Python utilizando el framework Flet. Funciona como una tienda digital interactiva de videojuegos, permitiendo a los usuarios explorar un catálogo dinámico, filtrar títulos por nombre o género, ver información detallada en modales, gestionar un carrito de compras y cambiar de vista de forma fluida.

Características Principales
Catálogo Responsivo: Visualización de juegos en una cuadrícula (GridView) moderna y adaptable con diseño oscuro.

Búsqueda en Tiempo Real: Filtra instantáneamente los juegos del catálogo según su título o género.

Detalles del Juego: Al hacer clic en cualquier tarjeta, se despliega una ventana emergente (AlertDialog) con la descripción completa, plataformas, fecha de lanzamiento, calificación y precio.

Gestión de Carrito: Añade juegos al carrito, incrementa o disminuye cantidades y calcula automáticamente el total de artículos con un contador dinámico.

Navegación Fluida: Permite alternar fácilmente entre la vista principal de la tienda y el carrito de compras.

 Estructura del Proyecto
Elamigos-legal/
│
├── main.py             # Archivo principal con la lógica de la interfaz y navegación
├── data.py             # Base de datos local con la lista de juegos (GAMES)
└── views/
    └── cart.py         # Vista y lógica del carrito de compras (build_cart_view)

Descripción de los archivos
 main.py (El núcleo de la aplicación)
Es el archivo principal y el punto de entrada (main) de todo el proyecto. Aquí se centraliza la mayor parte de la lógica de la interfaz de usuario (UI):

Gestión de Estado: Administra el estado global de la aplicación, como los elementos agregados al carrito (cart_items) y la actualización dinámica del contador.

Vistas y Navegación: Controla la barra superior (header), la barra de búsqueda en tiempo real, las pestañas de navegación y el cambio fluido entre la tienda y el carrito.

Componentes Visuales: Define la cuadrícula principal (GridView) del catálogo, el diseño de las tarjetas de cada juego (game_card) y los diálogos modales (show_game) que muestran los detalles extendidos de un título.

data.py (La fuente de datos)
Funciona como una base de datos local y estática para la aplicación:

Estructura de Juegos (GAMES): Contiene una lista de diccionarios con la información de cada videojuego disponible en la tienda (título, género, precio, calificación, plataformas, fecha de lanzamiento, descripción e imagen de portada).

Desacoplamiento: Mantiene los datos separados de la interfaz, lo que permite modificar, agregar o quitar juegos fácilmente sin alterar el código de diseño.

views/cart.py (La vista del carrito)
Este archivo modulariza la interfaz correspondiente al carrito de compras:

Función build_cart_view: Se encarga de construir y retornar el diseño visual de la pantalla del carrito.

Interactividad: Muestra los productos seleccionados, permite modificar cantidades (incrementar o disminuir), calcular subtotales y totales, y provee un botón de retorno rápido a la tienda para continuar explorando.
Requisitos e Instalación
Para ejecutar este proyecto en tu máquina local, asegúrate de tener instalado Python 3.8 o superior.

Clona o descarga el repositorio:

Bash
git clone https://github.com/@yisus2159/Elamigos legal.git
cd Elamigos legal
Instala las dependencias necesarias (Flet):


pip install flet

 Cómo Ejecutar la Aplicación
Una vez instaladas las dependencias, ejecuta el archivo principal desde tu terminal:

Bash
python main.py

La aplicación se abrirá automáticamente en una ventana nativa de Flet (también puedes configurarla para correr en el navegador web modificando la ejecución si lo deseas).

Tecnologías Utilizadas
Python: Lógica general de la aplicación.

Flet: Framework basado en Flutter para construir interfaces de usuario en Python de forma sencilla y potente.

Estado del proyecto
El proyecto se encuentra en una etapa de Prototipo Funcional Completo (MVP - Producto Mínimo Viable). Las características esenciales de la interfaz y la experiencia del usuario ya están totalmente implementadas y operativas.

Autor 
Jesus Alvarez