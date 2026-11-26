"""Catalog of the LGPD provisions the kit understands.

Every code used in the YAML files maps to the article and item of Lei 13.709/2018 (LGPD) it
comes from, plus a short label in Portuguese and English. Where there is a direct counterpart in
the GDPR it is listed too, only as a reading aid.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Provision:
    code: str
    reference: str
    pt: str
    en: str
    gdpr: str = ""

    def label(self, lang: str) -> str:
        return self.pt if lang == "pt" else self.en


# Art. 7: legal bases for processing personal data.
ART7 = {
    p.code: p
    for p in (
        Provision("consent", "art. 7, I", "Consentimento", "Consent", "art. 6(1)(a)"),
        Provision(
            "legal_obligation",
            "art. 7, II",
            "Cumprimento de obrigação legal ou regulatória",
            "Legal or regulatory obligation",
            "art. 6(1)(c)",
        ),
        Provision(
            "public_policy",
            "art. 7, III",
            "Execução de políticas públicas",
            "Public policy (public administration)",
            "art. 6(1)(e)",
        ),
        Provision("research", "art. 7, IV", "Estudos por órgão de pesquisa", "Research body"),
        Provision(
            "contract",
            "art. 7, V",
            "Execução de contrato ou procedimentos preliminares",
            "Performance of a contract",
            "art. 6(1)(b)",
        ),
        Provision(
            "legal_proceedings",
            "art. 7, VI",
            "Exercício regular de direitos em processo",
            "Exercise of rights in legal proceedings",
        ),
        Provision(
            "protection_of_life",
            "art. 7, VII",
            "Proteção da vida ou da incolumidade física",
            "Protection of life or physical safety",
            "art. 6(1)(d)",
        ),
        Provision(
            "health_protection",
            "art. 7, VIII",
            "Tutela da saúde",
            "Health protection by health professionals",
        ),
        Provision(
            "legitimate_interest",
            "art. 7, IX",
            "Legítimo interesse",
            "Legitimate interest",
            "art. 6(1)(f)",
        ),
        Provision("credit_protection", "art. 7, X", "Proteção do crédito", "Credit protection"),
    )
}

# Art. 11: legal bases for sensitive personal data. Contract, legitimate interest and credit
# protection are deliberately absent: the LGPD does not accept them for sensitive data.
ART11 = {
    p.code: p
    for p in (
        Provision(
            "consent",
            "art. 11, I",
            "Consentimento específico e destacado",
            "Specific and highlighted consent",
            "art. 9(2)(a)",
        ),
        Provision(
            "legal_obligation",
            "art. 11, II, a",
            "Cumprimento de obrigação legal ou regulatória",
            "Legal or regulatory obligation",
            "art. 9(2)(b)",
        ),
        Provision(
            "public_policy",
            "art. 11, II, b",
            "Execução de políticas públicas",
            "Public policy (public administration)",
            "art. 9(2)(g)",
        ),
        Provision(
            "research",
            "art. 11, II, c",
            "Estudos por órgão de pesquisa",
            "Research body",
            "art. 9(2)(j)",
        ),
        Provision(
            "legal_proceedings",
            "art. 11, II, d",
            "Exercício regular de direitos, inclusive em contrato",
            "Exercise of rights, including in contracts",
            "art. 9(2)(f)",
        ),
        Provision(
            "protection_of_life",
            "art. 11, II, e",
            "Proteção da vida ou da incolumidade física",
            "Protection of life or physical safety",
            "art. 9(2)(c)",
        ),
        Provision(
            "health_protection",
            "art. 11, II, f",
            "Tutela da saúde",
            "Health protection by health professionals",
            "art. 9(2)(h)",
        ),
        Provision(
            "fraud_prevention",
            "art. 11, II, g",
            "Prevenção à fraude e segurança do titular",
            "Fraud prevention and data subject security",
        ),
    )
}

# Art. 5, II: categories of sensitive personal data.
SENSITIVE = {
    p.code: p
    for p in (
        Provision("racial_ethnic_origin", "art. 5, II", "Origem racial ou étnica", "Racial or ethnic origin"),
        Provision("religious_belief", "art. 5, II", "Convicção religiosa", "Religious belief"),
        Provision("political_opinion", "art. 5, II", "Opinião política", "Political opinion"),
        Provision(
            "organization_membership",
            "art. 5, II",
            "Filiação a sindicato ou organização religiosa, filosófica ou política",
            "Trade union or religious, philosophical or political membership",
        ),
        Provision("health", "art. 5, II", "Saúde", "Health"),
        Provision("sex_life", "art. 5, II", "Vida sexual", "Sex life"),
        Provision("genetic", "art. 5, II", "Dado genético", "Genetic data"),
        Provision("biometric", "art. 5, II", "Dado biométrico", "Biometric data"),
    )
}

# Art. 33: mechanisms that allow an international transfer.
ART33 = {
    p.code: p
    for p in (
        Provision(
            "adequacy",
            "art. 33, I",
            "País com nível de proteção adequado",
            "Country with an adequate level of protection",
            "art. 45",
        ),
        Provision(
            "specific_clauses",
            "art. 33, II, a",
            "Cláusulas contratuais específicas",
            "Specific contractual clauses",
            "art. 46(3)(a)",
        ),
        Provision(
            "standard_clauses",
            "art. 33, II, b",
            "Cláusulas-padrão contratuais",
            "Standard contractual clauses",
            "art. 46(2)(c)",
        ),
        Provision(
            "binding_corporate_rules",
            "art. 33, II, c",
            "Normas corporativas globais",
            "Binding corporate rules",
            "art. 47",
        ),
        Provision(
            "certification",
            "art. 33, II, d",
            "Selos, certificados e códigos de conduta",
            "Seals, certifications and codes of conduct",
            "art. 46(2)(e)",
        ),
        Provision(
            "international_cooperation",
            "art. 33, III",
            "Cooperação jurídica internacional",
            "International legal cooperation",
        ),
        Provision(
            "protection_of_life",
            "art. 33, IV",
            "Proteção da vida do titular ou de terceiro",
            "Protection of life",
            "art. 49(1)(f)",
        ),
        Provision(
            "anpd_authorization",
            "art. 33, V",
            "Autorização da ANPD",
            "Authorization by the ANPD",
        ),
        Provision(
            "international_commitment",
            "art. 33, VI",
            "Compromisso assumido em acordo de cooperação internacional",
            "International cooperation agreement",
        ),
        Provision(
            "public_policy",
            "art. 33, VII",
            "Execução de política pública",
            "Public policy",
        ),
        Provision(
            "specific_consent",
            "art. 33, VIII",
            "Consentimento específico e em destaque",
            "Specific and highlighted consent",
            "art. 49(1)(a)",
        ),
        Provision(
            "legal_basis_art7",
            "art. 33, IX",
            "Hipóteses do art. 7, II, V e VI",
            "Art. 7, II, V and VI bases",
            "art. 49(1)(b)",
        ),
    )
}


def gdpr_hint(code: str) -> str:
    provision = ART7.get(code)
    return provision.gdpr if provision and provision.gdpr else "n/a"
