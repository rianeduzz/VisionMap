# Base de Dados — Empresas de São José dos Campos

Base tratada com **todos os estabelecimentos de São José dos Campos registrados na RAIS** (Relação Anual de Informações Sociais, do Ministério do Trabalho e Emprego). É a base que alimenta o [painel Power BI](../Power-BI) do projeto VisionMap.

**Arquivo:** [`base_rais_sjc.xlsx`](base_rais_sjc.xlsx). Para baixar, clique no arquivo e depois no botão de download (**Download raw file**).

---

## Números da base

| Indicador | Valor |
|---|---|
| Estabelecimentos | 47.339 |
| Vínculos ativos (empregos formais em 31/12) | 206.717 |
| Colunas por estabelecimento | 44 |
| Linhas lidas da RAIS (Brasil todo) | 12.643.067 |

---

## Abas do arquivo

| Aba | Conteúdo |
|---|---|
| **Base_Tratada** | Base completa: um estabelecimento por linha, com 44 colunas |
| **Resumo** | Estabelecimentos, vínculos e percentual por setor, subsetor IBGE, cadeia produtiva, porte, faixa de tamanho, natureza jurídica, atividade no ano e Simples Nacional |
| **Log_Qualidade** | Cada verificação e correção aplicada, com a quantidade de registros afetados |
| **Dicionario_Dados** | Descrição, percentual de preenchimento e exemplo de cada coluna |
| **Fontes** | Origem dos dados, endereços e data de extração |
| **Sprint** | Backlog da Sprint 1 (preparação dos dados) |

---

## Como a base foi construída

A base foi gerada pelo notebook da pasta [`Codigo-Python`](../Codigo-Python), que pode ser executado novamente no Google Colab para atualizar os dados.

| Etapa | O que foi feito | Registros |
|---|---|---|
| Leitura | Leitura do arquivo RAIS de estabelecimentos do Brasil | 12.643.067 |
| Filtro | Seleção dos estabelecimentos de São José dos Campos (código IBGE 3549904) | 47.339 |
| Seleção | Remoção de colunas que só existem para outras cidades (bairros de SP, RJ, Fortaleza e DF) | 5 colunas |
| Padronização | Códigos de “não classificado” convertidos para vazio; CEP, CNAE e natureza jurídica em formato padrão | — |
| Endereço | CEPs inválidos ou fora da faixa de SJC convertidos para vazio | 2 |
| CNAE | Subclasses que não existem na tabela oficial do IBGE (sinalizadas) | 16 |
| Duplicidade | Linhas idênticas a outra (sinalizadas, não removidas) | 4.977 |
| Classificação | Setor econômico, seção CNAE, subsetor IBGE, cadeia produtiva de SJC e porte SEBRAE | 47.339 |
| Origem | Fonte, arquivo, linha de origem e data de tratamento registrados em cada linha | 47.339 |

As descrições oficiais das atividades vêm da API de CNAE 2.0 do IBGE.

---

## Principais colunas

| Grupo | Colunas |
|---|---|
| Identificação | `id_registro`, `municipio`, `uf`, `cod_municipio_ibge`, `cep` |
| Atividade econômica | `cnae_subclasse`, `cnae_classe`, `cnae_divisao`, `cnae_secao` (com descrições) |
| Classificação | `setor_economico`, `ibge_subsetor`, `cadeia_produtiva_sjc`, `porte_sebrae`, `tamanho_estab_faixa` |
| Emprego | `qtd_vinculos_ativos`, `qtd_vinculos_clt`, `qtd_vinculos_estatutarios` |
| Perfil | `natureza_juridica`, `natureza_juridica_grupo`, `tipo_estab`, `optante_simples`, `status_atividade` |
| Qualidade | `qualidade_registro_pct` e colunas `flag_...` (CEP ausente, CNAE inexistente, vínculos inconsistentes, possível duplicata etc.) |
| Origem | `fonte_dados`, `url_fonte`, `arquivo_origem`, `linha_origem`, `data_tratamento` |

A descrição de todas as 44 colunas está na aba **Dicionario_Dados**.

---

## Panorama por setor econômico

| Setor | Estabelecimentos | Vínculos ativos |
|---|---:|---:|
| Serviços | 29.830 | 108.496 |
| Comércio | 11.826 | 46.228 |
| Indústria | 2.088 | 39.387 |
| Construção | 3.297 | 11.870 |
| Agropecuária | 295 | 624 |
| Administração Pública | 3 | 112 |

A coluna `cadeia_produtiva_sjc` destaca as cadeias relevantes para o município, como Aeroespacial e Defesa, Automotiva, Tecnologia da Informação, Logística, Pesquisa e Engenharia, Saúde e Educação.

---

## Cuidados ao usar a base

- **Sem CNPJ:** a RAIS pública não identifica as empresas. Por isso, cada linha recebe um código próprio (`id_registro`), e linhas idênticas podem ser estabelecimentos diferentes.
- **Possíveis duplicidades:** 4.977 linhas estão marcadas em `flag_possivel_duplicata` e foram mantidas na base. Para excluí-las de uma análise, filtre essa coluna por “Não”.
- **Ano-base:** o ano de referência da RAIS não foi informado no tratamento (`ano_base_rais` = “Não informado”). Ao atualizar a base, preencha o `ANO_BASE` no notebook.
- **Estabelecimentos sem empregados:** 32.281 estabelecimentos têm zero vínculos ativos. A coluna `qtd_vinculos_ativos` permite separar os estabelecimentos empregadores.

---

## Fontes

- **RAIS Estabelecimentos** — Ministério do Trabalho e Emprego: <https://pdet.mte.gov.br/microdados-rais-e-caged>
- **API de CNAE 2.0** — IBGE: <https://servicodados.ibge.gov.br/api/v2/cnae/subclasses>
- **Classificação CNAE 2.0** — IBGE/CONCLA: <https://concla.ibge.gov.br/busca-online-cnae.html>
- **Porte por número de empregados** — critério SEBRAE

O processo completo está documentado no [Relatório Final](../VisionMap-Docs/VisionMap_Relatorio_Final.pdf).
