# lgpd-ropa-kit

[![CI](https://github.com/gavicoding/lgpd-ropa-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/gavicoding/lgpd-ropa-kit/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20a%203.13-blue)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-green)](LICENSE)

[English](README.md) | Português

Mantenha o Registro das Operações de Tratamento (art. 37 da LGPD) em arquivos YAML num
repositório Git, valide contra um schema e contra as regras da lei, e gere um relatório HTML e
rascunhos de RIPD.

> **É uma ferramenta de apoio e não substitui orientação jurídica.** As regras abaixo pegam
> lacunas comuns; elas não dizem se um tratamento é lícito.

## O problema

Na maioria dos lugares o inventário fica numa planilha que ninguém confere:

- a linha diz "dados de saúde", mas a base legal é "execução de contrato", que a LGPD não aceita
  para dado sensível;
- "legítimo interesse" aparece em tudo, sem teste de balanceamento guardado;
- prazo de retenção em branco, operador sem cláusulas de proteção de dados, transferência para
  fora do país sem mecanismo;
- não há histórico de quem mudou o quê, e cada revisão começa do zero.

O `lgpd-ropa-kit` passa o inventário para YAML simples (um arquivo por operação). Assim ele
ganha revisão por pull request, histórico e comparação de versões, e é conferido a cada mudança.

## Instalação

Precisa do Python 3.10 ou mais novo.

```bash
pip install git+https://github.com/gavicoding/lgpd-ropa-kit.git
```

## Uso rápido

```bash
ropa-kit init minha-empresa                 # exemplo com 12 operações fictícias
ropa-kit validate minha-empresa             # schema + regras da LGPD, sai com 1 se houver erro
ropa-kit report minha-empresa -o ropa.html  # relatório HTML num arquivo só
ropa-kit ripd minha-empresa rh-ponto-biometrico -o ripd.md   # rascunho de RIPD
```

Mensagens e relatórios saem em português. Use `--lang en` para inglês.

### Estrutura da pasta

```text
minha-empresa/
  organization.yaml          controlador e encarregado (art. 41)
  operations/
    rh-folha-pagamento.yaml  uma operação de tratamento por arquivo
    mkt-newsletter.yaml
    ...
```

### Uma operação

```yaml
id: mkt-newsletter
name: Envio de newsletter
area: Marketing
owner: Coordenação de Marketing
purpose: Enviar novidades e ofertas para quem se inscreveu.
data_subjects: [assinantes]
personal_data: [nome, e-mail, preferências]
legal_basis: consent              # código do art. 7
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
    mechanism: standard_clauses   # código do art. 33
security_measures:
  - Link de descadastro em todo e-mail
risk:
  likelihood: 2                   # probabilidade, 1 a 5
  impact: 2                       # impacto, 1 a 5
```

As chaves ficam em inglês para o mesmo arquivo servir também para quem trabalha com GDPR. Cada
campo está explicado em [schema/README.md](schema/README.md), e o JSON Schema está em
[schema/ropa.schema.json](schema/ropa.schema.json) (o `ropa-kit schema` também mostra).

## Saída de exemplo

O `validate` no exemplo que vem junto, que tem algumas lacunas de propósito:

```text
$ ropa-kit validate examples/empresa-exemplo
operations/atd-chat-online.yaml: international_transfers[0].mechanism: erro R005: transferência internacional para US sem o mecanismo do art. 33
operations/mkt-perfil-de-consumo.yaml: lia: erro R002: legítimo interesse exige o registro do teste de balanceamento (LIA, art. 10), com data
operations/mkt-perfil-de-consumo.yaml: dpia: aviso R007: operação de alto risco (pontuação 12) sem RIPD concluído
operations/rh-ponto-biometrico.yaml: dpia: aviso R007: operação de alto risco (pontuação 12, dados sensíveis) sem RIPD concluído
operations/rh-recrutamento.yaml: processors[0]: aviso R006: operador 'Vagas Exemplo Tecnologia Ltda' sem cláusulas de proteção de dados (DPA)
operations/ti-cftv.yaml: retention.period: erro R004: prazo de retenção não informado (retention.period)
operations/ti-cftv.yaml: security_measures: aviso R008: nenhuma medida de segurança registrada (art. 46)

12 operações · 3 erro(s) · 4 aviso(s)
```

`--format json` mostra o mesmo em JSON, e `--strict` faz os avisos também falharem.

O relatório HTML dessa pasta está em [docs/sample-report.html](docs/sample-report.html) e um
rascunho de RIPD em [docs/sample-ripd.md](docs/sample-ripd.md). O relatório traz:

- números do inventário e índice por área;
- cada operação com os dados tratados, **dados sensíveis destacados**, base legal (com o
  artigo e o artigo mais próximo da GDPR) e prazo de retenção;
- operadores (contrato e DPA), compartilhamentos e transferências internacionais;
- matriz de risco 5 x 5 (probabilidade x impacto) das operações que pedem RIPD;
- a lista de pendências.

É um arquivo HTML só, sem scripts nem nada externo: abre sem internet, imprime bem e segue o
tema claro ou escuro do sistema.

## Regras

| Código | Nível | Regra | LGPD |
| --- | --- | --- | --- |
| S001 | erro | Schema: campo faltando, campo desconhecido, código inválido, tipo errado | |
| R001 | erro | Dado sensível precisa de base legal do art. 11 | art. 11 |
| R002 | erro | Legítimo interesse precisa de teste de balanceamento (LIA) com data | art. 7, IX e art. 10 |
| R003 | erro | O LIA reprovou o legítimo interesse, mas ele continua como base | art. 10 |
| R004 | erro | Prazo de retenção é obrigatório | arts. 15 e 16 |
| R005 | erro | Transferência internacional precisa de mecanismo | art. 33 |
| R006 | aviso | Operador sem contrato ou sem cláusulas de proteção de dados | art. 39 |
| R007 | aviso | Operação de alto risco sem RIPD concluído | art. 38 |
| R008 | aviso | Nenhuma medida de segurança registrada | art. 46 |
| R009 | erro | Duas operações com o mesmo `id` | |
| R010 | aviso | Contato do encarregado não informado | art. 41 |
| R011 | aviso | Base do art. 11 sem nenhum dado sensível listado | |
| R012 | aviso | Pasta sem operações | |

O schema só aceita códigos do art. 11 em `sensitive_legal_basis`. Então execução de contrato,
legítimo interesse e proteção do crédito não passam para dado sensível.

**Quando o RIPD é esperado?** Quando `probabilidade x impacto` dá 12 ou mais, ou quando a
operação trata dado sensível ou dado de criança ou adolescente. Use `risk.requires_dpia` com
`true` ou `false` para mudar essa decisão numa operação específica.

## Usando no CI

Guarde o inventário num repositório próprio e adicione um workflow:

```yaml
- run: pip install git+https://github.com/gavicoding/lgpd-ropa-kit.git
- run: ropa-kit validate inventario
- run: ropa-kit report inventario -o ropa.html
```

Um pull request que inclui operação sem retenção, ou com dado sensível na base errada, falha
antes de entrar.

## Limitações conhecidas

- As regras conferem estrutura e coerência. Não avaliam se a finalidade é legítima, se o dado é
  mesmo necessário ou se o teste de balanceamento está bem feito.
- O rascunho de RIPD segue as seções usuais; a análise em si precisa ser escrita por pessoas.
- Os critérios de RIPD (pontuação 12, dado sensível, dado de criança) são um ponto de partida,
  não a lista oficial da ANPD. Ajuste por operação com `risk.requires_dpia`.
- Texto livre (finalidade, prazo) não é interpretado: "5 anos" e "cinco anos" passam igual.

## Artigos da LGPD citados

Lei 13.709/2018: art. 5, II (dado sensível), art. 7 (bases legais), art. 10 (legítimo
interesse), art. 11 (bases para dado sensível), art. 14 (crianças e adolescentes), arts. 15 e
16 (término do tratamento), art. 33 (transferência internacional), art. 37 (registro das
operações), art. 38 (relatório de impacto), art. 39 (operador), art. 41 (encarregado), art. 46
(segurança).

## Desenvolvimento

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && pytest
```

A pasta de exemplo e o `docs/` são gerados pela própria ferramenta, e os testes falham se
ficarem desatualizados. Para gerar de novo depois de mudar o exemplo ou o relatório:

```bash
ropa-kit init examples/empresa-exemplo   # numa pasta vazia
ropa-kit report examples/empresa-exemplo -o docs/sample-report.html --date 2026-11-26
```

## Licença

[MIT](LICENSE). Empresas, pessoas e dados dos exemplos são todos fictícios.
