# Expediente 10 ha Inambari (uso privado)

Carpeta completa para copiar en tu PC a:

`/home/nicolas/Documents/Personal Docs/Terreno Docs`

## Cómo traerlo a tu computadora (clonar)

En **tu Linux**, en una terminal:

```bash
mkdir -p "/home/nicolas/Documents/Personal Docs"
cd "/home/nicolas/Documents/Personal Docs"

git clone --branch cursor/terreno-expediente-c9c8 --single-branch \
  https://github.com/NicolasCutire/NicolasCutire.git terreno-github-tmp

mkdir -p "Terreno Docs"
cp -a terreno-github-tmp/Terreno-Docs/. "Terreno Docs/"
rm -rf terreno-github-tmp
```

Luego abre:

```bash
xdg-open "/home/nicolas/Documents/Personal Docs/Terreno Docs/Final Docs List"
```

Ahí están los PDF (incluye el **DOC-24**, recibo de S/ 20 000 en trato directo). También hay un texto para imprimir y firmar:

`Terreno Docs/PARA_FIRMAR_Recibo_20k_trato_directo.txt`

El plano de trabajo es `Final Docs List/11_Plano_Perimetrico_Trabajo.pdf`.

## Si tu repo es privado

Usa SSH o un token:

```bash
git clone --branch cursor/terreno-expediente-c9c8 --single-branch \
  git@github.com:NicolasCutire/NicolasCutire.git terreno-github-tmp
```

## Alternativa: zip

También está `Terreno-Docs-Expediente-10ha.zip` en esta carpeta (y en Artifacts del agente). En Cursor Web a veces **no se puede descargar** (Preview not available). Por eso está en GitHub.

## Advertencia

Estos archivos tienen DNI, teléfonos y direcciones. **No dejes la rama pública** más tiempo del necesario. Haz el repo **privado** o borra la rama después de copiar.
