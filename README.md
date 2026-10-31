# pipeline-etl-dados-normalizados
# 📊 Pipeline ETL & Normalização de Dados de Mercado

Este projeto consiste em um pipeline de dados simples desenvolvido em Python que consome dados brutos de uma API REST, aplica conceitos de modelagem e normalização de banco de dados relacional (1FN a 3FN) e persiste as informações estruturadas em um banco SQLite.

## 🛠️ Tecnologias Utilizadas
- **Python 3** (requests, sqlite3, datetime)
- **SQLite** (Modelagem Relacional)
- **REST API** (CoinGecko API)

## 🗄️ Estrutura do Banco de Dados
O esquema foi modelado em tabelas separadas para evitar redundância:
- `criptomoedas`: Tabela dimensão com ID, símbolo e nome.
- `cotacoes`: Tabela fato com registros de preços e timestamps.
- `metricas_mercado`: Tabela auxiliar de indicadores de mercado.
