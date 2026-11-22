"""Genera las tarjetas SVG de proyectos y la línea de tiempo de experiencia.

Uso:  python scripts/build_cards.py
Salida: assets/projects/*.svg y assets/experience.svg

GitHub no permite CSS en el README, así que el diseño vive en SVG.
Nota: animar sólo opacity (no transform) y renombrar archivos si GitHub cachea.
"""
from pathlib import Path
from xml.sax.saxutils import escape as esc

ROOT = Path(__file__).resolve().parent.parent
SANS = "'Segoe UI',Inter,-apple-system,Helvetica,Arial,sans-serif"
MONO = "'Cascadia Code',Consolas,'SFMono-Regular',Menlo,monospace"


def mono_w(text: str, size: float) -> float:
    return len(text) * size * 0.6


def common_defs(accent: str, w: int, h: int) -> str:
    return f"""
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1020"/><stop offset="0.6" stop-color="#111a33"/><stop offset="1" stop-color="#0d1326"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.95" cy="0" r="0.75">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M24 0H0V24" fill="none" stroke="#fff" stroke-opacity="0.035"/>
    </pattern>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="16"/></clipPath>"""


# ───────────────────────────── Proyectos ─────────────────────────────

PROJECTS = [
    {
        "file": "cra-desk", "idx": "01", "kind": "SAAS · COMPLIANCE",
        "title": "CRA Desk", "accent": "#7c9cff",
        "status": ("EN DESARROLLO", "#7c9cff"),
        "desc": [
            "Cumplimiento del EU Cyber Resilience Act para",
            "fabricantes IoT: SBOM CycloneDX, vulnerabilidades",
            "OSV + CISA KEV y borradores de reporte con IA.",
        ],
        "metrics": [("300+", "tests"), ("24h·72h·14d", "relojes de reporte"), ("hash-chain", "audit log")],
        "stack": ["Spring Boot", "Go", "Next.js", "PostgreSQL"],
    },
    {
        "file": "vigia", "idx": "02", "kind": "DATA · FORECASTING",
        "title": "Vigía", "accent": "#2dd4bf",
        "status": ("EN DESARROLLO", "#2dd4bf"),
        "desc": [
            "Ingesta, análisis y pronóstico de vigilancia",
            "epidemiológica del Perú. Convierte CSV/XLSX",
            "desordenados en datos validados y forecasts.",
        ],
        "metrics": [("CSV/XLSX", "ingesta validada"), ("zod", "contratos tipados"), ("monorepo", "TypeScript e2e")],
        "stack": ["NestJS", "Next.js", "TypeORM", "PostgreSQL"],
    },
    {
        "file": "inkari", "idx": "03", "kind": "E-COMMERCE",
        "title": "Inkari Café", "accent": "#f5a524",
        "status": ("EN PRODUCCIÓN", "#28c840"),
        "desc": [
            "Tienda de café en producción con panel",
            "administrativo para productos, pedidos y",
            "contenido, más alertas de control operativo.",
        ],
        "metrics": [("live", "inkari.shop"), ("admin", "panel de gestión"), ("alertas", "operativas")],
        "stack": ["Next.js", "Express", "Tailwind", "PostgreSQL"],
    },
    {
        "file": "cem", "idx": "04", "kind": "E-LEARNING",
        "title": "CEM eLearning", "accent": "#a78bfa",
        "status": ("DEMO EN VIVO", "#a78bfa"),
        "desc": [
            "Plataforma de cursos con módulos por dominio.",
            "Modelé la base de datos relacional y la lógica",
            "de negocio académica y administrativa.",
        ],
        "metrics": [("4", "dominios"), ("Next 16", "+ React 19"), ("Redux", "estado global")],
        "stack": ["Next.js", "React", "Redux", "TypeScript"],
    },
]


