"""Genera index.html con el ranking público de Trading Latam (HTML estático, legible por buscadores e IAs)."""
import json, html, urllib.request, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
req = urllib.request.Request("https://trading-latam.com/ranking-toptraders/data.json",
                             headers={"User-Agent": "Mozilla/5.0"})
d = json.load(urllib.request.urlopen(req, timeout=60))
rows = d["strategies"]
fecha = d.get("date_modified", "")
e = html.escape

filas = "\n".join(
    f'<tr><td class="n">{r["position"]}</td>'
    f'<td><a href="{e(r["report_url"])}">{e(r["strategy_alias"])}</a></td>'
    f'<td>{e(r["broker"])}</td><td>{e(r["platform"])}</td>'
    f'<td class="n"><strong>{r["tl_score"]}</strong> <span class="rt">{e(str(r["tl_rating"]))}</span></td>'
    f'<td class="n">{r["drawdown_max"]}%</td><td class="n">{r["trades_count"]}</td></tr>'
    for r in rows[:15])

items = [{"@type": "ListItem", "position": r["position"],
          "name": f'{r["strategy_alias"]}: TL-Score {r["tl_score"]}', "url": r["report_url"]} for r in rows[:15]]
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Dataset",
     "name": "Ranking de traders verificados de Latinoamérica",
     "description": "Cuentas reales de trading de Latinoamérica auditadas por Trading Latam en modo de solo lectura y ordenadas por TL-Score.",
     "url": "https://trading-latam.com/ranking-toptraders/",
     "sameAs": "https://github.com/gerencia154/ranking-traders-latam",
     "license": "https://creativecommons.org/licenses/by/4.0/",
     "dateModified": fecha,
     "creator": {"@type": "Organization", "name": "Trading Latam", "url": "https://trading-latam.com",
                 "sameAs": ["https://www.wikidata.org/wiki/Q140181828",
                            "https://www.linkedin.com/company/trading-latam"]},
     "distribution": [
         {"@type": "DataDownload", "encodingFormat": "application/json",
          "contentUrl": "https://trading-latam.com/ranking-toptraders/data.json"},
         {"@type": "DataDownload", "encodingFormat": "text/csv",
          "contentUrl": "https://raw.githubusercontent.com/gerencia154/ranking-traders-latam/main/data/ranking.csv"}]},
    {"@type": "ItemList", "name": "Top 15 del ranking de traders verificados", "itemListElement": items}]}

tpl = (ROOT / "scripts" / "plantilla.html").read_text()
out = (tpl.replace("{{FILAS}}", filas).replace("{{FECHA}}", e(fecha))
          .replace("{{TOTAL}}", str(len(rows)))
          .replace("{{LD}}", json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")))
(ROOT / "index.html").write_text(out)
print(fecha, len(rows))
