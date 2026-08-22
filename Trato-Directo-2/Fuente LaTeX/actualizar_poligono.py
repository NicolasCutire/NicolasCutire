#!/usr/bin/env python3
"""
Actualiza el polígono de trabajo (100 m × 1 000 m por defecto) en un solo paso:

  1. Recalcula P2, P3 y P4 en UTM 19S (EPSG:32719) a partir de P1.
  2. Escribe las macros en datos.tex  →  DOC-08 y el resto del expediente.
  3. Redibuja diagrama-10ha-puente-jayave.png  →  DOC-11.

Uso (desde Fuente LaTeX/):

  uv run --with matplotlib actualizar_poligono.py

  uv run --with matplotlib actualizar_poligono.py \\
      --p1 -12.912452,-70.170058 \\
      --p2 -12.912497,-70.170981 \\
      --frente 100 --fondo 1000

P1 queda fijo. --p2 solo aporta el rumbo de la Interoceánica (el pin Google
original); la distancia P1–P2 se fuerza a --frente metros. P3 y P4 se
proyectan --fondo metros hacia el norte (izquierda rumbo Mazuco → P. Maldonado).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
DATOS = DIR / "datos.tex"
PNG = DIR / "diagrama-10ha-puente-jayave.png"

# WGS84 UTM (fórmulas USGS / paquete utm)
K0 = 0.9996
E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)
R = 6378137.0
M1 = 1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256
M2 = 3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024
M3 = 15 * E2 / 256 + 45 * E3 / 1024
M4 = 35 * E3 / 3072
E1 = (1 - math.sqrt(1 - E)) / (1 + math.sqrt(1 - E))
UTM_ZONE = 19


def latlon_to_utm(lat: float, lon: float, zone: int = UTM_ZONE) -> tuple[float, float]:
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lon0 = math.radians((zone - 1) * 6 - 180 + 3)
    n = R / math.sqrt(1 - E * math.sin(lat_rad) ** 2)
    t = math.tan(lat_rad) ** 2
    c = E_P2 * math.cos(lat_rad) ** 2
    a = math.cos(lat_rad) * (lon_rad - lon0)
    m = R * (
        M1 * lat_rad
        - M2 * math.sin(2 * lat_rad)
        + M3 * math.sin(4 * lat_rad)
        - M4 * math.sin(6 * lat_rad)
    )
    easting = (
        K0
        * n
        * (
            a
            + a**3 * (1 - t + c) / 6
            + a**5 * (5 - 18 * t + t**2 + 72 * c - 58 * E_P2) / 120
        )
        + 500000.0
    )
    northing = K0 * (
        m
        + n
        * math.tan(lat_rad)
        * (
            a**2 / 2
            + a**4 * (5 - t + 9 * c + 4 * c**2) / 24
            + a**6 * (61 - 58 * t + t**2 + 600 * c - 330 * E_P2) / 720
        )
    )
    if lat < 0:
        northing += 10_000_000.0
    return easting, northing


def utm_to_latlon(easting: float, northing: float, zone: int = UTM_ZONE) -> tuple[float, float]:
    x = easting - 500000.0
    y = northing - 10_000_000.0
    m = y / K0
    mu = m / (R * M1)
    p_rad = (
        mu
        + (3 * E1 / 2 - 27 * E1**3 / 32) * math.sin(2 * mu)
        + (21 * E1**2 / 16 - 55 * E1**4 / 32) * math.sin(4 * mu)
        + (151 * E1**3 / 96) * math.sin(6 * mu)
    )
    p_tan = math.tan(p_rad)
    p_cos = math.cos(p_rad)
    ep_sin = 1 - E * math.sin(p_rad) ** 2
    n = R / math.sqrt(ep_sin)
    r = (1 - E) / ep_sin
    c = E_P2 * p_cos**2
    d = x / (n * K0)
    lat = p_rad - (p_tan / r) * (
        d**2 / 2
        - d**4 / 24 * (5 + 3 * p_tan**2 + 10 * c - 4 * c**2 - 9 * E_P2)
        + d**6 / 720 * (61 + 90 * p_tan**2 + 298 * c + 45 * p_tan**4 - 252 * E_P2 - 3 * c**2)
    )
    lon = (
        d
        - d**3 / 6 * (1 + 2 * p_tan**2 + c)
        + d**5 / 120 * (5 - 2 * c + 28 * p_tan**2 - 3 * c**2 + 8 * E_P2 + 24 * p_tan**4)
    ) / p_cos
    lon0 = (zone - 1) * 6 - 180 + 3
    return math.degrees(lat), math.degrees(lon) + lon0


def parse_latlon(text: str) -> tuple[float, float]:
    a, b = text.split(",")
    return float(a.strip()), float(b.strip())


def latex_miles(x: float, decimals: int = 2) -> str:
    sign = "-" if x < 0 else ""
    n = abs(x)
    s = f"{n:.{decimals}f}"
    entero, frac = s.split(".")
    grupos = []
    while entero:
        grupos.append(entero[-3:])
        entero = entero[:-3]
    entero = " ".join(reversed(grupos))
    return f"{sign}{entero}{{,}}{frac}"


def latex_coord(x: float, decimals: int = 6) -> str:
    sign = "-" if x < 0 else ""
    s = f"{abs(x):.{decimals}f}".replace(".", "{,}")
    return f"${sign}{s}$"


def fmt_m(x: float) -> str:
    """1000.0 → '1 000,00'  |  100.0 → '100,00'"""
    return latex_miles(x, 2).replace("{,}", ",")


def compute(p1: tuple[float, float], p2_google: tuple[float, float], frente: float, fondo: float) -> dict:
    e1, n1 = latlon_to_utm(*p1)
    e2g, n2g = latlon_to_utm(*p2_google)
    dx, dy = e2g - e1, n2g - n1
    dist_google = math.hypot(dx, dy)
    ux, uy = dx / dist_google, dy / dist_google
    ix, iy = uy, -ux  # izquierda del rumbo este (Mazuco → Puerto Maldonado)

    e2, n2 = e1 + ux * frente, n1 + uy * frente
    e4, n4 = e1 + ix * fondo, n1 + iy * fondo
    e3, n3 = e2 + ix * fondo, n2 + iy * fondo

    # Publicar P1 redondeado a cm; el resto sobre ese origen.
    e1, n1 = round(e1, 2), round(n1, 2)
    e2, n2 = round(e1 + ux * frente, 2), round(n1 + uy * frente, 2)
    e4, n4 = round(e1 + ix * fondo, 2), round(n1 + iy * fondo, 2)
    e3, n3 = round(e2 + ix * fondo, 2), round(n2 + iy * fondo, 2)

    def ll(e, n):
        lat, lon = utm_to_latlon(e, n)
        return round(lat, 6), round(lon, 6)

    lat1, lon1 = p1  # P1 se publica tal cual el pin Google
    lat2, lon2 = ll(e2, n2)
    lat3, lon3 = ll(e3, n3)
    lat4, lon4 = ll(e4, n4)

    az_frente = (math.degrees(math.atan2(-ux, -uy)) + 360) % 360
    perimetro = 2 * (frente + fondo)
    area = frente * fondo

    # Puente ~350 m al oeste de P2, sobre el rumbo de la vía.
    pe, pn = e2 + ux * 350.0, n2 + uy * 350.0
    plat, plon = utm_to_latlon(pe, pn)

    return {
        "p1": {"lat": lat1, "lon": lon1, "e": e1, "n": n1, "rol": "Frente este (dato fijo)"},
        "p2": {"lat": lat2, "lon": lon2, "e": e2, "n": n2, "rol": "Frente oeste (ajustado)"},
        "p3": {"lat": lat3, "lon": lon3, "e": e3, "n": n3, "rol": "Fondo oeste (calculado)"},
        "p4": {"lat": lat4, "lon": lon4, "e": e4, "n": n4, "rol": "Fondo este (calculado)"},
        "frente": frente,
        "fondo": fondo,
        "perimetro": perimetro,
        "area": area,
        "area_ha": area / 10_000.0,
        "azimut": az_frente,
        "dist_google": dist_google,
        "ux": ux,
        "uy": uy,
        "ix": ix,
        "iy": iy,
        "puente": {"e": pe, "n": pn, "lat": plat, "lon": plon},
        "p1_google": p1,
        "p2_google": p2_google,
    }


GENERATED_BEGIN = "% --- PREDIO A INDEPENDIZAR (inicio generado por actualizar_poligono.py) ---"
GENERATED_END = "% --- PREDIO A INDEPENDIZAR (fin generado) ---"


def datos_block(g: dict) -> str:
    p1, p2, p3, p4 = g["p1"], g["p2"], g["p3"], g["p4"]
    ha = g["area_ha"]
    metros = g["area"]
    return f"""{GENERATED_BEGIN}
