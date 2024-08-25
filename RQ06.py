import numpy as np
import requests
from datetime import datetime
import csv

from scipy import stats

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = "" 

headers = {"Authorization": f"Bearer {TOKEN}"}


def run_query(query, variables={}):
    request = requests.post(GITHUB_API_URL, json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}. {query}")


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
          issues(states: [OPEN, CLOSED]) {
            totalCount
          }
          closedIssues: issues(states: CLOSED) {
            totalCount
          }
        }
      }
    }
  }
}
"""

variables = {"after": None}
resultados = []
total_repos = 0
max_repos = 1000

while total_repos < max_repos:
    result = run_query(query, variables)
    data = result['data']['search']
    resultados.extend(data['edges'])
    total_repos += len(data['edges'])
    if not data['pageInfo']['hasNextPage'] or total_repos >= max_repos:
        break
    variables['after'] = data['pageInfo']['endCursor']


resultados = resultados[:max_repos]


razoes_fechamento = []
with open('DadosRQ06.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Razão Fechamento Issues:"])
    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        total_issues = repo_data['issues']['totalCount']
        closed_issues = repo_data['closedIssues']['totalCount']
        if total_issues > 0:
            razao_fechamento = closed_issues / total_issues
        else:
            razao_fechamento = 0 
        razoes_fechamento.append(razao_fechamento)
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], f"{razao_fechamento:.2%}"])

media = np.mean(razoes_fechamento)

# Calcular a mediana
mediana = np.median(razoes_fechamento)

# Calcular a moda
moda = stats.mode(razoes_fechamento, keepdims=True)

with open('DadosRQ06.csv', mode='a', newline='') as arquivo_csv:  
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Média", "Mediana", "Moda/Ocorrências"])
    writer.writerow([media, mediana, moda.mode[0] + "/" + moda.count[0]])