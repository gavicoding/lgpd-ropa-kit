# lgpd-ropa-kit

[![CI](https://github.com/gavicoding/lgpd-ropa-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/gavicoding/lgpd-ropa-kit/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20to%203.13-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

English | [Português](README.pt-BR.md)

Keep the LGPD Record of Processing Activities (RoPA, art. 37) as YAML files in a Git repository,
validate it against a schema and the rules of the law, and turn it into a clean HTML report and
DPIA (RIPD) drafts.

> **This is a support tool. It does not replace legal advice.** The rules below catch common
> gaps; they do not decide whether a processing operation is lawful.

## The problem

Most DPOs and IT teams keep the processing inventory in a spreadsheet that nobody validates:

- a row says "health data" but the legal basis is "contract", which the LGPD does not accept for
  sensitive data;
- "legitimate interest" is everywhere, with no balancing test on file;
- retention periods are blank, processors have no data processing clauses, transfers abroad
  have no mechanism;
- there is no history of who changed what, and every review starts from scratch.

`lgpd-ropa-kit` moves the inventory to plain YAML (one file per operation), so it gets code
review, history and diffs for free, and checks it every time it changes.

## Install

Requires Python 3.10 or newer.

```bash
pip install git+https://github.com/gavicoding/lgpd-ropa-kit.git
```

## Quick start

```bash
ropa-kit init minha-empresa                 # example with 12 fictional operations
ropa-kit validate minha-empresa             # schema + LGPD rules, exit 1 on errors
ropa-kit report minha-empresa -o ropa.html  # self-contained HTML report
ropa-kit ripd minha-empresa rh-ponto-biometrico -o ripd.md   # DPIA draft
```

Messages and reports are in Portuguese by default. Add `--lang en` for English.

### Folder layout

```text
minha-empresa/
  organization.yaml          controller and DPO (art. 41)
  operations/
    rh-folha-pagamento.yaml  one processing operation per file
    mkt-newsletter.yaml
    ...
```

### One operation

```yaml
id: mkt-newsletter
name: Envio de newsletter
area: Marketing
owner: Coordenação de Marketing
purpose: Enviar novidades e ofertas para quem se inscreveu.
data_subjects: [assinantes]
personal_data: [nome, e-mail, preferências]
legal_basis: consent              # art. 7 code
retention:
  period: Até o titular cancelar a inscrição
  disposal: Exclusão da lista em até 10 dias
processors:
  - name: Mail Exemplo Inc.
    country: US
    contract: true
    dpa: true
international_transfers:
  - country: US
    mechanism: standard_clauses   # art. 33 code
security_measures:
  - Link de descadastro em todo e-mail
risk:
  likelihood: 2                   # 1 to 5
  impact: 2                       # 1 to 5
```

Every field is described in [schema/README.md](schema/README.md), and the JSON Schema itself is
in [schema/ropa.schema.json](schema/ropa.schema.json) (also printed by `ropa-kit schema`).

## Example output

Running `validate` on the bundled example, which has some gaps on purpose:

```text
$ ropa-kit validate examples/empresa-exemplo --lang en
operations/atd-chat-online.yaml: international_transfers[0].mechanism: error R005: international transfer to US without an art. 33 mechanism
operations/mkt-perfil-de-consumo.yaml: lia: error R002: legitimate interest requires a recorded balancing test (LIA, art. 10) with a date
operations/mkt-perfil-de-consumo.yaml: dpia: warning R007: high-risk operation (score 12) without a completed DPIA (RIPD)
operations/rh-ponto-biometrico.yaml: dpia: warning R007: high-risk operation (score 12, sensitive data) without a completed DPIA (RIPD)
operations/rh-recrutamento.yaml: processors[0]: warning R006: processor 'Vagas Exemplo Tecnologia Ltda' has no data processing clauses (DPA)
operations/ti-cftv.yaml: retention.period: error R004: retention period is missing (retention.period)
operations/ti-cftv.yaml: security_measures: warning R008: no security measures recorded (art. 46)

12 operations · 3 error(s) · 4 warning(s)
```

`--format json` prints the same findings as JSON, and `--strict` also fails on warnings.

The HTML report generated from the same folder is in
[docs/sample-report.html](docs/sample-report.html) and a DPIA draft in
[docs/sample-ripd.md](docs/sample-ripd.md). The report has:

- summary cards and an index by area;
- every operation with its data, **sensitive data highlighted**, legal basis (with the article
  and the closest GDPR article) and retention;
- processors (contract and DPA), sharing and international transfers;
- a 5 x 5 risk matrix (likelihood x impact) of the operations that need a DPIA;
- the list of open issues.

It is a single HTML file with no scripts or external assets: it opens offline, prints well and
follows the system light or dark theme.

## Rules

| Code | Level | Rule | LGPD |
| --- | --- | --- | --- |
| S001 | error | Schema: missing field, unknown field, invalid code, wrong type | |
| R001 | error | Sensitive data needs a legal basis from art. 11 | art. 11 |
| R002 | error | Legitimate interest needs a dated balancing test (LIA) | art. 7, IX and art. 10 |
| R003 | error | The LIA rejected legitimate interest but it is still the basis | art. 10 |
| R004 | error | Retention period is mandatory | art. 15 and 16 |
| R005 | error | International transfer needs a mechanism | art. 33 |
| R006 | warning | Processor without a contract or data processing clauses | art. 39 |
| R007 | warning | High-risk operation without a completed DPIA | art. 38 |
| R008 | warning | No security measures recorded | art. 46 |
| R009 | error | Two operations with the same `id` | |
| R010 | warning | DPO contact missing | art. 41 |
| R011 | warning | Art. 11 basis set but no sensitive data listed | |
| R012 | warning | No operations in the folder | |

The schema only accepts art. 11 codes for `sensitive_legal_basis`, so contract, legitimate
interest and credit protection cannot be used for sensitive data.

**When is a DPIA expected?** When `likelihood x impact` is 12 or more, or the operation
processes sensitive data or children's data. Set `risk.requires_dpia` to `true` or `false` to
override that decision for a specific operation.

## Using it in CI

Keep the inventory in its own repository and add a workflow:

```yaml
- run: pip install git+https://github.com/gavicoding/lgpd-ropa-kit.git
- run: ropa-kit validate inventario
- run: ropa-kit report inventario -o ropa.html
```

A pull request that adds an operation without retention or with sensitive data on the wrong
basis then fails before it is merged.

## Known limitations

- The rules check structure and consistency. They do not judge whether a purpose is legitimate,
  whether the data is really necessary or whether a balancing test is sound.
- The DPIA draft follows the usual RIPD sections; the analysis itself has to be written by people.
- The DPIA criteria (score 12, sensitive data, children's data) are a starting point, not the
  ANPD's official list. Adjust per operation with `risk.requires_dpia`.
- Free text (purpose, retention period) is not interpreted, so "5 anos" and "five years" are
  both accepted.

## LGPD articles referenced

Lei 13.709/2018: art. 5, II (sensitive data), art. 7 (legal bases), art. 10 (legitimate
interest), art. 11 (sensitive data bases), art. 14 (children), art. 15 and 16 (end of
processing), art. 33 (international transfer), art. 37 (record of operations), art. 38 (DPIA),
art. 39 (processor), art. 41 (DPO), art. 46 (security).

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && pytest
```

The example folder and `docs/` are generated by the tool itself; tests fail if they drift. To
regenerate after changing the sample or the report:

```bash
ropa-kit init examples/empresa-exemplo   # on an empty folder
ropa-kit report examples/empresa-exemplo -o docs/sample-report.html --date 2026-11-26
```

## License

[MIT](LICENSE). All companies, people and data in the examples are fictional.