% No editar a mano. Recalcular:
%   uv run --with matplotlib actualizar_poligono.py
% P1 fijo. P2 sobre el rumbo Google a {fmt_m(g['frente'])} m.
% P3 y P4 a {fmt_m(g['fondo'])} m al norte (izquierda, Mazuco → Puerto Maldonado).
\\newcommand{{\\AreaIndependizarHa}}{{{latex_miles(ha)}}}
\\newcommand{{\\AreaIndependizarMetros}}{{{latex_miles(metros)}}}
\\newcommand{{\\PerimetroM}}{{{latex_miles(g['perimetro'])}}}
\\newcommand{{\\FrenteM}}{{{latex_miles(g['frente'])}}}
\\newcommand{{\\FondoM}}{{{latex_miles(g['fondo'])}}}
\\newcommand{{\\AzimutFrente}}{{{latex_miles(g['azimut'])}}}
\\newcommand{{\\DistanciaPinGoogle}}{{{latex_miles(g['dist_google'])}}}

\\newcommand{{\\PUnoLat}}{{{latex_coord(p1['lat'])}}}
\\newcommand{{\\PUnoLon}}{{{latex_coord(p1['lon'])}}}
\\newcommand{{\\PDosLat}}{{{latex_coord(p2['lat'])}}}
\\newcommand{{\\PDosLon}}{{{latex_coord(p2['lon'])}}}
\\newcommand{{\\PTresLat}}{{{latex_coord(p3['lat'])}}}
\\newcommand{{\\PTresLon}}{{{latex_coord(p3['lon'])}}}
\\newcommand{{\\PCuatroLat}}{{{latex_coord(p4['lat'])}}}
\\newcommand{{\\PCuatroLon}}{{{latex_coord(p4['lon'])}}}

