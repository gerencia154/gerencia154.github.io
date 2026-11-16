# Ranking público de Trading Latam

Página estática del Ranking y widget reutilizable. Ambos se generan con la misma descarga pública del proceso diario; el widget no realiza peticiones de datos desde el navegador.

## Insertar el Top 5

Copia este HTML en tu página cuando la ruta publicada esté disponible:

```html
<iframe
  src="https://gerencia154.github.io/widget/"
  title="Top 5 del Ranking de Trading Latam"
  width="100%"
  height="720"
  style="border:0; max-width:640px; display:block;"
  loading="lazy"
  referrerpolicy="no-referrer"
></iframe>
```

La página del widget se adapta desde 320 px de ancho. La altura de 720 px permite el contenido habitual en móvil; aumenta el valor si tu diseño o los alias más largos lo requieren. El iframe mantiene su propio desplazamiento si el contenido supera la altura elegida. No necesita JavaScript, cookies, formularios ni acceso al contenido de tu página. Los reportes se abren en una pestaña nueva.

El Top 5 conserva el orden de la fuente y muestra alias públicos, bróker, plataforma, TL-Score y caída máxima. Un guion indica una métrica no disponible; un cero publicado sigue siendo cero. La fecha visible es la fecha de la fuente, no la de visita. Si el proceso diario falla, permanece la última versión publicada con su fecha.

Fuente y atribución: [Ranking de Trading Latam](https://trading-latam.com/ranking-toptraders/), datos bajo [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Conserva la atribución visible incluida en el widget. Los resultados pasados no garantizan resultados futuros.

## Generar y verificar

Requiere Python 3 y su biblioteca estándar, sin paquetes adicionales:

```sh
python -m unittest discover -s tests -v
python scripts/build.py
python -m http.server 8000
```

Abre `http://localhost:8000/widget/` para revisar el widget. Las pruebas usan datos sintéticos y no acceden a la red. `scripts/build.py` obtiene una sola vez el JSON público existente y genera `index.html` y `widget/index.html`. El workflow diario existente publica ambos archivos; la plantilla principal no cambia.
