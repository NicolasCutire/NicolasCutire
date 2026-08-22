---
name: poligono-trabajo
description: Recalcula el polígono de 10 ha (P1–P4), actualiza datos.tex (DOC-08) y redibuja el diagrama PNG de DOC-11. Usar cuando el usuario cambie coordenadas, frente, fondo, P1, P2, el rectángulo de trabajo o pida regenerar la imagen del plano.
---

# Polígono de trabajo (DOC-08 + DOC-11)

Fuente única: `Fuente LaTeX/actualizar_poligono.py`.

P1 queda fijo. `--p2` solo da el rumbo de la Interoceánica. Las medidas `--frente` y `--fondo` se fuerzan en UTM 19S; P3 y P4 salen al norte (izquierda rumbo Mazuco → Puerto Maldonado).

```bash
cd "Fuente LaTeX"
uv run --with matplotlib actualizar_poligono.py
# o con otros números:
uv run --with matplotlib actualizar_poligono.py \
  --p1 -12.912452,-70.170058 \
  --p2 -12.912497,-70.170981 \
  --frente 100 --fondo 1000
```

Eso escribe el bloque generado de `datos.tex` y `diagrama-10ha-puente-jayave.png`.

Luego recompilar al menos DOC-08 y DOC-11 con tectonic (`required_permissions: ["all"]`) y copiar los PDF a `Final Docs List/`.

No editar a mano las macros `\PUnoLat` … `\PCuatroN`, `\FrenteM`, `\FondoM` ni `\DistanciaPinGoogle` en `datos.tex`. El dígito en un nombre TeX (`P1`) parte el comando: por eso el pin Google se llama `\DistanciaPinGoogle`.
