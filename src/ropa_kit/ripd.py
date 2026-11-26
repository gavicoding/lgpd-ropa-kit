"""Markdown skeleton of a DPIA (RIPD, LGPD art. 5, XVII and art. 38) for one operation."""

from __future__ import annotations

from datetime import date

from .legal import ART7, ART11, ART33, SENSITIVE
from .validate import dpia_reasons, risk_score

TODO = {"pt": "_[preencher]_", "en": "_[fill in]_"}

T = {
    "pt": {
        "title": "Relatório de Impacto à Proteção de Dados Pessoais (RIPD)",
        "draft": "Rascunho gerado a partir do inventário em {date}. Revise cada seção antes de "
        "aprovar. Este documento não substitui orientação jurídica.",
        "s1": "1. Identificação dos agentes de tratamento",
        "controller": "Controlador",
        "dpo": "Encarregado",
        "owner": "Área responsável",
        "s2": "2. Por que este relatório é necessário",
        "s3": "3. Descrição do tratamento",
        "operation": "Operação",
        "purpose": "Finalidade",
        "subjects": "Titulares",
        "data": "Dados pessoais",
        "sensitive": "Dados sensíveis",
        "children": "Envolve dados de crianças ou adolescentes (art. 14)",
        "systems": "Sistemas",
        "processors": "Operadores",
        "sharing": "Compartilhamentos",
        "transfers": "Transferências internacionais",
        "flow": "Ciclo de vida (coleta, uso, armazenamento, eliminação)",
        "s4": "4. Partes interessadas consultadas",
        "s5": "5. Necessidade e proporcionalidade",
        "basis": "Base legal",
        "sbasis": "Base legal para dados sensíveis",
        "lia": "Teste de balanceamento (LIA)",
        "minimization": "Por que cada dado é necessário (minimização, art. 6, III)",
        "retention": "Retenção",
        "disposal": "Eliminação",
        "rights": "Como o titular exerce seus direitos (art. 18)",
        "s6": "6. Riscos identificados",
        "current": "Avaliação atual no inventário: probabilidade {l}, impacto {i}, pontuação {s}.",
        "risk_table": "| Risco | Probabilidade (1 a 5) | Impacto (1 a 5) | Nível |",
        "risk_examples": [
            "Acesso não autorizado",
            "Vazamento ou perda de dados",
            "Uso para finalidade diferente da informada",
            "Retenção além do necessário",
        ],
        "s7": "7. Medidas para tratar os riscos",
        "existing": "Medidas já registradas",
        "planned": "| Risco | Medida | Responsável | Prazo |",
        "s8": "8. Aprovação",
        "approval": "| Papel | Nome | Data | Parecer |",
        "roles": ["Encarregado", "Área responsável", "Representante do controlador"],
        "none": "nenhum",
        "yes": "sim",
    },
    "en": {
        "title": "Data Protection Impact Assessment (DPIA / RIPD)",
        "draft": "Draft generated from the inventory on {date}. Review every section before "
        "approval. This document does not replace legal advice.",
        "s1": "1. Controller and processors",
        "controller": "Controller",
        "dpo": "DPO",
        "owner": "Owner",
        "s2": "2. Why this assessment is needed",
        "s3": "3. Description of the processing",
        "operation": "Operation",
        "purpose": "Purpose",
        "subjects": "Data subjects",
        "data": "Personal data",
        "sensitive": "Sensitive data",
        "children": "Involves children's or adolescents' data (art. 14)",
        "systems": "Systems",
        "processors": "Processors",
        "sharing": "Sharing",
        "transfers": "International transfers",
        "flow": "Life cycle (collection, use, storage, deletion)",
        "s4": "4. Stakeholders consulted",
        "s5": "5. Necessity and proportionality",
        "basis": "Legal basis",
        "sbasis": "Legal basis for sensitive data",
        "lia": "Legitimate interest assessment (LIA)",
        "minimization": "Why each data item is needed (data minimization, art. 6, III)",
        "retention": "Retention",
        "disposal": "Disposal",
        "rights": "How data subjects exercise their rights (art. 18)",
        "s6": "6. Identified risks",
        "current": "Current inventory assessment: likelihood {l}, impact {i}, score {s}.",
        "risk_table": "| Risk | Likelihood (1 to 5) | Impact (1 to 5) | Level |",
        "risk_examples": [
            "Unauthorized access",
            "Data leak or loss",
            "Use for a purpose other than the stated one",
            "Retention beyond what is needed",
        ],
        "s7": "7. Measures to address the risks",
        "existing": "Measures already recorded",
        "planned": "| Risk | Measure | Owner | Due date |",
        "s8": "8. Approval",
        "approval": "| Role | Name | Date | Opinion |",
        "roles": ["DPO", "Owner", "Controller representative"],
        "none": "none",
        "yes": "yes",
    },
}


