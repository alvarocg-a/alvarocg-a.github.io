# Contenido pendiente

Cada hueco pendiente en la web tiene un **ID** visible (recuadro naranja con rayas o texto en naranja) y el atributo `data-placeholder="ID"` en el HTML. Para encontrarlo: busca el ID en el proyecto.

## Placeholders

| ID | Página | Qué falta |
|---|---|---|
| `BNG-TOOLS-DEBUG-TXT` | `bng-tools.html` | Texto de la Debugging Tool (en Wix solo había el título; he dejado una descripción provisional sacada de la captura) |
| `BNG-TOOLS-STREAMING-MEDIA` | `bng-tools.html` | Imagen o vídeo de Level Streaming |
| `BNG-TOOLS-STREAMING-TXT` | `bng-tools.html` | Texto de Level Streaming |
| `BNG-TOOLS-CHECKPOINT-MEDIA` | `bng-tools.html` | Imagen o vídeo de Checkpoints & saves |
| `BNG-TOOLS-CHECKPOINT-TXT` | `bng-tools.html` | Texto de Checkpoints & saves |
| `BNG-TOOLS-OPTIMIZATION-MEDIA` | `bng-tools.html` | Imagen o vídeo de Optimization |
| `BNG-TOOLS-OPTIMIZATION-TXT` | `bng-tools.html` | Texto de Optimization |
| `BNG-PROTO-ENEMIES-MORE` | `bng-prototyping.html` | El resto de enemigos (en Wix, tras el Puckarb, solo había una imagen de "WIP") |
| `BNG-PROTO-HYDROGEL-VIDEO` | `bng-prototyping.html` | Vídeo de Hydrogel: el de Wix (`tIn--X-9LRo`) es privado en YouTube |
| `BNG-PROTO-ELECTROPLASM-VIDEO` | `bng-prototyping.html` | Vídeo de Electroplasm (en Wix usaba el mismo vídeo privado) |
| `PP-BEATFOUND-ROLE`, `-ENGINE`, `-CONTRIB` | `beat-found.html` | Tu rol, el motor y tus contribuciones (itch.io no los indica) |
| `PP-YOUARENOBODY-ROLE`, `-ENGINE`, `-DATE`, `-CONTRIB` | `you-are-nobody.html` | Tu rol, el motor, la fecha/contexto y tus contribuciones |
| `BNG-BLINKBALL-VIDEO` | `bng-blinkball.html` | (Opcional) vídeo de gameplay de BlinkBall |

## Cómo sustituirlos

- **Imagen:** copia el archivo en `assets/img/…` y cambia el bloque `<div class="ph" …>…</div>` por:
  ```html
  <figure><div class="media"><img src="assets/img/bng/level-streaming.webp" alt="Descripción" loading="lazy" class="zoomable"></div></figure>
  ```
- **Vídeo de YouTube:** cambia el bloque por `<div class="yt" data-yt="ID_DEL_VIDEO" data-title="Título"></div>` (la miniatura se carga sola).
- **Texto:** cambia el `<p class="ph-text" …>…</p>` por párrafos normales `<p>…</p>`.

## Estructura

- Cada página es un `.html` en la raíz. El menú (`MENU`), el pie con el contacto, las pestañas de Bugs 'N' Guns y los enlaces anterior/siguiente (`GROUPS`) se generan desde `js/site.js`: para añadir una página, añade una entrada ahí.
- Estilos en `css/style.css`: colores (paleta *moss*) y tipografías en las variables de `:root`. Las fuentes (Barlow Condensed e Inter) están en `assets/fonts/`, sin depender de Google Fonts.
- Imágenes optimizadas (WebP) en `assets/img/`.
