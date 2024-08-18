import requests

# Configurações da API
GITHUB_API_URL = "https://api.github.com/graphql"
TOKEN = "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"

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

# Variável para paginação
variables = {"after": None}
resultados = []
total_repos = 0
max_repos = 100

# Coletar dados de até 100 repositórios
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

# Processar os dados para calcular a idade dos repositórios e imprimir as informações
pull_requests = []
for index, repo in enumerate(resultados, start=1):
    repo_data = repo['node']
    pr_aceitas = repo_data['pullRequests']['totalCount']
    pull_requests.append(pr_aceitas)
    print(f"{index}: Repositório: {repo_data['name']}, Estrelas: {repo_data['stargazers']['totalCount']}, Pull Requests Aceitas: {pr_aceitas}")

# Calcular a média de pull requests aceitas
media_pr_aceitas = sum(pull_requests) / len(pull_requests)
print(f"Média de Pull Requests Aceitas: {media_pr_aceitas:.2f}")
