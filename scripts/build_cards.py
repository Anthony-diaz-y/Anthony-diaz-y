"""Genera los SVG del perfil: banner, tarjetas de proyectos y línea de tiempo.

Uso:  python scripts/build_cards.py
Salida: assets/banner.svg, assets/card-*.svg, assets/timeline.svg

Reglas:
- Paleta sobria (grises de GitHub) y un único acento verde para "en vivo / hoy".
- Nada de fade-in: renders estáticos lo dejarían invisible. Sólo animaciones
  cuyo estado por defecto sea visible (parpadeo, pulso).
- GitHub cachea imágenes: si un cambio no aparece, renombra el archivo.
"""
import math
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "'Segoe UI',Inter,-apple-system,Helvetica,Arial,sans-serif"
MONO = "'Cascadia Code',Consolas,'SFMono-Regular',Menlo,monospace"

BG, SURF, BORDER, LINE = "#0d1117", "#161b22", "#30363d", "#21262d"
TXT, SOFT, MUTED, DIM, FAINT = "#e6edf3", "#c9d1d9", "#8b949e", "#6e7681", "#484f58"
ACCENT = "#3fb950"

BASE_CSS = f"""
      .h{{font:600 22px {SANS};fill:{TXT};letter-spacing:-0.3px}}
      .p{{font:400 13px {SANS};fill:{MUTED}}}
      .m{{font:400 11px {MONO};fill:{DIM}}}
      .ms{{font:500 11px {MONO};fill:{SOFT}}}
      .lbl{{font:500 11px {MONO};fill:{SOFT}}}
      .pulse{{animation:pulse 2.4s ease-in-out infinite}}
      @keyframes pulse{{50%{{opacity:.3}}}}"""