\\newcommand{{\\PUnoE}}{{{latex_miles(p1['e'])}}}
\\newcommand{{\\PUnoN}}{{{latex_miles(p1['n'])}}}
\\newcommand{{\\PDosE}}{{{latex_miles(p2['e'])}}}
\\newcommand{{\\PDosN}}{{{latex_miles(p2['n'])}}}
\\newcommand{{\\PTresE}}{{{latex_miles(p3['e'])}}}
\\newcommand{{\\PTresN}}{{{latex_miles(p3['n'])}}}
\\newcommand{{\\PCuatroE}}{{{latex_miles(p4['e'])}}}
\\newcommand{{\\PCuatroN}}{{{latex_miles(p4['n'])}}}
{GENERATED_END}
"""


def patch_datos(g: dict) -> None:
    text = DATOS.read_text(encoding="utf-8")
    block = datos_block(g)
    if GENERATED_BEGIN in text and GENERATED_END in text:
        text = re.sub(
            re.escape(GENERATED_BEGIN) + r".*?" + re.escape(GENERATED_END),
            lambda _m: block.strip(),
            text,
            count=1,
            flags=re.S,
        )
    else:
        old = r"% --- PREDIO A INDEPENDIZAR --------------------------------------------------.*?(?=\n\\newcommand\{\\FechaPago\})"
        if not re.search(old, text, flags=re.S):
            sys.exit("No encuentro el bloque PREDIO A INDEPENDIZAR en datos.tex")
        text = re.sub(old, lambda _m: block.strip() + "\n\n", text, count=1, flags=re.S)
    DATOS.write_text(text, encoding="utf-8")



def _m_entero(x: float) -> str:
    n = int(round(x))
    s = f"{n:,}".replace(",", " ")
    return f"{s} m"



def render_png(g: dict) -> None:
    """Esquema: matriz 100 ha; franja de 10 ha adosada al lindero oeste (100 m de frente)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    import matplotlib.patheffects as pe

    frente = g["frente"]
    fondo = g["fondo"]
    # Misma profundidad que el recorte → frente de la matriz = 10 × 100 m = 1 000 m (100 ha).
    matriz_frente = 10.0 * frente
    tinta = "#1B2A4A"
    rojo = "#C0392B"
    relleno = "#D6EAF8"
    remanente = "#E8E4D4"
    via = "#F4D03F"
    via_borde = "#B7950B"
    rio = "#5DADE2"
    papel = "#F7F3E8"
    grid = "#C5BBA8"
    halo = [pe.withStroke(linewidth=3.0, foreground=papel)]

    fig, ax = plt.subplots(figsize=(15.2, 6.2), dpi=170, facecolor=papel)
    ax.set_facecolor(papel)

    x0, x1 = -380, matriz_frente + 90
    y0, y1 = -150, fondo + 120
    for x in range(0, int(matriz_frente) + 1, 200):
        ax.axvline(x, color=grid, lw=0.4, ls=(0, (4, 4)), zorder=1)
    for y in range(0, int(fondo) + 1, 200):
        ax.axhline(y, color=grid, lw=0.4, ls=(0, (4, 4)), zorder=1)

    puente_x, puente_y = -220.0, 0.0
    rio_x, rio_y = [], []
    for i in range(41):
        t = i / 40
        rio_x.append(puente_x + 12 * math.sin(t * math.pi * 2.0))
        rio_y.append(-40 + t * 280.0)
    ax.plot(rio_x, rio_y, color=rio, lw=7.2, solid_capstyle="round", zorder=3, alpha=0.92)
    ax.plot(rio_x, rio_y, color="#2E86C1", lw=2.2, solid_capstyle="round", zorder=3)

    half = 14.0
    ax.add_patch(Rectangle((x0, -half), x1 - x0, 2 * half,
                           facecolor=via, edgecolor=via_borde, lw=1.0, zorder=4))
    ax.plot([x0, x1], [0, 0], color=via_borde, lw=0.7, ls=(0, (7, 4)), zorder=5)

    ax.add_patch(Rectangle((0, 0), matriz_frente, fondo,
                           facecolor=remanente, edgecolor="#7D6E57", lw=1.6, zorder=5, alpha=0.95))
    ax.add_patch(Rectangle((0, 0), frente, fondo,
                           facecolor=relleno, edgecolor=rojo, lw=2.25, zorder=6, alpha=0.95))
    ax.plot([0, 0], [0, fondo], color="#1A5276", lw=3.0, zorder=7)

    ax.text(frente / 2, fondo / 2, "LOTE A\n10 ha",
            ha="center", va="center", fontsize=12, color="#1A5276", fontweight="bold",
            zorder=8, path_effects=halo)
    ax.text(frente + (matriz_frente - frente) / 2, fondo * 0.72, "REMANENTE  90 ha",
            ha="center", va="center", fontsize=12, color="#5D4E37", fontweight="bold",
            zorder=8, path_effects=halo)
    ax.text(frente / 2, -36, f"{_m_entero(frente)}  (frente)",
            ha="center", va="center", fontsize=10, color=rojo, fontweight="bold",
            zorder=9, path_effects=halo)
    ax.text(-48, fondo / 2, "lindero oeste\nde la matriz",
            ha="center", va="center", fontsize=9, color="#1A5276", fontweight="bold",
            rotation=90, zorder=9, path_effects=halo)
    ax.text(matriz_frente / 2, fondo + 36, "predio matriz  100 ha  (esquema)",
            ha="center", va="center", fontsize=10, color="#5D4E37", fontweight="bold",
            zorder=9, path_effects=halo)

    pts = {
        "P2": ((0, 0), "frente oeste\n= lindero oeste", "right", -10, -28),
        "P1": ((frente, 0), "frente este\n(100 m)", "left", 10, -28),
        "P3": ((0, fondo), "fondo oeste", "right", -10, 16),
        "P4": ((frente, fondo), "fondo este", "left", 10, 16),
    }
    for key, (xy, rol, ha, dx, dy) in pts.items():
        ax.scatter([xy[0]], [xy[1]], s=62, c="#F4D03F", edgecolors=tinta, linewidths=1.15, zorder=10)
        ax.annotate(f"{key}  {rol}", xy, xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.2, color=tinta, ha=ha, va="center", zorder=11, path_effects=halo)

    ax.plot(puente_x, puente_y, marker="v", markersize=15, color=rojo, zorder=12,
            markeredgecolor="#6B1111", markeredgewidth=0.5)
    ax.annotate("PUENTE JAYAVE", (puente_x, puente_y), xytext=(-8, 24),
                textcoords="offset points", ha="right", fontsize=9.5, color=rojo,
                fontweight="bold", zorder=13, path_effects=halo)

    ax.text(-300, 40, "←  Mazuco", ha="center", fontsize=10, color=tinta,
            fontweight="bold", zorder=8, path_effects=halo)
    ax.text(matriz_frente + 20, 40, "Puerto Maldonado  →", ha="left", fontsize=10, color=tinta,
            fontweight="bold", zorder=8, path_effects=halo)
    ax.text(matriz_frente / 2, -88, "Interoceánica Sur  (PE-30C)  —  margen norte",
            ha="center", fontsize=9.5, color="#7D6608", fontweight="bold",
            zorder=8, path_effects=halo)

    nx0, ny0 = matriz_frente - 40, fondo * 0.78
    ax.annotate("", xy=(nx0, ny0 + 80), xytext=(nx0, ny0),
                arrowprops=dict(arrowstyle="-|>", color=tinta, lw=1.7, mutation_scale=15), zorder=12)
    ax.text(nx0, ny0 + 96, "N", fontsize=13, fontweight="bold", color=tinta, ha="center")

    # Leyenda dentro del remanente, sobre la vía (no tapa el pie del esquema).
    leg = ax.inset_axes([0.54, 0.28, 0.43, 0.32])
    leg.set_xlim(0, 1)
    leg.set_ylim(0, 1)
    leg.axis("off")
    leg.add_patch(FancyBboxPatch((0.02, 0.06), 0.96, 0.88, boxstyle="round,pad=0.03",
                                 facecolor="#FFFdf6", edgecolor="#A69070", lw=0.8))
    leg.text(0.08, 0.82, "Leyenda (esquema, sin escala)", fontsize=8.8, fontweight="bold", color=tinta)
    leg.add_patch(Rectangle((0.08, 0.58), 0.12, 0.12, facecolor=relleno, edgecolor=rojo, lw=1.2))
    leg.text(0.24, 0.64, "10 ha  (LOTE A)", fontsize=8.2, va="center", color=tinta)
    leg.add_patch(Rectangle((0.08, 0.38), 0.12, 0.12, facecolor=remanente, edgecolor="#7D6E57", lw=1.0))
    leg.text(0.24, 0.44, "90 ha  remanente", fontsize=8.2, va="center", color=tinta)
    leg.plot([0.08, 0.20], [0.24, 0.24], color="#1A5276", lw=2.6)
    leg.text(0.24, 0.24, "lindero oeste de las 100 ha", fontsize=8.2, va="center", color=tinta)
    leg.plot(0.14, 0.10, marker="v", markersize=8, color=rojo)
    leg.text(0.24, 0.10, "Puente Jayave (fuera del lote)", fontsize=8.2, va="center", color=tinta)

    ax.set_aspect(0.38)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.axis("off")
    fig.suptitle("Predio 10 ha  —  Inambari, Madre de Dios", fontsize=16, fontweight="bold", color=tinta, y=0.978)
    ax.set_title(
        "Franja de 100 m de frente × 1 000 m de fondo, pegada al oeste de la matriz. El campo sigue el lindero real.",
        fontsize=9.2, color="#5D5648", pad=6,
    )
    fig.tight_layout(rect=(0.01, 0.01, 0.99, 0.96))
    fig.savefig(PNG, dpi=170, facecolor=papel)
    plt.close(fig)



