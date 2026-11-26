"""Self-contained HTML report of the inventory."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from html import escape

from . import __version__
from .legal import ART7, ART11, ART33, SENSITIVE, gdpr_hint
from .loader import Inventory
from .validate import ERROR, Finding, dpia_reasons, risk_score

L = {
    "pt": {
        "title": "Registro das Operações de Tratamento",
        "controller": "Controlador",
        "dpo": "Encarregado",
        "reviewed": "Inventário revisado em",
        "generated": "Relatório gerado em",
        "disclaimer": "Ferramenta de apoio: não substitui orientação jurídica.",
        "s_ops": "operações",
        "s_sensitive": "com dados sensíveis",
        "s_transfers": "com transferência internacional",
        "s_dpia": "pedem RIPD",
        "s_errors": "erros",
        "s_warnings": "avisos",
        "areas": "Índice por área",
        "operations": "Operações",
        "id": "ID",
        "name": "Operação",
        "purpose": "Finalidade",
        "subjects": "Titulares",
        "data": "Dados tratados",
        "basis": "Base legal",
        "retention": "Retenção",
        "owner": "Responsável",
        "processors_title": "Operadores e compartilhamentos",
        "processor": "Operador",
        "service": "Serviço",
        "country": "País",
        "contract": "Contrato",
        "dpa": "DPA",
        "sharing": "Compartilhado com",
        "transfers_title": "Transferências internacionais",
        "recipient": "Destinatário",
        "mechanism": "Mecanismo (art. 33)",
        "missing": "não informado",
        "risk_title": "Matriz de risco das operações que pedem RIPD",
        "likelihood": "Probabilidade",
        "impact": "Impacto",
        "why": "Motivo",
        "dpia_status": "RIPD",
        "no_risk": "sem probabilidade e impacto",
        "pending_title": "Pendências",
        "level": "Nível",
        "file": "Arquivo",
        "field": "Campo",
        "message": "Mensagem",
        "error": "erro",
        "warning": "aviso",
        "none": "Nenhuma.",
        "yes": "sim",
        "no": "não",
        "done": "concluído",
        "in_progress": "em andamento",
        "not_started": "não iniciado",
        "absent": "não existe",
        "sensitive_tag": "sensível",
        "children_tag": "crianças",
        "gdpr": "GDPR",
        "not_in_report": "Operações com erro de estrutura ficam fora das tabelas até serem corrigidas.",
    },
    "en": {
        "title": "Record of Processing Activities",
        "controller": "Controller",
        "dpo": "DPO",
        "reviewed": "Inventory reviewed on",
        "generated": "Report generated on",
        "disclaimer": "Support tool: it does not replace legal advice.",
        "s_ops": "operations",
        "s_sensitive": "with sensitive data",
        "s_transfers": "with international transfers",
        "s_dpia": "need a DPIA",
        "s_errors": "errors",
        "s_warnings": "warnings",
        "areas": "Index by area",
        "operations": "Operations",
        "id": "ID",
        "name": "Operation",
        "purpose": "Purpose",
        "subjects": "Data subjects",
        "data": "Personal data",
        "basis": "Legal basis",
        "retention": "Retention",
        "owner": "Owner",
        "processors_title": "Processors and sharing",
        "processor": "Processor",
        "service": "Service",
        "country": "Country",
        "contract": "Contract",
        "dpa": "DPA",
        "sharing": "Shared with",
        "transfers_title": "International transfers",
        "recipient": "Recipient",
        "mechanism": "Mechanism (art. 33)",
        "missing": "missing",
        "risk_title": "Risk matrix of operations that need a DPIA",
        "likelihood": "Likelihood",
        "impact": "Impact",
        "why": "Reason",
        "dpia_status": "DPIA",
        "no_risk": "no likelihood and impact",
        "pending_title": "Open issues",
        "level": "Level",
        "file": "File",
        "field": "Field",
        "message": "Message",
        "error": "error",
        "warning": "warning",
        "none": "None.",
        "yes": "yes",
        "no": "no",
        "done": "done",
        "in_progress": "in progress",
        "not_started": "not started",
        "absent": "none",
        "sensitive_tag": "sensitive",
        "children_tag": "children",
        "gdpr": "GDPR",
        "not_in_report": "Operations with structural errors stay out of the tables until fixed.",
    },
}

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--text:#1c2430;--muted:#5b6676;--line:#dde2e8;--accent:#1f6feb;
--err:#c62828;--warn:#a15c00;--sens:#8e24aa;--ok:#2e7d32;--h1:#fdecea;--h2:#fff4e0;--h3:#e8f5e9}
@media (prefers-color-scheme:dark){:root{--bg:#0f141a;--card:#171d25;--text:#e6ebf1;--muted:#9aa6b5;
--line:#2a333f;--accent:#58a6ff;--err:#ff7b72;--warn:#e3b341;--sens:#d2a8ff;--ok:#7ee787;
--h1:#3d1d1d;--h2:#3a2d12;--h3:#16301d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font:14px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 48px}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.15rem;margin:32px 0 12px;
border-bottom:1px solid var(--line);padding-bottom:6px}h3{font-size:1rem;margin:20px 0 8px}
.meta{color:var(--muted);margin:2px 0}.disclaimer{font-size:.85rem;color:var(--muted)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
.card b{display:block;font-size:1.5rem}.card.err b{color:var(--err)}.card.warn b{color:var(--warn)}
.scroll{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;
padding:7px 10px;border-bottom:1px solid var(--line)}th{font-size:.8rem;text-transform:uppercase;
letter-spacing:.03em;color:var(--muted);white-space:nowrap}tr:last-child td{border-bottom:0}
code{font-family:ui-monospace,Consolas,monospace;font-size:.85em}
.tag{display:inline-block;border-radius:4px;padding:0 6px;margin:1px 2px 1px 0;font-size:.8rem;
border:1px solid var(--line)}.tag.sens{border-color:var(--sens);color:var(--sens);font-weight:600}
.ref{color:var(--muted);font-size:.8rem}.bad{color:var(--err);font-weight:600}
.lvl-error{color:var(--err);font-weight:600}.lvl-warning{color:var(--warn);font-weight:600}
.areas{display:flex;flex-wrap:wrap;gap:8px;padding:0;list-style:none}
.areas a{display:block;background:var(--card);border:1px solid var(--line);border-radius:6px;
padding:6px 10px;color:var(--accent);text-decoration:none}
.matrix{display:grid;grid-template-columns:auto repeat(5,minmax(80px,1fr));gap:4px;
min-width:520px;padding:10px}
.matrix .ax{color:var(--muted);font-size:.8rem;display:flex;align-items:center;justify-content:center}
.cell{min-height:54px;border-radius:6px;padding:4px;font-size:.75rem}
.cell.lo{background:var(--h3)}.cell.mid{background:var(--h2)}.cell.hi{background:var(--h1)}
.cell a{color:var(--text)}
footer{margin-top:40px;color:var(--muted);font-size:.8rem}
@media print{body{background:#fff}.scroll,.card{border-color:#ccc}h2{break-after:avoid}}
"""


