# Wix Scraper

Extrae todo el contenido de una web publicada en Wix (texto, estructura por secciones, imágenes a resolución original, vídeos, embeds, enlaces, tipografías y colores) para poder rehacerla en otro sitio.

## Instalación (una vez)

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

> En este PC `python` no está en el PATH; usa `C:\Users\calvo\AppData\Local\Programs\Python\Python312\python.exe`.

## Uso

```bash
python wix_scraper.py https://calvoalvaro12.wixsite.com/-lvarocg-a --out output
```

Opciones: `--max-pages N`, `--no-mobile` (sin capturas móviles), `--no-download` (solo inventario, sin descargar).

## Qué genera (`output/`)

| Ruta | Contenido |
|---|---|
| `README.md` | Resumen: menú de navegación, lista de páginas, tipografías/colores, inventario de imágenes, vídeos, enlaces externos y recursos rotos |
| `site.json` | Todo en JSON (para generar la nueva web automáticamente) |
| `pages/<slug>/content.md` | Contenido de cada página en orden, por secciones, con imágenes locales |
| `pages/<slug>/page.json` | Bloques en bruto con posición (x, y, w, h) y estilos computados |
| `pages/<slug>/desktop.png`, `mobile.png` | Capturas de página completa |
| `pages/<slug>/rendered.html` | HTML renderizado |
| `assets/images/` | Imágenes originales (sin los recortes/compresión de Wix) |
| `assets/videos/` | Vídeos subidos a Wix (mp4, máxima calidad) |
| `assets/thumbnails/` | Miniaturas de los vídeos de YouTube/Vimeo |

## Cómo funciona

1. Lee `sitemap.xml` y además recorre los enlaces internos, así encuentra también las páginas que no están en el menú.
2. Renderiza cada página con Chromium (Wix necesita JavaScript) y hace scroll para forzar la carga diferida.
3. Extrae los bloques del DOM en orden, además de los metadatos de Wix (`data-image-info`, `data-video-info`) y el JSON interno de cada página, con lo que también saca las imágenes ocultas en carruseles.
4. Convierte las URLs de Wix (`/v1/fill/w_300,...`) a la del archivo original y lo descarga.
5. Los recursos a los que Wix responde 403/404 se marcan como **rotos**: están borrados del gestor de medios y tampoco se ven en la web publicada.