def main() -> None:
    ap = argparse.ArgumentParser(description="Recalcula el polígono y redibuja DOC-08 / DOC-11.")
    ap.add_argument("--p1", default="-12.912452,-70.170058", help="lat,lon de P1 (queda fijo)")
    ap.add_argument("--p2", default="-12.912497,-70.170981", help="lat,lon Google de P2 (solo rumbo)")
    ap.add_argument("--frente", type=float, default=100.0, help="P1–P2 en metros")
    ap.add_argument("--fondo", type=float, default=1000.0, help="profundidad en metros")
    ap.add_argument("--solo-imagen", action="store_true")
    ap.add_argument("--no-imagen", action="store_true")
    args = ap.parse_args()

    g = compute(parse_latlon(args.p1), parse_latlon(args.p2), args.frente, args.fondo)
    print("P1 fijo   ", g["p1"])
    print("P2 ajust. ", g["p2"], f"  (Google estaba a {g['dist_google']:.2f} m)")
    print("P3        ", g["p3"])
    print("P4        ", g["p4"])
    print(f"Lados {g['frente']:.2f} / {g['fondo']:.2f} / {g['frente']:.2f} / {g['fondo']:.2f} m")
    print(f"Área {g['area']:.2f} m² = {g['area_ha']:.2f} ha   perímetro {g['perimetro']:.2f} m")
    print(f"Azimut de frente (hacia P. Maldonado) {g['azimut']:.2f}°")

    if not args.solo_imagen:
        patch_datos(g)
        print(f"Actualizado {DATOS}")

    if not args.no_imagen:
        render_png(g)
        print(f"Renderizado {PNG}")


if __name__ == "__main__":
    main()