def _list(items, none: str) -> str:
    return ", ".join(str(i) for i in items) if items else none


def render_ripd(op: dict, org: dict, lang: str = "pt", today: date | None = None) -> str:
    t = T[lang]
    todo = TODO[lang]
    today = today or date.today()
    controller = (org.get("controller") or {}).get("name") or todo
    dpo = org.get("dpo") or {}
    dpo_text = " · ".join(x for x in (dpo.get("name"), dpo.get("email")) if x) or todo

    lines = [
        f"# {t['title']}",
        "",
        f"**{t['operation']}:** {op['name']} (`{op['id']}`)",
        "",
        f"> {t['draft'].format(date=today.isoformat())}",
        "",
        f"## {t['s1']}",
        "",
        f"- **{t['controller']}:** {controller}",
        f"- **{t['dpo']}:** {dpo_text}",
        f"- **{t['owner']}:** {op.get('owner') or op['area']}",
        f"- **{t['processors']}:** " + _list([p["name"] for p in op.get("processors") or []], t["none"]),
        "",
        f"## {t['s2']}",
        "",
    ]
    reasons = dpia_reasons(op, lang)
    lines += [f"- {r}" for r in reasons] or [f"- {todo}"]

    sensitive = [SENSITIVE[c].label(lang) for c in op.get("sensitive_data") or [] if c in SENSITIVE]
    transfers = [
        f"{tr['country']} ({ART33[tr['mechanism']].reference})"
        if tr.get("mechanism") in ART33
        else tr["country"]
        for tr in op.get("international_transfers") or []
    ]
    lines += [
        "",
        f"## {t['s3']}",
        "",
        f"- **{t['purpose']}:** {op['purpose']}",
        f"- **{t['subjects']}:** {_list(op.get('data_subjects'), todo)}",
        f"- **{t['data']}:** {_list(op.get('personal_data'), todo)}",
        f"- **{t['sensitive']}:** {_list(sensitive, t['none'])}",
    ]
    if op.get("children_data"):
        lines.append(f"- **{t['children']}:** {t['yes']}")
    lines += [
        f"- **{t['systems']}:** {_list(op.get('systems'), todo)}",
        f"- **{t['sharing']}:** " + _list([s["recipient"] for s in op.get("sharing") or []], t["none"]),
        f"- **{t['transfers']}:** {_list(transfers, t['none'])}",
        f"- **{t['flow']}:** {todo}",
        "",
        f"## {t['s4']}",
        "",
        f"- {todo}",
        "",
        f"## {t['s5']}",
        "",
    ]
    p7 = ART7.get(op.get("legal_basis", ""))
    if p7:
        lines.append(f"- **{t['basis']}:** {p7.label(lang)} ({p7.reference})")
    p11 = ART11.get(op.get("sensitive_legal_basis", ""))
    if p11:
        lines.append(f"- **{t['sbasis']}:** {p11.label(lang)} ({p11.reference})")
    if op.get("legal_basis") == "legitimate_interest":
        lia = op.get("lia") or {}
        lia_text = " · ".join(
            str(x) for x in (lia.get("reference"), lia.get("date"), lia.get("outcome")) if x
        )
        lines.append(f"- **{t['lia']}:** {lia_text or todo}")
    retention = op.get("retention") or {}
    lines += [
        f"- **{t['minimization']}:** {todo}",
        f"- **{t['retention']}:** {retention.get('period') or todo}"
        + (f" ({retention['justification']})" if retention.get("justification") else ""),
        f"- **{t['disposal']}:** {retention.get('disposal') or todo}",
        f"- **{t['rights']}:** {todo}",
        "",
        f"## {t['s6']}",
        "",
    ]
    score = risk_score(op)
    if score is not None:
        risk = op["risk"]
        lines += [t["current"].format(l=risk["likelihood"], i=risk["impact"], s=score), ""]
    lines += [t["risk_table"], "| --- | --- | --- | --- |"]
    lines += [f"| {r} | {todo} | {todo} | {todo} |" for r in t["risk_examples"]]
    lines += ["", f"## {t['s7']}", "", f"**{t['existing']}:**", ""]
    lines += [f"- {m}" for m in op.get("security_measures") or []] or [f"- {todo}"]
    lines += ["", t["planned"], "| --- | --- | --- | --- |", f"| {todo} | {todo} | {todo} | {todo} |"]
    lines += ["", f"## {t['s8']}", "", t["approval"], "| --- | --- | --- | --- |"]
    lines += [f"| {role} |  |  |  |" for role in t["roles"]]
    return "\n".join(lines) + "\n"
