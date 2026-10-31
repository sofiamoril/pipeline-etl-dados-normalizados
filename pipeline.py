import sqlite3
import datetime
import requests

# 1. Configuração de Conexão com o Banco SQL (SQLite local)
DB_NAME = "dados_mercado.db"


def inicializar_banco():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Criando Tabelas Normalizadas (1FN, 2FN, 3FN)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS criptomoedas (
            id_cripto INTEGER PRIMARY KEY AUTOINCREMENT,
            simbolo TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotacoes (
            id_cotacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cripto INTEGER NOT NULL,
            preco_usd REAL NOT NULL,
            volume_24h REAL,
            data_hora DATETIME NOT NULL,
            FOREIGN KEY (id_cripto) REFERENCES criptomoedas (id_cripto)
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS metricas_mercado (
            id_metrica INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cripto INTEGER NOT NULL,
            variacao_24h_pct REAL,
            capitalizacao_mercado REAL,
            FOREIGN KEY (id_cripto) REFERENCES criptomoedas (id_cripto)
        )
    """)

  conn.commit()
  conn.close()


# 2. Ingestão de Dados via API REST
def extrair_dados_api():
  url = "https://api.coingecko.com/api/v3/coins/markets"
  params = {
      "vs_currency": "usd",
      "ids": "bitcoin,ethereum,solana,cardano",
      "order": "market_cap_desc",
      "per_page": 10,
      "page": 1,
      "sparkline": "false",
  }
  response = requests.get(url, params=params)
  if response.status_code == 200:
    return response.json()
  else:
    print(f"Erro na requisição: {response.status_code}")
    return []


# 3. Tratamento, Normalização e Carga no Banco
def carregar_dados(dados):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  for item in dados:
    simbolo = item["symbol"].upper()
    nome = item["name"]
    preco = item["current_price"]
    volume = item["total_volume"]
    variacao = item["price_change_percentage_24h"]
    market_cap = item["market_cap"]

    # Inserir ou obter Criptomoeda (Tabela Dimensão)
    cursor.execute(
        """
            INSERT OR IGNORE INTO criptomoedas (simbolo, nome) 
            VALUES (?, ?)
        """,
        (simbolo, nome),
    )

    cursor.execute(
        "SELECT id_cripto FROM criptomoedas WHERE simbolo = ?", (simbolo,)
    )
    id_cripto = cursor.fetchone()[0]

    # Inserir Cotação Fato
    cursor.execute(
        """
            INSERT INTO cotacoes (id_cripto, preco_usd, volume_24h, data_hora)
            VALUES (?, ?, ?, ?)
        """,
        (id_cripto, preco, volume, data_atual),
    )

    # Inserir Métricas de Mercado
    cursor.execute(
        """
            INSERT INTO metricas_mercado (id_cripto, variacao_24h_pct, capitalizacao_mercado)
            VALUES (?, ?, ?)
        """,
        (id_cripto, variacao, market_cap),
    )

  conn.commit()
  conn.close()
  print(" Pipeline executado com sucesso! Dados armazenados no SQL.")


if __name__ == "__main__":
  inicializar_banco()
  dados_brutos = extrair_dados_api()
  if dados_brutos:
    carregar_dados(dados_brutos)