# Inventory schema

[`ropa.schema.json`](ropa.schema.json) (JSON Schema 2020-12) has two definitions: `organization`
for `organization.yaml` and `operation` for each file in `operations/`. Unknown fields are
rejected, so a typo such as `legal_bassis` is caught. Dates are `YYYY-MM-DD`.

## organization.yaml

| Field | Required | Description |
| --- | --- | --- |
| `controller.name` | yes | Legal name of the controller |
| `controller.cnpj` | | Company registration number |
| `controller.address` | | Address |
| `dpo.name`, `dpo.email`, `dpo.channel` | email or channel expected (R010) | DPO identity and public contact (art. 41) |
| `reviewed_at` | | Date of the last full review |

## operations/*.yaml

| Field | Required | Description |
| --- | --- | --- |
| `id` | yes | Stable identifier: lowercase letters, digits and hyphens |
| `name` | yes | Short name of the operation |
| `area` | yes | Business area, used to group the report |
| `owner` | | Team or role accountable |
| `purpose` | yes | Why the data is processed |
| `data_subjects` | | List of data subject groups |
| `personal_data` | yes, at least one | List of data items |
| `sensitive_data` | | Codes from the table below (art. 5, II) |
| `children_data` | | `true` if it processes data of children or adolescents (art. 14) |
| `legal_basis` | yes | Art. 7 code |
| `sensitive_legal_basis` | when `sensitive_data` is set (R001) | Art. 11 code |
| `lia.date`, `lia.reference`, `lia.outcome` | date when the basis is legitimate interest (R002) | Balancing test; outcome is `approved`, `approved_with_measures` or `rejected` |
| `retention.period` | yes (R004) | How long the data is kept |
| `retention.justification` | | Why that period |
| `retention.disposal` | | How it is deleted or anonymized |
| `systems` | | Systems involved |
| `processors[]` | | `name` (required), `service`, `country`, `contract` and `dpa` (booleans, R006) |
| `sharing[]` | | `recipient` (required), `purpose` |
| `international_transfers[]` | | `country` (required), `recipient`, `mechanism` (art. 33 code, R005) |
| `security_measures` | expected (R008) | List of measures |
| `risk.likelihood`, `risk.impact` | both, when `risk` is present | Integers from 1 to 5 |
| `risk.requires_dpia` | | Overrides the automatic DPIA decision |
| `dpia.status` | when `dpia` is present | `not_started`, `in_progress` or `done` |
| `dpia.reference`, `dpia.date` | | Where the DPIA is and when it was approved |
| `notes` | | Free text |

## Codes

### Art. 7: `legal_basis`

| Code | LGPD | Meaning |
| --- | --- | --- |
| `consent` | art. 7, I | Consent |
| `legal_obligation` | art. 7, II | Legal or regulatory obligation |
| `public_policy` | art. 7, III | Public policy (public administration) |
| `research` | art. 7, IV | Research body |
| `contract` | art. 7, V | Performance of a contract |
| `legal_proceedings` | art. 7, VI | Exercise of rights in proceedings |
| `protection_of_life` | art. 7, VII | Protection of life or physical safety |
| `health_protection` | art. 7, VIII | Health protection |
| `legitimate_interest` | art. 7, IX | Legitimate interest |
| `credit_protection` | art. 7, X | Credit protection |

### Art. 11: `sensitive_legal_basis`

| Code | LGPD |
| --- | --- |
| `consent` | art. 11, I |
| `legal_obligation` | art. 11, II, a |
| `public_policy` | art. 11, II, b |
| `research` | art. 11, II, c |
| `legal_proceedings` | art. 11, II, d |
| `protection_of_life` | art. 11, II, e |
| `health_protection` | art. 11, II, f |
| `fraud_prevention` | art. 11, II, g |

### Art. 5, II: `sensitive_data`

`racial_ethnic_origin`, `religious_belief`, `political_opinion`, `organization_membership`,
`health`, `sex_life`, `genetic`, `biometric`.

### Art. 33: `international_transfers[].mechanism`

| Code | LGPD |
| --- | --- |
| `adequacy` | art. 33, I |
| `specific_clauses` | art. 33, II, a |
| `standard_clauses` | art. 33, II, b |
| `binding_corporate_rules` | art. 33, II, c |
| `certification` | art. 33, II, d |
| `international_cooperation` | art. 33, III |
| `protection_of_life` | art. 33, IV |
| `anpd_authorization` | art. 33, V |
| `international_commitment` | art. 33, VI |
| `public_policy` | art. 33, VII |
| `specific_consent` | art. 33, VIII |
| `legal_basis_art7` | art. 33, IX |

The packaged copy at `src/ropa_kit/ropa.schema.json` is the one the tool loads; a test makes sure
both files stay identical.
