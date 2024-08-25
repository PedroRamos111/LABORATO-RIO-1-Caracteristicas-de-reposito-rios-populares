import requests
from datetime import datetime
import csv
import numpy as np
from scipy import stats

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = ""

headers = {"Authorization": f"Bearer {TOKEN}"}

# Função para executar a consulta GraphQL
def run_query(query, variables={}):
    request = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")

# Consulta GraphQL para coletar dados dos repositórios
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
          createdAt
          stargazers {
            totalCount
          }
        }
      }
    }
  }
}
"""

# Função para calcular a idade do repositório
def calcular_idade(data_criacao):
    data_criacao = datetime.strptime(data_criacao, '%Y-%m-%dT%H:%M:%SZ')
    data_atual = datetime.utcnow()
    idade_anos = (data_atual - data_criacao).days / 365.25  
    return idade_anos

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

resultados = resultados[:max_repos]

# Processar os dados para calcular a idade dos repositórios e salvar as informações em um arquivo CSV
idades = []
with open('DadosRQ01.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Idade (anos)"])

    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        idade = calcular_idade(repo_data["createdAt"])
        idades.append(idade)
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], f"{idade:.2f}"])

media = np.mean(idades)

# Calcular a mediana
mediana = np.median(idades)

# Calcular a moda
moda = stats.mode(idades, keepdims=True)

with open('DadosRQ01.csv', mode='a', newline='') as arquivo_csv:  
    writer = csv.writer(arquivo_csv)
    writer.writerow([])
    writer.writerow(["Média", "Mediana", "Moda", "Ocorrências"])
    writer.writerow([media, mediana, moda.mode[0], moda.count[0]])