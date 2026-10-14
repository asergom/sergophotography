# sergophotography

Web: https://asergom.github.io/sergophotography/

## Estructura

```
index.html                 portada
newgallery/<serie>.html    una página por serie (la genera tools/build_gallery.py)
newgallery/images/fulls/   fotos ORIGINALES a resolución completa (nunca se modifican)
newgallery/images/raw/     versiones sin revelar (<nombre>_ori.jpg), opcional
newgallery/images/web/     versiones para la web (se generan solas, no editar)
cover/cover.jpg            foto de portada
assets/css, js, fonts      estilos, visor de fotos y tipografía
icons/                     logos SVG
tools/build_gallery.py     script que genera las versiones web y las páginas
```

## Añadir o cambiar fotos

1. Copia la foto (JPG) en `newgallery/images/fulls/<serie>/`.
   Si quieres la comparación «raw_view», pon la versión sin revelar en
   `newgallery/images/raw/<serie>/<mismo-nombre>_ori.jpg`.
2. Ejecuta (necesita Python 3 y Pillow: `pip install Pillow`):

   ```
   python tools/build_gallery.py
   ```

   Crea las versiones web (480, 960, 1600 y 2560 px en WebP calidad 90, con
   color sRGB y datos EXIF), lee ISO, velocidad, diafragma y focal, y
   reescribe las páginas de las series. Solo procesa las fotos nuevas o cambiadas.
3. Sube los cambios (`git add -A && git commit && git push`).

Para crear una serie nueva: añade una línea a `ALBUMS` al principio del script,
crea la carpeta `newgallery/images/fulls/<serie>/`, pon su icono en `icons/` y
añade su enlace al menú de `index.html`.

## Calidad de imagen

- En la rejilla y en el visor, cada dispositivo descarga la versión que encaja
  con su pantalla (unos 150 KB en un móvil, unos 700 KB en una pantalla 4K).
  El WebP a calidad 90 es visualmente indistinguible del original.
- El botón **full_resolution ↗** del visor abre el JPG original intacto.
- `_config.yml` deja `images/raw`, `tools` y este README fuera de la web
  publicada (siguen en el repositorio).
