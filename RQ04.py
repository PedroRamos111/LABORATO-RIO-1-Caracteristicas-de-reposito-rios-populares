import requests
from datetime import datetime
import csv

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = ""  # Substitua pelo seu token

headers = {"Authorization": f"Bearer {TOKEN}"}

# Função para executar a consulta GraphQL
def run_query(query, variables={}):
    request = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")

# Consulta GraphQL para coletar dados dos repositórios, incluindo a data da última atualização
query = """
query ($after: String) {
  search(query: "stars:>1", type: REPOSITORY, first: 10, after: $after) {
    repositoryCount
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          name
          stargazers {
            totalCount
          }
          updatedAt
        }
      }
    }
  }
}
"""

# Variável para paginação
variables = {"after": None}
resultados = []
total_repos = 0
max_repos = 1000

# Coletar dados de até 1000 repositórios
while total_repos < max_repos:
    result = run_query(query, variables)
    data = result['data']['search']
    resultados.extend(data['edges'])
    total_repos += len(data['edges'])
    if not data['pageInfo']['hasNextPage'] or total_repos >= max_repos:
        break
    variables['after'] = data['pageInfo']['endCursor']

# Limitar ao número exato de repositórios necessários
resultados = resultados[:max_repos]

tempos_atualizacao = []
with open('DadosRQ04.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Tempo Desde a Ultima Atualizacao"])

    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        data_ultima_atualizacao = datetime.strptime(repo_data['updatedAt'], '%Y-%m-%dT%H:%M:%SZ')
        tempo_atualizacao_segundos = (datetime.utcnow() - data_ultima_atualizacao).total_seconds()
        tempo_atualizacao_horas = tempo_atualizacao_segundos / 3600  # Converter segundos para horas
        tempos_atualizacao.append(tempo_atualizacao_horas)
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], f"{tempo_atualizacao_horas:.2f}"])

# Calcular a média do tempo desde a última atualização em horas
media_tempo_atualizacao_horas = sum(tempos_atualizacao) / len(tempos_atualizacao)
print(f"Média do Tempo desde a Última Atualização: {media_tempo_atualizacao_horas:.2f} horas")