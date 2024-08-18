import requests
from datetime import datetime

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
max_repos = 100

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
for index, repo in enumerate(resultados, start=1):
    repo_data = repo['node']
    total_issues = repo_data['issues']['totalCount']
    closed_issues = repo_data['closedIssues']['totalCount']
    if total_issues > 0:
        razao_fechamento = closed_issues / total_issues
    else:
        razao_fechamento = 0 
    razoes_fechamento.append(razao_fechamento)
    print(f"{index}: Repositório: {repo_data['name']}, Estrelas: {repo_data['stargazers']['totalCount']}, Razão Fechamento Issues: {razao_fechamento:.2%}")


media_razao_fechamento = sum(razoes_fechamento) / len(razoes_fechamento)
print(f"Média da Razão de Fechamento de Issues: {media_razao_fechamento:.2%}")