def _e(value: object) -> str:
    return escape(str(value), quote=True)


def _join(items, empty: str = "") -> str:
    return ", ".join(_e(i) for i in items) if items else empty


def _basis(op: dict, lang: str) -> str:
    parts = []
    p7 = ART7.get(op.get("legal_basis", ""))
    if p7:
        hint = gdpr_hint(p7.code)
        gdpr = f" · GDPR {hint}" if hint != "n/a" else ""
        parts.append(f"{_e(p7.label(lang))}<br><span class='ref'>{_e(p7.reference)}{_e(gdpr)}</span>")
    p11 = ART11.get(op.get("sensitive_legal_basis", ""))
    if p11:
        parts.append(f"{_e(p11.label(lang))}<br><span class='ref'>{_e(p11.reference)}</span>")
    return "<br>".join(parts)


def _data_tags(op: dict, t: dict, lang: str) -> str:
    tags = [f"<span class='tag'>{_e(d)}</span>" for d in op.get("personal_data") or []]
    for code in op.get("sensitive_data") or []:
        label = SENSITIVE[code].label(lang) if code in SENSITIVE else code
        tags.append(f"<span class='tag sens' title='{_e(t['sensitive_tag'])}'>{_e(label)}</span>")
    if op.get("children_data"):
        tags.append(f"<span class='tag sens'>{_e(t['children_tag'])}</span>")
    return "".join(tags)


