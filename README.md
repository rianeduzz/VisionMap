# VisionMap

### Mapeamento do Ecossistema Econômico de São José dos Campos

Projeto de Aprendizagem por Projetos Integrados (API), desenvolvido pelo curso de Logística da Fatec São José dos Campos — 2026-1.

**Cliente:** CADI e Secretaria de Desenvolvimento Econômico de São José dos Campos.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rianeduzz/VisionMap/blob/main/Codigo-Python/rais_sjc_colab.ipynb)

---

## Índice

- [Objetivo do Projeto](#objetivo-do-projeto)
- [Entregas Finais](#entregas-finais)
- [Como Usar](#como-usar)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Equipe](#equipe)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Product Backlog](#product-backlog)
- [Sprints](#sprints)
- [Fonte do Projeto](#fonte-do-projeto)

---

## Objetivo do Projeto

Desenvolver uma solução para análise e visualização do ecossistema econômico de São José dos Campos, organizando dados públicos sobre empresas, setores e atividades econômicas para apoiar as decisões da gestão pública.

A solução reúne **47.339 estabelecimentos** e **206.717 vínculos ativos** do município, a partir dos microdados da RAIS (Ministério do Trabalho e Emprego), e envolve:

- Tratamento e organização dos dados;
- Classificação das empresas por setor, atividade e cadeia produtiva;
- Criação de gráficos e indicadores;
- Aplicação de filtros;
- Visualização da localização das empresas;
- Desenvolvimento de painel de BI.

---

## Entregas Finais

| Entrega | Descrição | Acesso |
|---|---|---|
| **Painel Power BI** | Versão final do painel, com 4 páginas, filtros e mapa | [Abrir pasta](Power-BI) · [Baixar .pbix](Power-BI/Sprint3/SPRINT%203%20-%20FINAL.pbix) |
| **Base de dados** | Base tratada da RAIS filtrada para São José dos Campos | [Abrir pasta](Base-de-Dados-SJC) · [Baixar .xlsx](Base-de-Dados-SJC/base_rais_sjc.xlsx) |
| **Código Python** | Notebook que gera a base tratada a partir da RAIS | [Abrir pasta](Codigo-Python) · [Abrir no Colab](https://colab.research.google.com/github/rianeduzz/VisionMap/blob/main/Codigo-Python/rais_sjc_colab.ipynb) |
| **Relatório final** | Documentação completa e passo a passo para replicação | [Abrir PDF](VisionMap-Docs/VisionMap_Relatorio_Final.pdf) |
| **User Stories** | Histórias de usuário e organização das sprints | [Abrir PDF](VisionMap-Docs/VisionMap%20.pdf) |
| **Vídeo final** | Apresentação do projeto com toda a equipe | [Assistir](COLE_AQUI_O_LINK_DO_VIDEO) |
| **PACER** | Avaliação da equipe | *Em preenchimento* |

---

## Como Usar

**Consultar o painel**
1. Baixe o arquivo [`SPRINT 3 - FINAL.pbix`](Power-BI/Sprint3/SPRINT%203%20-%20FINAL.pbix).
2. Abra no **Power BI Desktop** (gratuito, para Windows). Os dados já estão carregados no arquivo.

**Consultar a base de dados**
1. Baixe o arquivo [`base_rais_sjc.xlsx`](Base-de-Dados-SJC/base_rais_sjc.xlsx).
2. Abra no Excel. A aba **Dicionario_Dados** descreve cada coluna.

**Atualizar a base com uma nova RAIS**
1. Clique no botão **Abrir no Colab**, no topo desta página.
2. Siga a célula **Como usar (passo a passo)** do notebook.

O passo a passo completo de construção da base e do painel está no [Relatório Final](VisionMap-Docs/VisionMap_Relatorio_Final.pdf).

---

## Estrutura do Repositório

```
VisionMap/
├── Base-de-Dados-SJC/     → base tratada (Excel) e descrição das abas e colunas
├── Codigo-Python/         → notebook do Google Colab e script Python
├── Power-BI/
│   ├── Sprint3/           → versão final do painel (.pbix)
│   └── Sprint 2/          → primeira versão do painel (histórico)
├── VisionMap-Docs/        → relatório final, user stories, relatórios e PACER
└── README.md
```

---

## Equipe

| Nome | Papel | LinkedIn | GitHub |
|---|---|---|---|
| Bruno Godoi de Lima | Scrum Master | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/bruno-godoi-logistica/) | [![GitHub](https://img.shields.io/badge/GitHub-Perfil-181717?logo=github&logoColor=white)](https://github.com/Brunogodoi11) |
| Maria Eduarda de Souza | Product Owner | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maria-eduarda-souza-8118b5451/) | [![GitHub](https://img.shields.io/badge/GitHub-Perfil-181717?logo=github&logoColor=white)](https://github.com/madueds2014-oss) |
| Marinho B. Oliveira | Desenvolvedor | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/marinho-batista-de-oliveira-8061493b8/) | [![GitHub](https://img.shields.io/badge/GitHub-Perfil-181717?logo=github&logoColor=white)](https://github.com/marinhobatista2015) |
| Rian Eduardo de Brito Prado | Desenvolvedor | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rian-eduardo-9287512b7/) | [![GitHub](https://img.shields.io/badge/GitHub-Perfil-181717?logo=github&logoColor=white)](https://github.com/rianeduzz) |

---

## Tecnologias Utilizadas

- Power BI (Power Query, DAX e Azure Maps)
- Microsoft Excel
- Python
- Google Colab
- GitHub

---

## Product Backlog

| Rank | Prioridade | User Story | Sprint |
|---|---|---|---|
| 1 | Alta | Como equipe da Secretaria de Desenvolvimento Econômico, quero receber os dados públicos selecionados e filtrados para o município, para trabalhar com informações direcionadas à realidade local. | 1 |
| 2 | Alta | Como analista do CADI, quero limpar e padronizar a base de dados, para reduzir duplicidades, erros de preenchimento e inconsistências. | 1 |
| 3 | Alta | Como equipe responsável pelo projeto, quero classificar as empresas por setor e atividade econômica, para identificar o perfil produtivo do município. | 1 |
| 4 | Alta | Como Secretaria de Desenvolvimento Econômico, quero consultar uma base consolidada de empresas, atividades e setores, para utilizar esses dados nas análises municipais. | 1 |
| 5 | Alta | Como gestor público, quero visualizar os setores industriais e de serviços mais representativos, para reconhecer as principais atividades econômicas da cidade. | 2 |
| 6 | Alta | Como tomador de decisões, quero aplicar filtros por setor, atividade, contratação e período, para realizar consultas específicas no painel. | 2 |
| 7 | Alta | Como representante do CADI, quero visualizar a quantidade de empresas por segmento, para comparar indústria, tecnologia, logística e serviços especializados. | 2 |
| 8 | Alta | Como gestor público, quero consultar a localização das empresas por setor, para reconhecer as áreas com maior concentração de atividades econômicas. | 2 |
| 9 | Média | Como Secretária de Desenvolvimento Econômico, quero comparar os setores por empresas e oportunidades de trabalho, para apoiar o planejamento de ações públicas. | 3 |
| 10 | Média | Como analista do CADI, quero identificar as atividades produtivas predominantes, para compreender a composição econômica e produtiva do município. | 3 |
| 11 | Média | Como gestor público, quero analisar a conexão entre empresas, tecnologia e inovação, para avaliar sua contribuição ao desenvolvimento regional. | 3 |
| 12 | Média | Como equipe da Secretaria, quero visualizar os dados em gráficos, tabelas e mapas interativos, para interpretar os resultados com facilidade. | 3 |
| 13 | Média | Como estudante de logística, quero identificar processos de produção, armazenagem, transporte e distribuição, para relacioná-los às características da economia local. | 3 |
| 14 | Alta | Como responsável pelo projeto no CADI, quero disponibilizar a base tratada, os gráficos e a documentação, para permitir a consulta e a continuidade do trabalho pela Secretaria. | 3 |

---

## Sprints

### Sprint 1 — Preparação e filtragem dos dados

- Seleção das fontes públicas;
- Filtragem dos registros para São José dos Campos;
- Correção de inconsistências;
- Sinalização de possíveis duplicidades;
- Padronização dos campos;
- Classificação das empresas;
- Registro da origem dos dados.

**Entrega:** base de dados tratada, organizada e pronta para alimentar o painel.

### Sprint 2 — Primeira versão do painel de BI

- Gráficos sobre a quantidade de empresas por setor;
- Indicadores de emprego;
- Filtros básicos;
- Representação da localização das empresas.

**Entrega:** primeira versão funcional do painel, capaz de apresentar os principais setores industriais e de serviços do município.

### Sprint 3 — Complementação e finalização

- Comparações entre setores;
- Análise das atividades produtivas;
- Melhorias visuais;
- Testes;
- Documentação final.

**Entrega:** painel de BI revisado e finalizado, acompanhado da base tratada, do código, do relatório final com o passo a passo para replicação, do vídeo de apresentação e do PACER da equipe. Os links de cada item estão em [Entregas Finais](#entregas-finais).

---

## Fonte do Projeto

Documento **Requisitos de Cliente 1 — LOG-CADI**, referente ao projeto de Aprendizagem por Projetos Integrados 2026-1.
