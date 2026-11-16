"""Render the iframe from the daily build's already-fetched public dataset."""
import html
from pathlib import Path
from urllib.parse import urlsplit

TEMPLATE = Path(__file__).with_name("widget.html")
RANKING_URL = "https://trading-latam.com/ranking-toptraders/"


def render_widget(data):
    """Keep source order and expose only the widget's public field whitelist."""
    entries = []
    for row in data.get("strategies", [])[:5]:
        alias = html.escape(str(row.get("strategy_alias") or "Estrategia sin alias"))
        url = str(row.get("report_url") or "")
        try:
            parsed = urlsplit(url)
            safe_url = parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
        except ValueError:
            safe_url = False
        # Invalid URLs leave the alias readable; escaping alone does not make a javascript: link safe.
        if safe_url:
            alias = f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{alias}</a>'
        broker = html.escape(str(row.get("broker") or "Bróker no disponible"))
        platform = html.escape(str(row.get("platform") or "Plataforma no disponible"))
        score = '<strong title="No disponible">—</strong>' if row.get("tl_score") is None else f'<strong>{html.escape(str(row["tl_score"]))}</strong>'
        drawdown = '<span title="No disponible">—</span>' if row.get("drawdown_max") is None else f'<span>{html.escape(str(row["drawdown_max"]))}%</span>'
        position = html.escape(str(row.get("position") or "—"))
        entries.append(
            f'<li class="entry"><span class="position" aria-label="Posición {position}">{position}</span>'
            f'<div class="identity">{alias}<p>{broker} · {platform}</p></div>'
            f'<dl><div><dt>TL-Score</dt><dd>{score}</dd></div>'
            f'<div><dt>Caída máx.</dt><dd>{drawdown}</dd></div></dl></li>'
        )
    content = '<ol class="ranking">' + "\n".join(entries) + '</ol>' if entries else '<p class="empty">No hay estrategias públicas disponibles.</p>'
    date = data.get("date_modified")
    date_html = f'<time datetime="{html.escape(str(date), quote=True)}">{html.escape(str(date))}</time>' if date else 'Fecha no disponible'
    return (TEMPLATE.read_text(encoding="utf-8")
            .replace("{{ENTRIES}}", content)
            .replace("{{DATE}}", date_html)
            .replace("{{RANKING_URL}}", RANKING_URL))