def _retention(op: dict, t: dict) -> str:
    ret = op.get("retention") or {}
    period = (ret.get("period") or "").strip()
    if not period:
        return f"<span class='bad'>{_e(t['missing'])}</span>"
    extra = f"<br><span class='ref'>{_e(ret['justification'])}</span>" if ret.get("justification") else ""
    return _e(period) + extra


def _yes_no(value: object, t: dict) -> str:
    return _e(t["yes"]) if value else f"<span class='bad'>{_e(t['no'])}</span>"


def _anchor(op_id: str) -> str:
    return f"op-{_e(op_id)}"


def render_report(
    inventory: Inventory, findings: list[Finding], lang: str = "pt", today: date | None = None
) -> str:
    t = L[lang]
    today = today or date.today()
    broken = {f.file for f in findings if f.code in ("Y001", "Y002", "S001")}
    ops = [d.data for d in inventory.operations if isinstance(d.data, dict) and d.path not in broken]
    org = inventory.org if inventory.organization.path not in broken else {}
    controller = org.get("controller") or {}
    dpo = org.get("dpo") or {}

    by_area: dict[str, list[dict]] = defaultdict(list)
    for op in ops:
        by_area[op["area"]].append(op)
    areas = sorted(by_area, key=str.casefold)
    for area in areas:
        by_area[area].sort(key=lambda o: o["id"])

    errors = sum(1 for f in findings if f.level == ERROR)
    warnings = len(findings) - errors
    needs_dpia = [op for op in ops if dpia_reasons(op, lang)]
    stats = [
        ("", len(ops), t["s_ops"]),
        ("", sum(1 for o in ops if o.get("sensitive_data")), t["s_sensitive"]),
        ("", sum(1 for o in ops if o.get("international_transfers")), t["s_transfers"]),
        ("", len(needs_dpia), t["s_dpia"]),
        ("err", errors, t["s_errors"]),
        ("warn", warnings, t["s_warnings"]),
    ]

    out: list[str] = []
    w = out.append
    w(f"<!doctype html><html lang='{'pt-BR' if lang == 'pt' else 'en'}'><head><meta charset='utf-8'>")
    w("<meta name='viewport' content='width=device-width,initial-scale=1'>")
    w(f"<title>{_e(t['title'])}: {_e(controller.get('name', ''))}</title><style>{CSS}</style></head>")
    w("<body><main>")
    w(f"<h1>{_e(t['title'])}</h1>")
    if controller:
        cnpj = f" · CNPJ {_e(controller['cnpj'])}" if controller.get("cnpj") else ""
        w(f"<p class='meta'>{_e(t['controller'])}: <b>{_e(controller.get('name', ''))}</b>{cnpj}</p>")
    contact = " · ".join(_e(x) for x in (dpo.get("name"), dpo.get("email"), dpo.get("channel")) if x)
    if contact:
        w(f"<p class='meta'>{_e(t['dpo'])}: {contact}</p>")
    dates = []
    if org.get("reviewed_at"):
        dates.append(f"{_e(t['reviewed'])} {_e(org['reviewed_at'])}")
    dates.append(f"{_e(t['generated'])} {today.isoformat()}")
    w(f"<p class='meta'>{' · '.join(dates)}</p>")
    w(f"<p class='disclaimer'>{_e(t['disclaimer'])}</p>")

    w("<div class='cards'>")
    for cls, value, label in stats:
        w(f"<div class='card {cls}'><b>{value}</b>{_e(label)}</div>")
    w("</div>")

    # Index by area
    w(f"<h2 id='areas'>{_e(t['areas'])}</h2><ul class='areas'>")
    for area in areas:
        w(f"<li><a href='#area-{_e(area)}'>{_e(area)} ({len(by_area[area])})</a></li>")
    w("</ul>")

    # Operations, grouped by area
    w(f"<h2>{_e(t['operations'])}</h2>")
    for area in areas:
        w(f"<h3 id='area-{_e(area)}'>{_e(area)}</h3><div class='scroll'><table><thead><tr>")
        for key in ("id", "name", "subjects", "data", "basis", "retention"):
            w(f"<th>{_e(t[key])}</th>")
        w("</tr></thead><tbody>")
        for op in by_area[area]:
            owner = (
                f"<br><span class='ref'>{_e(t['owner'])}: {_e(op['owner'])}</span>" if op.get("owner") else ""
            )
            w(
                f"<tr id='{_anchor(op['id'])}'><td><code>{_e(op['id'])}</code></td>"
                f"<td><b>{_e(op['name'])}</b><br><span class='ref'>{_e(op['purpose'])}</span>{owner}</td>"
                f"<td>{_join(op.get('data_subjects'))}</td>"
                f"<td>{_data_tags(op, t, lang)}</td>"
                f"<td>{_basis(op, lang)}</td>"
                f"<td>{_retention(op, t)}</td></tr>"
            )
        w("</tbody></table></div>")

    # Processors and sharing
    w(f"<h2>{_e(t['processors_title'])}</h2>")
    rows = []
    for op in ops:
        for proc in op.get("processors") or []:
            rows.append(
                f"<tr><td><a href='#{_anchor(op['id'])}'><code>{_e(op['id'])}</code></a></td>"
                f"<td>{_e(proc['name'])}</td><td>{_e(proc.get('service', ''))}</td>"
                f"<td>{_e(proc.get('country', ''))}</td><td>{_yes_no(proc.get('contract'), t)}</td>"
                f"<td>{_yes_no(proc.get('dpa'), t)}</td></tr>"
            )
    if rows:
        w("<div class='scroll'><table><thead><tr>")
        for key in ("id", "processor", "service", "country", "contract", "dpa"):
            w(f"<th>{_e(t[key])}</th>")
        w("</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")
    else:
        w(f"<p>{_e(t['none'])}</p>")
    shared = [
        f"<tr><td><a href='#{_anchor(op['id'])}'><code>{_e(op['id'])}</code></a></td>"
        f"<td>{_e(s['recipient'])}</td><td>{_e(s.get('purpose', ''))}</td></tr>"
        for op in ops
        for s in op.get("sharing") or []
    ]
    if shared:
        w(f"<h3>{_e(t['sharing'])}</h3><div class='scroll'><table><thead><tr>")
        w(f"<th>{_e(t['id'])}</th><th>{_e(t['recipient'])}</th><th>{_e(t['purpose'])}</th>")
        w("</tr></thead><tbody>" + "".join(shared) + "</tbody></table></div>")

    # International transfers
    w(f"<h2>{_e(t['transfers_title'])}</h2>")
    transfers = []
    for op in ops:
        for tr in op.get("international_transfers") or []:
            mech = ART33.get(tr.get("mechanism", ""))
            mech_html = (
                f"{_e(mech.label(lang))}<br><span class='ref'>{_e(mech.reference)}</span>"
                if mech
                else f"<span class='bad'>{_e(t['missing'])}</span>"
            )
            transfers.append(
                f"<tr><td><a href='#{_anchor(op['id'])}'><code>{_e(op['id'])}</code></a></td>"
                f"<td>{_e(tr['country'])}</td><td>{_e(tr.get('recipient', ''))}</td><td>{mech_html}</td></tr>"
            )
    if transfers:
        w("<div class='scroll'><table><thead><tr>")
        for key in ("id", "country", "recipient", "mechanism"):
            w(f"<th>{_e(t[key])}</th>")
        w("</tr></thead><tbody>" + "".join(transfers) + "</tbody></table></div>")
    else:
        w(f"<p>{_e(t['none'])}</p>")

    # Risk matrix
    w(f"<h2>{_e(t['risk_title'])}</h2>")
    if needs_dpia:
        grid: dict[tuple[int, int], list[str]] = defaultdict(list)
        for op in needs_dpia:
            risk = op.get("risk") or {}
            if risk_score(op) is not None:
                grid[(risk["likelihood"], risk["impact"])].append(op["id"])
        w("<div class='scroll'><div class='matrix'>")
        for likelihood in range(5, 0, -1):
            w(f"<div class='ax'>{likelihood}</div>")
            for impact in range(1, 6):
                score = likelihood * impact
                cls = "hi" if score >= 12 else "mid" if score >= 6 else "lo"
                links = "<br>".join(
                    f"<a href='#{_anchor(i)}'>{_e(i)}</a>" for i in sorted(grid[(likelihood, impact)])
                )
                w(f"<div class='cell {cls}' title='{likelihood} x {impact} = {score}'>{links}</div>")
        w("<div></div>" + "".join(f"<div class='ax'>{i}</div>" for i in range(1, 6)))
        w(
            f"</div><p class='ref' style='padding:0 10px 10px'>{_e(t['likelihood'])} (↑) x "
            f"{_e(t['impact'])} (→)</p></div>"
        )
        w("<div class='scroll' style='margin-top:10px'><table><thead><tr>")
        w(
            f"<th>{_e(t['id'])}</th><th>{_e(t['name'])}</th><th>{_e(t['why'])}</th><th>{_e(t['dpia_status'])}</th>"
        )
        w("</tr></thead><tbody>")
        for op in sorted(needs_dpia, key=lambda o: (-(risk_score(o) or 0), o["id"])):
            dpia = op.get("dpia") or {}
            status = dpia.get("status")
            label = t.get(status, t["absent"]) if status else t["absent"]
            ref = f" <span class='ref'>{_e(dpia['reference'])}</span>" if dpia.get("reference") else ""
            cls = "" if status == "done" else " class='bad'"
            reasons = dpia_reasons(op, lang)
            if risk_score(op) is None:
                reasons.append(t["no_risk"])
            w(
                f"<tr><td><a href='#{_anchor(op['id'])}'><code>{_e(op['id'])}</code></a></td>"
                f"<td>{_e(op['name'])}</td><td>{_join(reasons)}</td><td><span{cls}>{_e(label)}</span>{ref}</td></tr>"
            )
        w("</tbody></table></div>")
    else:
        w(f"<p>{_e(t['none'])}</p>")

    # Open issues
    w(f"<h2 id='pending'>{_e(t['pending_title'])}</h2>")
    if findings:
        if broken:
            w(f"<p class='ref'>{_e(t['not_in_report'])}</p>")
        w("<div class='scroll'><table><thead><tr>")
        for key in ("level", "file", "field", "message"):
            w(f"<th>{_e(t[key])}</th>")
        w("</tr></thead><tbody>")
        ordered = sorted(findings, key=lambda f: (f.level != ERROR, f.file, f.code, f.field))
        for f in ordered:
            w(
                f"<tr><td class='lvl-{f.level}'>{_e(t[f.level])} <span class='ref'>{_e(f.code)}</span></td>"
                f"<td><code>{_e(f.file)}</code></td><td><code>{_e(f.field)}</code></td>"
                f"<td>{_e(f.message)}</td></tr>"
            )
        w("</tbody></table></div>")
    else:
        w(f"<p>{_e(t['none'])}</p>")

    w(f"<footer>lgpd-ropa-kit {__version__} · {_e(t['disclaimer'])}</footer>")
    w("</main></body></html>\n")
    return "\n".join(out)
