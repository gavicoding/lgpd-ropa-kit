"""Finding messages in Portuguese (default) and English."""

from __future__ import annotations

LANGS = ("pt", "en")

MESSAGES: dict[str, dict[str, str]] = {
    "Y001": {
        "pt": "o arquivo não é um YAML válido: {detail}",
        "en": "the file is not valid YAML: {detail}",
    },
    "Y002": {
        "pt": "o arquivo precisa conter um mapeamento (chave: valor) no nível de cima",
        "en": "the file must contain a mapping (key: value) at the top level",
    },
    "S001": {"pt": "{detail}", "en": "{detail}"},
    "R001": {
        "pt": "há dados sensíveis ({categories}), mas falta a base legal do art. 11 (sensitive_legal_basis)",
        "en": "sensitive data is processed ({categories}) but there is no art. 11 legal basis "
        "(sensitive_legal_basis)",
    },
    "R002": {
        "pt": "legítimo interesse exige o registro do teste de balanceamento (LIA, art. 10), com data",
        "en": "legitimate interest requires a recorded balancing test (LIA, art. 10) with a date",
    },
    "R003": {
        "pt": "o teste de balanceamento (LIA) reprovou o legítimo interesse, mas a operação "
        "ainda usa essa base",
        "en": "the balancing test (LIA) rejected legitimate interest, but the operation still relies on it",
    },
    "R004": {
        "pt": "prazo de retenção não informado (retention.period)",
        "en": "retention period is missing (retention.period)",
    },
    "R005": {
        "pt": "transferência internacional para {country} sem o mecanismo do art. 33",
        "en": "international transfer to {country} without an art. 33 mechanism",
    },
    "R006": {
        "pt": "operador '{name}' sem {missing}",
        "en": "processor '{name}' has no {missing}",
    },
    "R007": {
        "pt": "operação de alto risco ({reason}) sem RIPD concluído",
        "en": "high-risk operation ({reason}) without a completed DPIA (RIPD)",
    },
    "R008": {
        "pt": "nenhuma medida de segurança registrada (art. 46)",
        "en": "no security measures recorded (art. 46)",
    },
    "R009": {
        "pt": "id '{id}' repetido; já usado em {other}",
        "en": "duplicate id '{id}', already used in {other}",
    },
    "R010": {
        "pt": "contato do encarregado (dpo.email ou dpo.channel) não informado (art. 41)",
        "en": "DPO contact (dpo.email or dpo.channel) is missing (art. 41)",
    },
    "R011": {
        "pt": "há base do art. 11, mas nenhuma categoria em sensitive_data",
        "en": "an art. 11 basis is set but sensitive_data lists no category",
    },
    "R012": {
        "pt": "nenhuma operação encontrada na pasta operations/",
        "en": "no operation found in the operations/ folder",
    },
}

WORDS = {
    "contract": {"pt": "contrato", "en": "a contract"},
    "dpa": {"pt": "cláusulas de proteção de dados (DPA)", "en": "data processing clauses (DPA)"},
    "and": {"pt": " e ", "en": " and "},
    "score": {"pt": "pontuação {score}", "en": "score {score}"},
    "sensitive": {"pt": "dados sensíveis", "en": "sensitive data"},
    "children": {"pt": "dados de crianças ou adolescentes", "en": "children's data"},
    "forced": {"pt": "marcada manualmente", "en": "flagged manually"},
    "required": {"pt": "campo obrigatório ausente: {name}", "en": "missing required field: {name}"},
    "unknown": {"pt": "campo desconhecido: {name}", "en": "unknown field: {name}"},
    "enum": {
        "pt": "valor '{value}' não permitido; use um destes: {options}",
        "en": "value '{value}' is not allowed; use one of: {options}",
    },
    "type": {"pt": "tipo errado: esperado {expected}", "en": "wrong type: expected {expected}"},
    "range": {"pt": "valor fora do intervalo de 1 a 5", "en": "value outside the 1 to 5 range"},
    "pattern": {"pt": "formato inválido: '{value}'", "en": "invalid format: '{value}'"},
    "empty": {"pt": "não pode ficar vazio", "en": "must not be empty"},
    "duplicate": {"pt": "itens repetidos na lista", "en": "duplicate items in the list"},
}


def msg(code: str, lang: str, **kwargs: object) -> str:
    return MESSAGES[code][lang].format(**kwargs)


def word(key: str, lang: str, **kwargs: object) -> str:
    return WORDS[key][lang].format(**kwargs)
