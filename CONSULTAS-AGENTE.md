# Contexto para un agente nuevo (web / Cursor Cloud)

Este archivo resume el hilo de trabajo del 20–22 ago 2026 para que **otro agente** pueda consultar el expediente **sin** el chat original.

El hilo de Cursor (este proyecto) es: [trato directo 10 ha](12db2a20-c6e6-4548-9ca8-d68250c67dd9). Un agente **web/cloud no hereda** esa conversación: solo ve lo que esté en el git.

## Dónde están los documentos

| Carpeta | Precio | Uso |
|---|---|---|
| `Trato-Directo/` | S/ 6 500 efectivo | Expediente original |
| `Trato-Directo-2/` | S/ 20 000 efectivo | Copia ajustada (usar esta para la casuística 20 k) |

PDF: `…/Final Docs List/`. Fuentes: `…/Fuente LaTeX/`. Acuerdos: `Para_Firma/` (y `Para firma 2/`, mismo precio en la copia 20 k).

Compilar: `tectonic` (`~/.local/bin/tectonic`) sobre `0*.tex 1*.tex 2*.tex` en `Fuente LaTeX/`, copiar PDF a `Final Docs List/`. Permisos de fuentes a menudo `all`.

## Hechos canónicos

- **Vendedor:** RICHAR DARWIN CUTIRE CONDORI, DNI 42610690, soltero, sin unión de hecho.
- **Compradores 50/50:** NICO ALVARO CUTIRE ARCE (48325017) y LUCY CUTIRE ARCE (47478852, soltera, contadora).
- Acto: independización **10 ha** + compraventa (no donación). Trato **directo** (Lucio no es parte; DOC-16 opcional).
- Matriz: partida **05007514**, 100 ha, U.C. 30362, Inambari. Remanente 90 ha.
- Recorte: franja **100 m** de frente en Interoceánica (norte), **adosada al lindero oeste real**; este se mueve hasta **10 ha netas**.
- Richar compró las 100 ha el **15 ago 2017** por **S/ 65 000**; inscripción de dominio **26 ago 2019**. El pago privado de las 10 ha es ~**2018** (fecha a confirmar).
- 20 k **superaba** 3 UIT 2018 (S/ 12 450): efectivo igual; no “bancarizar” en 2026.
- IR 5 % vendedor (ganancia): costo proporcional ~S/ 6 500 → ganancia ~S/ 13 500 → IR ilustrativo ~**S/ 675**. Notario pide Form. 1665 o “no obligado”. Mora 2018 vs liquidación 2026: ver DOC-23.
- Alcabala 2026: 20 k por debajo de 10 UIT (S/ 55 000) → probable inafectación; igual liquidar.
- Notario/abogado/ingeniero: `Dr.` / `Abog.` / `Ing.` + línea, sin nombres inventados.

## Cómo seguir en un agente web

1. Clonar la rama `cursor/terreno-expediente-c9c8` del repo GitHub `NicolasCutire/NicolasCutire`.
2. Abrir el proyecto en Cursor (Cloud Agent o desktop) y apuntar a `Trato-Directo-2/` si el caso es 20 000.
3. Leer `Trato-Directo-2/LEAME-TRATO-DIRECTO.md` y `Fuente LaTeX/datos.tex`.

**Privacidad:** hay DNI, teléfonos y domicilios. El repo histórico ha sido **público**. Conviene **privado** o no hacer merge a `main`.