def frame(w: int, h: int, body: str, css: str = "", label: str = "") -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  <style>{BASE_CSS}{css}
  </style>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
{body}
</svg>
"""


# ─────────────────────────── Mapache pixel art ───────────────────────────
# G gris · D gris oscuro · W claro · K máscara · S borde laptop · L tapa · A luz
RACCOON = [
    "..GG........GG......",
    ".GDDG......GDDG.....",
    ".GDGGGGGGGGGGDG.....",
    "GGGGGGGGGGGGGGGG....",
    "GWWWWGGGGGGWWWWG....",
    "KKKKWWGGGGWWKKKK....",
    "KKWKKWWWWWWKKWKK....",
    "GKKKKWWWWWWKKKKG....",
    ".GWWWWWKKWWWWWG.....",
    "..GWWWWWWWWWWG...K..",
    "..GGGGGGGGGGGG..KKK.",
    ".GGSSSSSSSSSSGG.GGG.",
    "..SLLLLLLLLLLS..KKK.",
    "..SLLLLLAALLLS.GGG..",
    "..SLLLLLLLLLLS.KK...",
    ".SSSSSSSSSSSSSSGG...",
]
PIX = {"G": MUTED, "D": FAINT, "W": TXT, "K": "#010409", "S": DIM, "L": BORDER, "A": ACCENT}


def raccoon(x: float, y: float, px: int = 3) -> str:
    rects = []
    for r, row in enumerate(RACCOON):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            run = c
            while run < len(row) and row[run] == ch:
                run += 1
            rects.append(f'<rect x="{x + c * px:.1f}" y="{y + r * px}" width="{(run - c) * px}" height="{px}" fill="{PIX[ch]}"/>')
            c = run
    # parpadeo: tapa los brillos de los ojos un instante (por defecto invisible)
    blink = "".join(
        f'<rect class="blink" x="{x + cx * px:.1f}" y="{y + 6 * px}" width="{px}" height="{px}" fill="#010409"/>'
        for cx in (2, 13)
    )
    return f'<g shape-rendering="crispEdges">{"".join(rects)}{blink}</g>'


RACCOON_CSS = """
      .blink{opacity:0;animation:blink 4s steps(1) infinite}
      @keyframes blink{0%,92%{opacity:0}93%,96%{opacity:1}97%{opacity:0}}"""


# ───────────────────────────── Proyectos ─────────────────────────────

def arrow(x1, y, x2):
    return (f'<line x1="{x1:.1f}" y1="{y}" x2="{x2 - 5:.1f}" y2="{y}" stroke="{FAINT}" stroke-width="1.5"/>'
            f'<path d="M{x2 - 6:.1f} {y - 4}L{x2:.1f} {y}L{x2 - 6:.1f} {y + 4}" fill="none" stroke="{FAINT}" stroke-width="1.5"/>')


def box(x, y, w, h, label, strong=False):
    return (f'<rect x="{x:.1f}" y="{y}" width="{w}" height="{h}" rx="6" fill="{SURF}" stroke="{SOFT if strong else BORDER}"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + h / 2 + 4}" text-anchor="middle" class="lbl">{esc(label)}</text>')


def chart_cra(x0, y0, w):
    """Pipeline SBOM → reporte + plazos regulatorios."""
    bw = 90
    gap = (w - 4 * bw) / 3
    out = []
    for i, n in enumerate(["SBOM", "OSV · KEV", "Triage", "Reporte"]):
        bx = x0 + i * (bw + gap)
        out.append(box(bx, y0 + 6, bw, 32, n, strong=i == 3))
        if i < 3:
            out.append(arrow(bx + bw + 4, y0 + 22, bx + bw + gap - 4))
    ty = y0 + 82
    out.append(f'<text x="{x0}" y="{ty - 12}" class="m">plazos de reporte</text>')
    out.append(f'<rect x="{x0}" y="{ty}" width="{w}" height="4" rx="2" fill="{LINE}"/>')
    out.append(f'<rect x="{x0}" y="{ty}" width="{w * 0.18:.1f}" height="4" rx="2" fill="{SOFT}"/>')
    for frac, t in ((0.18, "24h"), (0.42, "72h"), (1.0, "14d")):
        tx = x0 + w * frac - (4 if frac == 1 else 0)
        out.append(f'<circle cx="{tx:.1f}" cy="{ty + 2}" r="4" fill="{BG}" stroke="{SOFT if frac < 0.2 else MUTED}" stroke-width="1.5"/>')
        out.append(f'<text x="{tx + (4 if frac == 1 else 0):.1f}" y="{ty + 22}" text-anchor="{"end" if frac == 1 else "middle"}" class="m">{t}</text>')
    return "".join(out)


def chart_vigia(x0, y0, w):
    """Serie observada + pronóstico con banda de incertidumbre (forma ilustrativa)."""
    h, n, split = 96, 40, 27

    def val(i):
        return 0.42 + 0.26 * math.sin(i / 4.2) + 0.1 * math.sin(i / 1.7 + 1) + 0.12 * math.exp(-((i - 20) / 5) ** 2)

    pts = [(x0 + w * i / (n - 1), y0 + h - h * val(i)) for i in range(n)]
    fmt = lambda ps: " ".join(f"{px:.1f},{py:.1f}" for px, py in ps)
    up = [(px, py - 4 - (i - split) * 1.6) for i, (px, py) in enumerate(pts) if i >= split]
    dn = [(px, py + 4 + (i - split) * 1.6) for i, (px, py) in enumerate(pts) if i >= split]
    sx, sy = pts[split]
    return (
        f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{LINE}"/>'
        f'<polygon points="{fmt(up + dn[::-1])}" fill="{FAINT}" fill-opacity="0.35"/>'
        f'<polyline points="{fmt(pts[: split + 1])}" fill="none" stroke="{SOFT}" stroke-width="2" stroke-linejoin="round"/>'
        f'<polyline points="{fmt(pts[split:])}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4 4"/>'
        f'<line x1="{sx:.1f}" y1="{y0 - 6}" x2="{sx:.1f}" y2="{y0 + h}" stroke="{BORDER}" stroke-dasharray="2 3"/>'
        f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.5" fill="{BG}" stroke="{SOFT}" stroke-width="1.5"/>'
        f'<text x="{sx - 8:.1f}" y="{y0 + 2}" text-anchor="end" class="m">observado</text>'
        f'<text x="{sx + 8:.1f}" y="{y0 + 2}" class="m">pronóstico</text>'
    )


def chart_inkari(x0, y0, w):
    """Flujo de un pedido, del carrito al envío."""
    cy = y0 + 36
    out = [f'<line x1="{x0 + 12}" y1="{cy}" x2="{x0 + w - 12}" y2="{cy}" stroke="{BORDER}" stroke-width="2"/>']
    for i, s in enumerate(["carrito", "pago", "preparación", "envío"]):
        cx = x0 + 12 + (w - 24) * i / 3
        col = ACCENT if i == 3 else SOFT
        out.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="9" fill="{BG}" stroke="{col}" stroke-width="2"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="3.5" fill="{col}"/>')
        anchor = "start" if i == 0 else "end" if i == 3 else "middle"
        tx = cx - 9 if i == 0 else cx + 9 if i == 3 else cx
        out.append(f'<text x="{tx:.1f}" y="{cy + 30}" text-anchor="{anchor}" class="lbl">{s}</text>')
    out.append(f'<text x="{x0}" y="{y0 + 100}" class="m">+ panel admin · alertas operativas</text>')
    return "".join(out)


def chart_cem(x0, y0, w):
    """Módulos por dominio alrededor de un núcleo."""
    cw, ch, nw, nh = 96, 32, 100, 28
    cx, cy = x0 + w / 2 - cw / 2, y0 + 34
    left, right = x0, x0 + w - nw
    nodes = [(left, y0 + 6, "auth"), (left, y0 + 68, "cursos"), (right, y0 + 6, "admin"), (right, y0 + 68, "instructor")]
    out = []
    for nx, ny, _ in nodes:
        sx = nx + nw if nx == left else nx
        ex = cx if nx == left else cx + cw
        mx = (sx + ex) / 2
        out.append(f'<path d="M{sx:.1f} {ny + nh / 2}C{mx:.1f} {ny + nh / 2} {mx:.1f} {cy + ch / 2} {ex:.1f} {cy + ch / 2}" fill="none" stroke="{FAINT}" stroke-width="1.5"/>')
    for nx, ny, label in nodes:
        out.append(box(nx, ny, nw, nh, label))
    out.append(box(cx, cy, cw, ch, "core", strong=True))
    return "".join(out)


PROJECTS = [
    {"file": "cra-desk", "title": "CRA Desk", "live": False, "status": "en desarrollo",
     "tag": "Cumplimiento del EU Cyber Resilience Act para fabricantes IoT.",
     "chart": chart_cra, "stack": "spring boot · go · next.js · postgres", "metric": "300+ tests"},
    {"file": "vigia", "title": "Vigía", "live": False, "status": "en desarrollo",
     "tag": "Pronóstico de vigilancia epidemiológica del Perú.",
     "chart": chart_vigia, "stack": "nestjs · next.js · typeorm · postgres", "metric": "monorepo ts"},
    {"file": "inkari", "title": "Inkari Café", "live": True, "status": "en producción",
     "tag": "E-commerce de café con panel administrativo.",
     "chart": chart_inkari, "stack": "next.js · express · tailwind · postgres", "metric": "inkari.shop"},
    {"file": "cem", "title": "CEM eLearning", "live": True, "status": "demo",
     "tag": "Plataforma de cursos con arquitectura modular.",
     "chart": chart_cem, "stack": "next.js · react · redux · typescript", "metric": "4 dominios"},
]


def project_svg(p: dict) -> str:
    W, H, PAD = 480, 270, 24
    col = ACCENT if p["live"] else MUTED
    dot = (f'<circle class="pulse" cx="{W - PAD - 4}" cy="42" r="3.5" fill="{col}"/>' if p["live"]
           else f'<circle cx="{W - PAD - 4}" cy="42" r="3.5" fill="none" stroke="{col}" stroke-width="1.5"/>')
    body = f"""
  <text x="{PAD}" y="48" class="h">{esc(p['title'])}</text>
  {dot}
  <text x="{W - PAD - 14}" y="46" text-anchor="end" class="m">{esc(p['status'])}</text>
  <text x="{PAD}" y="72" class="p">{esc(p['tag'])}</text>
  <g>{p['chart'](PAD, 104, W - 2 * PAD)}</g>
  <line x1="{PAD}" y1="226" x2="{W - PAD}" y2="226" stroke="{LINE}"/>
  <text x="{PAD}" y="249" class="m">{esc(p['stack'])}</text>
  <text x="{W - PAD}" y="249" text-anchor="end" class="ms">{esc(p['metric'])}</text>"""
    return frame(W, H, body, label=f"{p['title']} — {p['tag']}")


# ───────────────────────────── Experiencia ─────────────────────────────

def mo(year, month):
    """Meses desde enero de 2024."""
    return (year - 2024) * 12 + (month - 1)


TODAY = mo(2026, 11) + 0.7
ROLES = [  # (empresa, rol, inicio, fin)
    ("Grupo CORIL", "Gestión de Patrimonios", mo(2026, 8), TODAY),
    ("", "Abonos Bancarios", mo(2026, 6), mo(2026, 8)),
    ("", "Gestión de Emisiones", mo(2026, 4), mo(2026, 6)),
    ("", "Intranet corporativa", mo(2026, 1), mo(2026, 4)),
    ("CEM eLearning", "Full stack", mo(2025, 12), mo(2026, 4)),
    ("Comparapet", "Base de datos", mo(2025, 10), mo(2025, 12)),
    ("OpenLab", "Pasantía full stack", mo(2024, 2), mo(2025, 12)),
]


def timeline_svg() -> str:
    W, PAD = 900, 32
    X0, X1 = 340, 868
    pm = (X1 - X0) / 36
    top, rh = 104, 34
    X = lambda m: X0 + m * pm
    bottom = top + rh * len(ROLES)
    out = [f'<text x="{PAD}" y="40" class="m">experiencia · 2024 → hoy</text>']

    for q in range(0, 37, 3):  # rejilla: años y trimestres
        x = X(q)
        major = q % 12 == 0
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bottom}" stroke="{BORDER if major else LINE}"/>')
        if major and q < 36:
            out.append(f'<text x="{x + 6:.1f}" y="{bottom + 20}" class="m">{2024 + q // 12}</text>')

    for i, (co, role, s, e) in enumerate(ROLES):
        y = top + i * rh
        if co:
            if i:
                out.append(f'<line x1="{PAD}" y1="{y}" x2="{X0 - 16}" y2="{y}" stroke="{LINE}"/>')
            out.append(f'<text x="{PAD}" y="{y + 22}" font-family="{SANS}" font-size="13.5" font-weight="600" fill="{TXT}">{esc(co)}</text>')
        out.append(f'<text x="{PAD + 132}" y="{y + 22}" class="p">{esc(role)}</text>')
        current = e == TODAY
        out.append(f'<rect x="{X(s):.1f}" y="{y + 11}" width="{max(X(e) - X(s), 6):.1f}" height="12" rx="6" fill="{SOFT if current else BORDER}"/>')
        if current:
            out.append(f'<circle class="pulse" cx="{X(e):.1f}" cy="{y + 17}" r="4" fill="{ACCENT}"/>')

    hx = X(TODAY)
    out.append(f'<line x1="{hx:.1f}" y1="{top - 8}" x2="{hx:.1f}" y2="{bottom}" stroke="{ACCENT}" stroke-opacity="0.6" stroke-dasharray="3 3"/>')
    out.append(f'<text x="{hx:.1f}" y="{bottom + 20}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ACCENT}">hoy</text>')
    out.append(raccoon(hx - 25, top - 8 - len(RACCOON) * 3))  # sentado sobre "hoy"

    ey = bottom + 62
    out.append(f'<line x1="{PAD}" y1="{ey - 24}" x2="{W - PAD}" y2="{ey - 24}" stroke="{LINE}"/>')
    out.append(f'<text x="{PAD}" y="{ey}" class="m">formación</text>')
    out.append(f'<text x="{PAD + 132}" y="{ey}" class="p"><tspan fill="{SOFT}">Ingeniería Industrial</tspan> · UPN'
               f'<tspan dx="18" fill="{SOFT}">Gestión de Sistemas de Información</tspan> · Zegel</text>')
    return frame(W, ey + 28, "".join(out), css=RACCOON_CSS, label="Línea de tiempo de experiencia profesional")


# ───────────────────────────── Banner ─────────────────────────────

def banner_svg() -> str:
    W, H = 1200, 260
    k, s, c = MUTED, SOFT, "#a5b1bd"
    code = [
        (24, 64, f'<tspan fill="{k}">const</tspan><tspan fill="{TXT}"> anthony = {{</tspan>'),
        (44, 90, f'<tspan fill="{s}">stack</tspan><tspan fill="{DIM}">: [</tspan><tspan fill="{c}">"Next.js"</tspan><tspan fill="{DIM}">, </tspan><tspan fill="{c}">"NestJS"</tspan><tspan fill="{DIM}">],</tspan>'),
        (44, 116, f'<tspan fill="{s}">data</tspan><tspan fill="{DIM}">: </tspan><tspan fill="{c}">"PostgreSQL"</tspan><tspan fill="{DIM}">,</tspan>'),
        (44, 142, f'<tspan fill="{s}">learning</tspan><tspan fill="{DIM}">: [</tspan><tspan fill="{c}">"Java"</tspan><tspan fill="{DIM}">, </tspan><tspan fill="{c}">"Go"</tspan><tspan fill="{DIM}">],</tspan>'),
        (24, 166, f'<tspan fill="{TXT}">}};</tspan><tspan class="cursor" fill="{ACCENT}"> ▍</tspan>'),
    ]
    lines = "".join(f'<text x="{x}" y="{y}" class="code">{t}</text>' for x, y, t in code)
    body = f"""
  <text x="64" y="92" font-family="{MONO}" font-size="14" letter-spacing="3" fill="{DIM}">FULL STACK DEVELOPER</text>
  <text x="62" y="154" font-family="{SANS}" font-size="56" font-weight="700" letter-spacing="-1.2" fill="{TXT}">Anthony Díaz</text>
  <text x="64" y="194" font-family="{SANS}" font-size="18" fill="{MUTED}">Del modelo de datos a una interfaz clara · Lima, Perú</text>
  <g transform="translate(772 35)">
    <rect width="372" height="190" rx="10" fill="{SURF}" stroke="{BORDER}"/>
    <circle cx="22" cy="22" r="5" fill="{BORDER}"/><circle cx="40" cy="22" r="5" fill="{BORDER}"/><circle cx="58" cy="22" r="5" fill="{BORDER}"/>
    {lines}
  </g>"""
    css = f"""
      .code{{font:400 14.5px {MONO}}}
      .cursor{{animation:blink 1.1s steps(1) infinite}}
      @keyframes blink{{50%{{opacity:0}}}}"""
    return frame(W, H, body, css=css, label="Anthony Díaz — Full Stack Developer")


def main() -> None:
    for p in PROJECTS:
        (ASSETS / f"card-{p['file']}.svg").write_text(project_svg(p), encoding="utf-8")
    (ASSETS / "timeline.svg").write_text(timeline_svg(), encoding="utf-8")
    (ASSETS / "banner.svg").write_text(banner_svg(), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
