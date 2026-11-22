# Power BI — VisionMap

Painel de Business Intelligence (BI) do projeto **VisionMap**, que apresenta o ecossistema industrial e de serviços de São José dos Campos a partir dos microdados de estabelecimentos da RAIS.

**Versão final:** [`Sprint3/SPRINT 3 - FINAL.pbix`](Sprint3/SPRINT%203%20-%20FINAL.pbix)

---

## Como abrir o painel

1. Clique no arquivo `SPRINT 3 - FINAL.pbix`, dentro da pasta `Sprint3`.
2. Clique no botão de download (**Download raw file**) para baixar o arquivo.
3. Abra o arquivo no **Power BI Desktop**, que é gratuito e está disponível para Windows no site da Microsoft ou na Microsoft Store.

Os dados já estão carregados dentro do arquivo, então o painel abre pronto para consulta, sem nenhuma configuração adicional. O visual de mapa precisa de conexão com a internet para exibir o fundo do mapa.

---

## Páginas do painel

| Página | O que apresenta | User Stories |
|---|---|---|
| **Visão Geral** | Cartões com estabelecimentos, vínculos ativos, estabelecimentos com vínculos e média de vínculos; rosca de vínculos por porte; barras de vínculos e estabelecimentos por setor | US 5, US 6 e US 9 |
| **Setores e Atividades** | Mapa de árvore por cadeia produtiva e atividade; 10 maiores atividades; matriz por setor, atividade e seção CNAE | US 5, US 6, US 7 e US 10 |
| **Mapa da Economia** | Mapa com bolhas por setor, dimensionadas pelos vínculos; 15 bairros com mais vínculos | US 6 e US 8 |
| **Emprego e Porte** | Estabelecimentos por faixa de vínculos, compostos por setor econômico | US 5 e US 6 |

Todas as páginas contam com filtros por porte, setor, atividade, bairro e existência de vínculos.

---

## Principais números

| Indicador | Valor |
|---|---|
| Estabelecimentos | 47.339 |
| Vínculos ativos | 206.717 |
| Estabelecimentos com ao menos um vínculo | 15.058 |
| Média de vínculos por estabelecimento empregador | 13,73 |

---

## Fonte dos dados

O painel é alimentado pela base tratada disponível na pasta [`Base-de-Dados-SJC`](../Base-de-Dados-SJC), gerada pelo código da pasta [`Codigo-Python`](../Codigo-Python) a partir dos microdados da **RAIS Estabelecimentos** (Ministério do Trabalho e Emprego). A base foi reorganizada em um modelo estrela, com uma tabela fato e cinco tabelas de dimensão.

---

## Documentação

O passo a passo completo de construção do painel (preparação da pasta de trabalho, Power Query, modelagem, medidas DAX, páginas e validação) está no [Relatório Final](../VisionMap-Docs/VisionMap_Relatorio_Final.pdf).

---

## Histórico

A pasta `Sprint 2` guarda a primeira versão do painel, entregue na segunda sprint, mantida apenas como registro do desenvolvimento do projeto.
