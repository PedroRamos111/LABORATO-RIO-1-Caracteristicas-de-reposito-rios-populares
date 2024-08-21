import requests
import csv

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
          pullRequests(states: MERGED) {
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

# Processar os dados para calcular a quantidade de pull requests dos repositórios e salvar as informações em um arquivo csv
pull_requests = []
with open('DadosRQ02.csv', mode='w', newline='') as arquivo_csv:
    writer = csv.writer(arquivo_csv)
    writer.writerow(["Nome do Repositório", "Estrelas", "Pull Requests Aceitas"])

    for index, repo in enumerate(resultados, start=1):
        repo_data = repo['node']
        pr_aceitas = repo_data['pullRequests']['totalCount']
        pull_requests.append(pr_aceitas)
        writer.writerow([repo_data['name'], repo_data['stargazers']['totalCount'], f"{pr_aceitas}"])

media_pr_aceitas = sum(pull_requests) / len(pull_requests)
print(f"Média de Pull Requests Aceitas: {media_pr_aceitas:.2f}")