def project_svg(p: dict) -> str:
    W, H, PAD = 480, 300, 28
    a = p["accent"]
    status, scol = p["status"]

    pill_w = len(status) * 7.1 + 32  # 10px mono + 1px letter-spacing
    pill_x = W - PAD - pill_w

    desc = "".join(
        f'<text x="{PAD}" y="{116 + i * 21}" class="desc">{esc(line)}</text>'
        for i, line in enumerate(p["desc"])
    )

    col_w = (W - 2 * PAD) / 3
    metrics = "".join(
        f'<g class="f d3"><text x="{PAD + i * col_w}" y="214" class="mv" fill="{a if i == 0 else "#eef1ff"}">{esc(v)}</text>'
        f'<text x="{PAD + i * col_w}" y="233" class="ml">{esc(l)}</text></g>'
        for i, (v, l) in enumerate(p["metrics"])
    )

    chips, x = [], PAD
    for s in p["stack"]:
        cw = mono_w(s, 11) + 22
        chips.append(
            f'<rect x="{x}" y="254" width="{cw:.1f}" height="24" rx="12" fill="#ffffff" fill-opacity="0.05" stroke="#ffffff" stroke-opacity="0.1"/>'
            f'<text x="{x + cw / 2:.1f}" y="270" class="chip" text-anchor="middle">{esc(s)}</text>'
        )
        x += cw + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(p['title'])}">
  <defs>{common_defs(a, W, H)}
    <style>
      .k{{font:600 11px {MONO};letter-spacing:2px}}
      .t{{font:700 30px {SANS};fill:#f3f5ff;letter-spacing:-0.5px}}
      .desc{{font:400 14.5px {SANS};fill:#aab3d1}}
      .mv{{font:700 19px {SANS};letter-spacing:-0.3px}}
      .ml{{font:400 11px {MONO};fill:#7f89a8}}
      .chip{{font:500 11px {MONO};fill:#cfd5ec}}
      .st{{font:600 10px {MONO};letter-spacing:1px}}
            .pulse{{animation:p 2s ease-in-out infinite}}
      @keyframes p{{50%{{opacity:.25}}}}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <rect width="{W}" height="3" fill="url(#bar)"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>

  <g class="f d1">
    <text x="{PAD}" y="42" class="k" fill="{a}">{p['idx']} <tspan fill="#5d6785">/</tspan> {esc(p['kind'])}</text>
    <rect x="{pill_x:.1f}" y="27" width="{pill_w:.1f}" height="22" rx="11" fill="{scol}" fill-opacity="0.12" stroke="{scol}" stroke-opacity="0.35"/>
    <circle class="pulse" cx="{pill_x + 13:.1f}" cy="38" r="3.5" fill="{scol}"/>
    <text x="{pill_x + 23:.1f}" y="41.5" class="st" fill="{scol}">{esc(status)}</text>
  </g>
  <g class="f d2">
    <text x="{PAD}" y="84" class="t">{esc(p['title'])}</text>
    {desc}
  </g>
  <line x1="{PAD}" y1="184" x2="{W - PAD}" y2="184" stroke="#ffffff" stroke-opacity="0.08"/>
  {metrics}
  <g class="f d4">{''.join(chips)}
    <text x="{W - PAD}" y="271" text-anchor="end" font-family="{SANS}" font-size="18" fill="{a}">↗</text>
  </g>
</svg>
"""


# ───────────────────────────── Experiencia ─────────────────────────────

EXPERIENCE = [
    {
        "company": "Grupo CORIL", "period": "Ene 2026 — Actualidad", "current": True,
        "tag": "SECTOR FINANCIERO",
        "roles": [
            ("Full Stack · Gestión de Patrimonios", "Ago 2026 — hoy",
             "Obligaciones, vencimientos y cumplimiento mensual; roles y permisos para contadores."),
            ("Full Stack · Abonos Bancarios", "Jun — Ago 2026",
             "Carga y migración manual/automática de abonos; eliminé el registro manual."),
            ("Full Stack · Gestión de Emisiones", "Abr — Jun 2026",
             "Servicios backend y vistas de reportes e indicadores con arquitectura por capas."),
            ("Frontend · Intranet Corporativa", "Ene — Abr 2026",
             "Módulos reutilizables y responsive organizados por roles de usuario."),
        ],
    },
    {
        "company": "CEM eLearning", "period": "Dic 2025 — Abr 2026", "tag": "EDTECH",
        "roles": [("Desarrollador Full Stack", "",
                   "Modelé la base de datos relacional y la lógica académica con arquitectura modular.")],
    },
    {
        "company": "Comparapet", "period": "Oct — Dic 2025", "tag": "DATOS",
        "roles": [("Base de Datos y Mejora Continua", "",
                   "Normalicé PostgreSQL y optimicé consultas: búsqueda de productos 2× más rápida.")],
    },
    {
        "company": "OpenLab", "period": "Feb 2024 — Dic 2025", "tag": "PRÁCTICA",
        "roles": [("Pasante de Desarrollo Full Stack", "",
                   "Interfaces responsive, APIs y optimización de consultas PostgreSQL.")],
    },
]


def experience_svg() -> str:
    W, PAD, LX = 900, 40, 56
    a = "#7c9cff"
    body, y, delay = [], 64, 0.05

    for ci, c in enumerate(EXPERIENCE):
        cur = c.get("current")
        dot_col = "#2dd4bf" if cur else a
        block = []
        # nodo de la empresa
        if cur:
            block.append(f'<circle class="pulse" cx="{LX}" cy="{y - 6}" r="13" fill="{dot_col}" fill-opacity="0.25"/>')
        block.append(f'<circle cx="{LX}" cy="{y - 6}" r="7" fill="#0b1020" stroke="{dot_col}" stroke-width="2.5"/>')
        block.append(f'<circle cx="{LX}" cy="{y - 6}" r="2.5" fill="{dot_col}"/>')
        block.append(f'<text x="{LX + 30}" y="{y}" class="co">{esc(c["company"])}</text>')
        tag_x = LX + 30 + len(c["company"]) * 11.2 + 14
        tw = mono_w(c["tag"], 9.5) + 18
        block.append(f'<rect x="{tag_x:.1f}" y="{y - 16}" width="{tw:.1f}" height="20" rx="10" fill="{dot_col}" fill-opacity="0.1" stroke="{dot_col}" stroke-opacity="0.3"/>')
        block.append(f'<text x="{tag_x + tw / 2:.1f}" y="{y - 2.5}" class="tg" fill="{dot_col}" text-anchor="middle">{esc(c["tag"])}</text>')
        block.append(f'<text x="{W - PAD}" y="{y}" class="pe" text-anchor="end">{esc(c["period"])}</text>')
        y += 34

        multi = len(c["roles"]) > 1
        for ri, (role, period, hl) in enumerate(c["roles"]):
            rx = LX + 30
            if multi:
                block.append(f'<line x1="{rx + 4}" y1="{y - 18}" x2="{rx + 4}" y2="{y + 28 if ri < len(c["roles"]) - 1 else y + 4}" stroke="#ffffff" stroke-opacity="0.08"/>')
                block.append(f'<circle cx="{rx + 4}" cy="{y - 5}" r="3.5" fill="{dot_col if ri == 0 and cur else "#3b4566"}"/>')
                rx += 22
            block.append(f'<text x="{rx}" y="{y}" class="ro">{esc(role)}</text>')
            if period:
                block.append(f'<text x="{W - PAD}" y="{y}" class="rp" text-anchor="end">{esc(period)}</text>')
            block.append(f'<text x="{rx}" y="{y + 21}" class="hl">{esc(hl)}</text>')
            y += 54
        body.append(f'<g class="f">{"".join(block)}</g>')
        delay += 0.2
        y += 22

    line_end = y - 22 - 54 - 34 + 6
    # formación
    y += 6
    edu = (
        f'<line x1="{PAD}" y1="{y - 30}" x2="{W - PAD}" y2="{y - 30}" stroke="#ffffff" stroke-opacity="0.08"/>'
        f'<text x="{PAD}" y="{y}" class="k" fill="{a}">FORMACIÓN</text>'
        f'<text x="{PAD + 110}" y="{y}" class="ed"><tspan fill="#eef1ff" font-weight="600">Ingeniería Industrial</tspan> · Universidad Privada del Norte'
        f'<tspan fill="#5d6785" dx="14">/</tspan><tspan dx="14" fill="#eef1ff" font-weight="600">Gestión de Sistemas de Información</tspan> · Zegel</text>'
    )
    H = y + 34

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Experiencia profesional de Anthony Díaz">
  <defs>{common_defs(a, W, H)}
    <linearGradient id="rail" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2dd4bf"/><stop offset="0.5" stop-color="#7c9cff"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0.2"/>
    </linearGradient>
    <style>
      .co{{font:700 20px {SANS};fill:#f3f5ff;letter-spacing:-0.3px}}
      .tg{{font:600 9.5px {MONO};letter-spacing:1.2px}}
      .pe{{font:500 12.5px {MONO};fill:#aab3d1}}
      .ro{{font:600 15px {SANS};fill:#e3e7f7}}
      .rp{{font:400 11.5px {MONO};fill:#6f7a99}}
      .hl{{font:400 13.5px {SANS};fill:#8f99b8}}
      .k{{font:600 11px {MONO};letter-spacing:2px}}
      .ed{{font:400 13.5px {SANS};fill:#8f99b8}}
            .pulse{{animation:p 2.2s ease-in-out infinite}}
      @keyframes p{{50%{{opacity:.15}}}}
    </style>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="15.5" fill="none" stroke="#ffffff" stroke-opacity="0.09"/>
  <rect x="{LX - 1}" y="58" width="2" height="{line_end - 58}" rx="1" fill="url(#rail)"/>
  {''.join(body)}
  {edu}
</svg>
"""


def main() -> None:
    out = ROOT / "assets" / "projects"
    out.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS:
        (out / f"{p['file']}.svg").write_text(project_svg(p), encoding="utf-8")
    (ROOT / "assets" / "experience.svg").write_text(experience_svg(), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
